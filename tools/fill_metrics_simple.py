#!/usr/bin/env python3
from pathlib import Path
import re
import subprocess

BASE_DIR = Path(__file__).resolve().parent.parent
TABLE_FILE = BASE_DIR / "results" / "comparison_tables" / "solver_vs_baseline.md"
TARGETS = [
    BASE_DIR / "LINKEDIN_POST.txt",
    BASE_DIR / "PROJECT_SUMMARY.md",
    BASE_DIR / "README.md"
]

def find_column_index(header, keyword):
    for i, h in enumerate(header):
        if keyword.lower() in h.lower():
            return i
    raise ValueError(f"No column containing '{keyword}' found in: {header}")

def get_repo_url():
    try:
        url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"], text=True).strip()
        if url.startswith("git@github.com:"):
            url = "https://github.com/" + url.split("git@github.com:")[1]
        return url.rstrip(".git")
    except:
        return None

def main():
    lines = TABLE_FILE.read_text().splitlines()

    # Find first table header line
    for idx, line in enumerate(lines):
        if line.strip().startswith("|"):
            header_line_index = idx
            break
    else:
        raise ValueError("No markdown table header line found.")

    header = [h.strip() for h in lines[header_line_index].strip("|").split("|")]
    runtime_idx = find_column_index(header, "runtime")
    objective_idx = find_column_index(header, "objective")

    # Find first row with numeric runtime
    solver_runtime = None
    solver_accuracy = None
    for line in lines[header_line_index + 2:]:
        if "|" not in line:
            continue
        row = [c.strip() for c in line.strip("|").split("|")]
        try:
            rt_val = float(row[runtime_idx])
        except ValueError:
            continue
        solver_runtime = rt_val
        solver_accuracy = row[objective_idx]
        break

    if solver_runtime is None:
        raise ValueError("No valid numeric runtime found in table.")

    baseline_runtime = "—"
    baseline_accuracy = "—"

    repo_url = get_repo_url()

    for file in TARGETS:
        if not file.exists():
            continue
        text = file.read_text()
        text = re.sub(r"Runtime:.*", f"• Runtime: Solver = {solver_runtime} s vs Baseline = {baseline_runtime}", text)
        text = re.sub(r"Accuracy:.*", f"• Accuracy: Solver = {solver_accuracy} vs Baseline = {baseline_accuracy}", text)
        if repo_url:
            text = re.sub(r"https://github\\.com/\\s*your-username\\s*/\\s*your-repo", repo_url, text)
        file.write_text(text)
        print(f"Updated {file.name}")

    print("\n✅ Done.\nNext run:\n  git add LINKEDIN_POST.txt PROJECT_SUMMARY.md README.md\n  git commit -m 'Fill metrics from table'\n  git push origin main")

if __name__ == "__main__":
    main()

