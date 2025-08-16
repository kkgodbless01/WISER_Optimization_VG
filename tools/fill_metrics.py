#!/usr/bin/env python3
import re
import sys
import subprocess
from pathlib import Path

# -----------------------------
# Settings
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # repo root
TABLE_PATH = BASE_DIR / "results" / "comparison_tables" / "solver_vs_baseline.md"
TARGET_FILES = [
    BASE_DIR / "LINKEDIN_POST.txt",
    BASE_DIR / "PROJECT_SUMMARY.md",
    BASE_DIR / "README.md",
]

# Keywords
RUNTIME_KEYS = ["runtime", "time", "latency", "duration"]
ACCURACY_KEYS = ["accuracy", "acc"]
SOLVER_KEYS = ["solver", "proposed", "ours", "variant"]
BASELINE_KEYS = ["baseline", "reference", "default", "naive"]

# -----------------------------
# Helpers
# -----------------------------
def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip()).lower()

def contains_any(text: str, keys) -> bool:
    t = norm(text)
    return any(k in t for k in keys)

def ensure_runtime_unit(v: str) -> str:
    t = v.strip()
    if re.search(r"(ms|s)\b", t, re.IGNORECASE):
        return t
    # if it's plain number, default to seconds
    return f"{t} s"

def ensure_percent(v: str) -> str:
    t = v.strip()
    if "%" in t:
        return t
    return f"{t} %"

def parse_md_table(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines()]
    # find first header + separator pair
    header_idx = None
    for i in range(len(lines) - 1):
        if "|" in lines[i] and re.search(r"\|\s*:?-{3,}\s*\|", lines[i + 1]):
            header_idx = i
            break
    if header_idx is None:
        raise ValueError("Could not find a Markdown table with a separator line (---).")

    header_line = lines[header_idx]
    sep_line = lines[header_idx + 1]

    def split_row(row):
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        return cells

    header = split_row(header_line)
    rows = []
    for j in range(header_idx + 2, len(lines)):
        if "|" not in lines[j]:
            break
        row_cells = split_row(lines[j])
        # skip empty row lines
        if len([c for c in row_cells if c]) == 0:
            continue
        rows.append(row_cells)

    return header, rows

def find_first_table(path: Path):
    header, rows = parse_md_table(path)
    # normalize row lengths to header length
    cols = len(header)
    rows = [r + [""] * (cols - len(r)) if len(r) < cols else r[:cols] for r in rows]
    return header, rows

def find_metrics(header, rows):
    """
    Try two orientations:

    A) Metric rows:
       header ~= [Metric | Solver | Baseline]
       rows like: [Average Runtime (s) | 12.3 | 45.6]
       -> we match row by metric name and take solver/baseline columns.

    B) Metric columns:
       header has runtime/accuracy columns
       rows ~= [Solver | ...runtime... | ...accuracy...]
       -> we match rows by solver/baseline names and take metric columns.
    """
    hnorm = [norm(h) for h in header]
    cols = len(header)

    # Orientation A: "Metric" as a column and solver/baseline as columns
    metric_col = None
    if any("metric" in h for h in hnorm):
        metric_col = hnorm.index(next(h for h in hnorm if "metric" in h))
    # Identify solver and baseline column indices by header keywords
    solver_col = None
    baseline_col = None
    for i, h in enumerate(hnorm):
        if solver_col is None and contains_any(h, SOLVER_KEYS):
            solver_col = i
        if baseline_col is None and contains_any(h, BASELINE_KEYS):
            baseline_col = i

    # Try orientation A if we have metric_col and solver/baseline columns
    if metric_col is not None and solver_col is not None and baseline_col is not None:
        runtime_val_solver = runtime_val_base = None
        acc_val_solver = acc_val_base = None
        for r in rows:
            metric_name = r[metric_col]
            if contains_any(metric_name, RUNTIME_KEYS):
                runtime_val_solver = r[solver_col]
                runtime_val_base = r[baseline_col]
            if contains_any(metric_name, ACCURACY_KEYS):
                acc_val_solver = r[solver_col]
                acc_val_base = r[baseline_col]
        if all([runtime_val_solver, runtime_val_base, acc_val_solver, acc_val_base]):
            return {
                "solver_runtime": runtime_val_solver,
                "baseline_runtime": runtime_val_base,
                "solver_accuracy": acc_val_solver,
                "baseline_accuracy": acc_val_base,
            }

    # Orientation B: Solver/Baseline as rows, metrics as columns
    # Find runtime and accuracy columns by header keywords
    runtime_col = None
    acc_col = None
    for i, h in enumerate(hnorm):
        if runtime_col is None and contains_any(h, RUNTIME_KEYS):
            runtime_col = i
        if acc_col is None and contains_any(h, ACCURACY_KEYS):
            acc_col = i
    # Find the "label" column for row names (solver vs baseline)
    label_col = 0  # usually first column
    if runtime_col is not None and acc_col is not None:
        solver_row = baseline_row = None
        for r in rows:
            label = r[label_col]
            if solver_row is None and contains_any(label, SOLVER_KEYS):
                solver_row = r
            if baseline_row is None and contains_any(label, BASELINE_KEYS):
                baseline_row = r
        if solver_row and baseline_row:
            return {
                "solver_runtime": solver_row[runtime_col],
                "baseline_runtime": baseline_row[runtime_col],
                "solver_accuracy": solver_row[acc_col],
                "baseline_accuracy": baseline_row[acc_col],
            }

    raise ValueError("Could not detect runtime/accuracy and solver/baseline from the table.")

def get_repo_https_url() -> str | None:
    try:
        url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=BASE_DIR,
            text=True
        ).strip()
    except Exception:
        return None

    if url.startswith("git@github.com:"):
        path = url.split("git@github.com:")[1]
    elif url.startswith("https://github.com/"):
        path = url.split("https://github.com/")[1]
    else:
        return None
    path = path.rstrip(".git").strip("/")
    return f"https://github.com/{path}"

def replace_runtime_accuracy_bullets(text, solver_rt, base_rt, solver_acc, base_acc):
    # Standardize values with units
    sr = ensure_runtime_unit(solver_rt)
    br = ensure_runtime_unit(base_rt)
    sa = ensure_percent(solver_acc)
    ba = ensure_percent(base_acc)

    # Replace any line that starts with "Runtime:" or contains "Runtime:"
    text = re.sub(
        r"^.*Runtime:.*$",
        f"• Runtime: Solver = {sr} vs Baseline = {br}",
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    text = re.sub(
        r"^.*Accuracy:.*$",
        f"• Accuracy: Solver = {sa} vs Baseline = {ba}",
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    return text

def replace_runtime_accuracy_rows(text, solver_rt, base_rt, solver_acc, base_acc):
    # Keep original metric labels on the left if present
    def repl_row(kind_keys, solver_val, base_val):
        pattern = re.compile(rf"^\|([^\n|]*?(?:{'|'.join(kind_keys)}).*?)\|.*$", re.IGNORECASE | re.MULTILINE)
        def _sub(m):
            left = m.group(1).strip()
            return f"| {left} | {solver_val} | {base_val} |"
        return pattern.sub(_sub, text)

    # Do not add units here; assume table already includes them in the header
    t = text
    t = repl_row([r"runtime", r"time", r"latency", r"duration"], solver_rt, base_rt)
    t = repl_row([r"accuracy", r"\bacc\b"], solver_acc, base_acc)
    return t

def fix_placeholder_links(text, repo_url):
    if not repo_url:
        return text
    owner_repo = "/".join(repo_url.rstrip("/").split("/")[-2:])
    # Replace explicit placeholders with spaces like "https://github.com/ your-username/your-repo"
    text = re.sub(r"https://github\.com/\s*your-username\s*/\s*your-repo", repo_url, text, flags=re.IGNORECASE)
    # Replace bare placeholders "your-username/your-repo"
    text = re.sub(r"\byour-username\s*/\s*your-repo\b", owner_repo, text, flags=re.IGNORECASE)
    return text

def main():
    if not TABLE_PATH.exists():
        print(f"ERROR: Table not found: {TABLE_PATH}")
        sys.exit(1)

    print(f"Reading table: {TABLE_PATH}")
    header, rows = find_first_table(TABLE_PATH)
    print("Header:", header)
    try:
        vals = find_metrics(header, rows)
    except Exception as e:
        print("ERROR: Could not extract metrics.")
        print(f"Reason: {e}")
        print("Tip: Ensure your table has 'Runtime' and 'Accuracy' columns or rows, and 'Solver' and 'Baseline' labels.")
        sys.exit(1)

    print("Found values:")
    print("  Solver runtime     =", vals['solver_runtime'])
    print("  Baseline runtime   =", vals['baseline_runtime'])
    print("  Solver accuracy    =", vals['solver_accuracy'])
    print("  Baseline accuracy  =", vals['baseline_accuracy'])

    repo_url = get_repo_https_url()
    if repo_url:
        print("Detected repository URL:", repo_url)
    else:
        print("Could not detect repository URL from git. Link placeholders will be left unchanged.")

    updated_any = False
    for fp in TARGET_FILES:
        if not fp.exists():
            print(f"(skip) Missing file: {fp.name}")
            continue
        original = fp.read_text(encoding="utf-8")

        # Apply replacements
        text = original
        text = replace_runtime_accuracy_bullets(
            text,
            vals['solver_runtime'],
            vals['baseline_runtime'],
            vals['solver_accuracy'],
            vals['baseline_accuracy'],
        )
        text = replace_runtime_accuracy_rows(
            text,
            vals['solver_runtime'],
            vals['baseline_runtime'],
            vals['solver_accuracy'],
            vals['baseline_accuracy'],
        )
        text = fix_placeholder_links(text, repo_url)

        if text != original:
            fp.write_text(text, encoding="utf-8")
            updated_any = True
            print(f"Updated: {fp.name}")
        else:
            print(f"No changes needed: {fp.name}")

    if not updated_any:
        print("No files were changed. If you still see 'None' or placeholders, check your table and file formats.")
        sys.exit(0)

    print("✅ All files updated successfully.")
    print("Next: review with 'git diff', then commit and push.")

if __name__ == "__main__":
    main()

