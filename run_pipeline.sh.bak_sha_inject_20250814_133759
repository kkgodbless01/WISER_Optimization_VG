#!/bin/bash
set -euo pipefail

# Always operate from repo root
cd "$(dirname "$0")"
ROOT="$(pwd)"

echo "=== Step 0: Environment bootstrap ==="
# --- Step 0: Init colors and log file ---
if [ "${WISER_NO_COLOR:-0}" = "1" ]; then
  c_reset=""; c_green=""; c_yellow=""; c_red=""; c_cyan=""
else
  c_reset=$(tput sgr0 2>/dev/null || echo "")
  c_green=$(tput setaf 2 2>/dev/null || echo "")
  c_yellow=$(tput setaf 3 2>/dev/null || echo "")
  c_red=$(tput setaf 1 2>/dev/null || echo "")
  c_cyan=$(tput setaf 6 2>/dev/null || echo "")
fi
c_reset=$(tput sgr0 2>/dev/null || echo "")
c_green=$(tput setaf 2 2>/dev/null || echo "")
c_yellow=$(tput setaf 3 2>/dev/null || echo "")
c_red=$(tput setaf 1 2>/dev/null || echo "")
c_cyan=$(tput setaf 6 2>/dev/null || echo "")
ts=$(date +%Y%m%d_%H%M%S)
log_file="pip_failures_${ts}.log"
: > "$log_file"

# --- Step 0: Auto-venv activation ---
if [ -d "venv" ] && [ -f "venv/bin/activate" ] && [ -z "${VIRTUAL_ENV:-}" ]; then
    echo "${c_cyan}⚡ Activating venv...${c_reset}"
    # shellcheck disable=SC1091
    . venv/bin/activate
fi

# --- Step 0: Guarded import scan (once per run) ---
if [ -n "${WISER_DEP_SCAN_DONE:-}" ]; then
    echo "${c_yellow}⏭️  Step 0 already ran; skipping duplicate scan.${c_reset}"
else
    export WISER_DEP_SCAN_DONE=1
    echo "${c_cyan}🔍 Scanning Python files for imports...${c_reset}"
    missing_pkgs=()
    builtin_skip=$(python - <<PY
import sys
print(" ".join(getattr(sys, "stdlib_module_names", set())))
PY
)
    while IFS= read -r mod; do
        if [[ " $builtin_skip " =~ " $mod " ]]; then continue; fi
        if [ -e "src/$mod.py" ] || [ -d "src/$mod" ] || [ -e "experiments/$mod.py" ] || [ -d "experiments/$mod" ]; then
            echo "${c_cyan}🔹 Skipping local module: $mod${c_reset}"; continue
        fi
        if ! python -c "import $mod" &>/dev/null; then missing_pkgs+=("$mod"); fi
    done < <(grep -hRE "^import |^from " src/ experiments/ 2>/dev/null | sed -E "s/^from ([^ ]+).*/\1/; s/^import (.*)/\1/" | tr "," "\n" | sed -E "s/\s+as\s+\w+//; s/^[ \t]*//; s/[ \t]*$//" | cut -d. -f1 | sort -u)
    if [ ${#missing_pkgs[@]} -gt 0 ]; then
        echo "${c_yellow}📦 Installing missing packages individually...${c_reset}"
        for pkg in "${missing_pkgs[@]}"; do
            if ! pip install "$pkg"; then
                echo "$(date +%F_%T) - $pkg" >> "$log_file"
                echo "${c_red}⚠️  Failed to install $pkg (logged)${c_reset}"
            fi
        done
    else
        echo "${c_green}✅ No extra imports missing${c_reset}"
    fi
    fail_count=$(wc -l < "$log_file" 2>/dev/null || echo 0)
    summary_line="📊 Step 0 Dependency Check: $fail_count packages failed to install"
    touch PROJECT_SUMMARY.md
 # --- Step 0: Record log mode in PROJECT_SUMMARY.md ---
 log_mode_line="Log Mode: $([ \"${WISER_NO_COLOR:-0}\" = \"1\" ] && echo Plain-Text || echo Color)"
 # Local time in Ghana, recruiter-friendly format: 14-Aug-2025 13:07
 env_summary_line="Env: $(TZ=Africa/Accra date +%d-%b-%Y\ %H:%M) | Git: $(git rev-parse --short HEAD 2>/dev/null || echo N/A) | Python: $(python3 --version 2>/dev/null | { read _ v _; echo $v; })"
 sed -i \"/^Log Mode:/d\" PROJECT_SUMMARY.md
 sed -i \"/^Env:/d\" PROJECT_SUMMARY.md
 sed -i \"1i$env_summary_line\" PROJECT_SUMMARY.md
 sed -i \"1i$log_mode_line\" PROJECT_SUMMARY.md

 # --- Step 0.1: Refresh Git SHA after auto-commit ---
 if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
   final_sha=$(git rev-parse --short HEAD)
   sed -i \"s/^Env: .*Git: [^|]*/Env: $(TZ=Africa/Accra date +%d-%b-%Y\ %H:%M) | Git: $final_sha/\" PROJECT_SUMMARY.md
 fi
 log_mode_line="Log Mode: $([ \"${WISER_NO_COLOR:-0}\" = \"1\" ] && echo Plain-Text || echo Color)"
 # Use local time in Africa/Accra
 env_summary_line="Env: $(TZ=Africa/Accra date +%F_%T) | Git: $(git rev-parse --short HEAD 2>/dev/null || echo N/A) | Python: $(python3 --version 2>/dev/null | awk \\"{print \\$2}\\")"
 sed -i \"/^Log Mode:/d\" PROJECT_SUMMARY.md
 sed -i \"/^Env:/d\" PROJECT_SUMMARY.md
 sed -i \"1i$env_summary_line\" PROJECT_SUMMARY.md
 sed -i \"1i$log_mode_line\" PROJECT_SUMMARY.md

 # --- Step 0.1: Refresh Git SHA after auto-commit ---
 if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
   final_sha=$(git rev-parse --short HEAD)
   sed -i \"s/^Env: .*Git: [^|]*/Env: $(TZ=Africa/Accra date +%F_%T) | Git: $final_sha/\" PROJECT_SUMMARY.md
 fi
 log_mode_line="Log Mode: $([ "${WISER_NO_COLOR:-0}" = "1" ] && echo Plain-Text || echo Color)"
 sed -i "/^Log Mode:/d" PROJECT_SUMMARY.md
 sed -i "1i$log_mode_line" PROJECT_SUMMARY.md
    sed -i "1i$summary_line" PROJECT_SUMMARY.md
    if [ -s "$log_file" ]; then
        echo "${c_yellow}📄 Recent failures:${c_reset}"
        tail -n 5 "$log_file"
    else
        echo "${c_green}📄 No failures logged${c_reset}"
    fi
fi
# --- Step 0: Init log file ---
ts=$(date +%Y%m%d_%H%M%S)
log_file="pip_failures_${ts}.log"
: > "$log_file"

# --- Step 0: Auto-venv activation ---
if [ -d "venv" ] && [ -f "venv/bin/activate" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "⚡ Activating venv..."
    source venv/bin/activate
fi

# --- Step 0: Catch‑all import tester ---
echo "🔍 Scanning Python files for imports..."
missing_pkgs=()
builtin_skip=$(python - <<PY
import sys
print(" ".join(getattr(sys, "stdlib_module_names", set())))
PY
)
while IFS= read -r mod; do
    if [[ " $builtin_skip " =~ " $mod " ]]; then continue; fi
    if [ -e "src/$mod.py" ] || [ -d "src/$mod" ] || [ -e "experiments/$mod.py" ] || [ -d "experiments/$mod" ]; then
        echo "🔹 Skipping local module: $mod"; continue
    fi
    if ! python -c "import $mod" &>/dev/null; then missing_pkgs+=("$mod"); fi
done < <(grep -hE "^import |^from " src/*.py src/**/*.py experiments/*.py experiments/**/*.py 2>/dev/null | sed -E "s/^from ([^ ]+).*/\1/; s/^import (.*)/\1/" | tr "," "\n" | sed -E "s/\s+as\s+\w+//; s/^[ \t]*//; s/[ \t]*$//" | cut -d. -f1 | sort -u)
if [ ${#missing_pkgs[@]} -gt 0 ]; then
    echo "📦 Installing missing packages individually..."
    for pkg in "${missing_pkgs[@]}"; do
        if ! pip install "$pkg"; then
            echo "$(date +%F_%T) - $pkg" >> "$log_file"
            echo "⚠️ Failed to install $pkg (logged)"
        fi
    done
else
    echo "✅ No extra imports missing"
fi
# --- Step 0: Summary for PROJECT_SUMMARY.md (top prepend) ---
fail_count=$(wc -l < "$log_file" 2>/dev/null || echo 0)
summary_line="📊 Step 0 Dependency Check: $fail_count packages failed to install"
sed -i "1i$summary_line" PROJECT_SUMMARY.md
if [ -s "$log_file" ]; then
    echo "📄 Recent failures:"
    tail -n 5 "$log_file"
else
    echo "📄 No failures logged"
fi
# --- Step 0: Auto-venv activation ---
if [ -d "venv" ] && [ -f "venv/bin/activate" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "⚡ Activating venv..."
    source venv/bin/activate
fi

# --- Step 0: Catch‑all import tester (built‑ins + locals skipped) ---
echo "🔍 Scanning Python files for imports..."
missing_pkgs=()
builtin_skip=$(python - <<PY
import sys
print(" ".join(getattr(sys, "stdlib_module_names", set())))
PY
)
while IFS= read -r mod; do
    if [[ " $builtin_skip " =~ " $mod " ]]; then continue; fi
    if [ -e "src/$mod.py" ] || [ -d "src/$mod" ] || [ -e "experiments/$mod.py" ] || [ -d "experiments/$mod" ]; then
        echo "🔹 Skipping local module: $mod"; continue
    fi
    if ! python -c "import $mod" &>/dev/null; then missing_pkgs+=("$mod"); fi
done < <(grep -hE "^import |^from " src/*.py src/**/*.py experiments/*.py experiments/**/*.py 2>/dev/null | sed -E "s/^from ([^ ]+).*/\1/; s/^import (.*)/\1/" | tr "," "\n" | sed -E "s/\s+as\s+\w+//; s/^[ \t]*//; s/[ \t]*$//" | cut -d. -f1 | sort -u)
if [ ${#missing_pkgs[@]} -gt 0 ]; then
    echo "📦 Installing missing packages individually..."
    for pkg in "${missing_pkgs[@]}"; do
        if ! pip install "$pkg"; then
            echo "$(date +%F_%T) - $pkg" >> pip_failures_20250814_115749.log
            echo "⚠️ Failed to install $pkg (logged)"
        fi
    done
else
    echo "✅ No extra imports missing"
fi
# --- Step 0: Summary for PROJECT_SUMMARY.md (top prepend) ---
fail_count=$(wc -l < "$log_file" 2>/dev/null || echo 0)
summary_line="📊 Step 0 Dependency Check: $fail_count packages failed to install"
sed -i "1i$summary_line" PROJECT_SUMMARY.md
# --- Step 0: Auto-venv activation ---
if [ -d "venv" ] && [ -f "venv/bin/activate" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "⚡ Activating venv..."
    source venv/bin/activate
fi

# --- Step 0: Catch‑all import tester (built‑ins + locals skipped) ---
echo "🔍 Scanning Python files for imports..."
missing_pkgs=()
builtin_skip=$(python - <<PY
import sys
print(" ".join(getattr(sys, "stdlib_module_names", set())))
PY
)
while IFS= read -r mod; do
    if [[ " $builtin_skip " =~ " $mod " ]]; then continue; fi
    if [ -e "src/$mod.py" ] || [ -d "src/$mod" ] || [ -e "experiments/$mod.py" ] || [ -d "experiments/$mod" ]; then
        echo "🔹 Skipping local module: $mod"; continue
    fi
    if ! python -c "import $mod" &>/dev/null; then missing_pkgs+=("$mod"); fi
done < <(grep -hE "^import |^from " src/*.py src/**/*.py experiments/*.py experiments/**/*.py 2>/dev/null | sed -E "s/^from ([^ ]+).*/\1/; s/^import (.*)/\1/" | tr "," "\n" | sed -E "s/\s+as\s+\w+//; s/^[ \t]*//; s/[ \t]*$//" | cut -d. -f1 | sort -u)
if [ ${#missing_pkgs[@]} -gt 0 ]; then
    echo "📦 Installing missing packages individually..."
    for pkg in "${missing_pkgs[@]}"; do
        if ! pip install "$pkg"; then
            echo "$(date +%F_%T) - $pkg" >> pip_failures_20250814_105531.log
            echo "⚠️ Failed to install $pkg (logged)"
        fi
    done
else
    echo "✅ No extra imports missing"
fi
# --- Step 0: Summary for PROJECT_SUMMARY.md ---
fail_count=$(wc -l < "$log_file" 2>/dev/null || echo 0)
echo "📊 Step 0 Dependency Check: $fail_count packages failed to install" | tee -a PROJECT_SUMMARY.md
# --- Step 0: Auto-venv activation ---
if [ -d "venv" ] && [ -f "venv/bin/activate" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "⚡ Activating venv..."
    source venv/bin/activate
fi

# --- Step 0: Catch‑all import tester (built‑ins + locals skipped) ---
echo "🔍 Scanning Python files for imports..."
missing_pkgs=()
builtin_skip=$(python - <<PY
import sys
print(" ".join(getattr(sys, "stdlib_module_names", set())))
PY
)
while IFS= read -r mod; do
    if [[ " $builtin_skip " =~ " $mod " ]]; then continue; fi
    if [ -e "src/$mod.py" ] || [ -d "src/$mod" ] || [ -e "experiments/$mod.py" ] || [ -d "experiments/$mod" ]; then
        echo "🔹 Skipping local module: $mod"; continue
    fi
    if ! python -c "import $mod" &>/dev/null; then missing_pkgs+=("$mod"); fi
done < <(grep -hE "^import |^from " src/*.py src/**/*.py experiments/*.py experiments/**/*.py 2>/dev/null | sed -E "s/^from ([^ ]+).*/\1/; s/^import (.*)/\1/" | tr "," "\n" | sed -E "s/\s+as\s+\w+//; s/^[ \t]*//; s/[ \t]*$//" | cut -d. -f1 | sort -u)
if [ ${#missing_pkgs[@]} -gt 0 ]; then
    echo "📦 Installing missing packages individually..."
    for pkg in "${missing_pkgs[@]}"; do
        if ! pip install "$pkg"; then
            echo "$(date +%F_%T) - $pkg" >> pip_failures_20250814_104209.log
            echo "⚠️ Failed to install $pkg (logged)"
        fi
    done
else
    echo "✅ No extra imports missing"
fi
# --- Step 0: Auto-venv activation ---
if [ -d "venv" ] && [ -f "venv/bin/activate" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "⚡ Activating venv..."
    source venv/bin/activate
fi

# --- Step 0: Catch‑all import tester (built‑ins + locals skipped) ---
echo "🔍 Scanning Python files for imports..."
missing_pkgs=()
builtin_skip=$(python - <<PY
import sys
print(" ".join(getattr(sys, "stdlib_module_names", set())))
PY
)
while IFS= read -r mod; do
    if [[ " $builtin_skip " =~ " $mod " ]]; then continue; fi
    if [ -e "src/$mod.py" ] || [ -d "src/$mod" ] || [ -e "experiments/$mod.py" ] || [ -d "experiments/$mod" ]; then
        echo "🔹 Skipping local module: $mod"; continue
    fi
    if ! python -c "import $mod" &>/dev/null; then missing_pkgs+=("$mod"); fi
done < <(grep -hE "^import |^from " src/*.py src/**/*.py experiments/*.py experiments/**/*.py 2>/dev/null | sed -E "s/^from ([^ ]+).*/\1/; s/^import (.*)/\1/" | tr "," "\n" | sed -E "s/\s+as\s+\w+//; s/^[ \t]*//; s/[ \t]*$//" | cut -d. -f1 | sort -u)
if [ ${#missing_pkgs[@]} -gt 0 ]; then
    echo "📦 Installing missing packages individually..."
    for pkg in "${missing_pkgs[@]}"; do
        if ! pip install "$pkg"; then
            echo "$(date +%F_%T) - $pkg" >> pip_failures_20250814_104012.log
            echo "⚠️ Failed to install $pkg (logged)"
        fi
    done
else
    echo "✅ No extra imports missing"
fi
# --- Step 0: Auto-venv activation ---
if [ -d "venv" ] && [ -f "venv/bin/activate" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "⚡ Activating venv..."
    source venv/bin/activate
fi

# --- Step 0: Catch‑all import tester (built‑ins + locals skipped) ---
echo "🔍 Scanning Python files for imports..."
missing_pkgs=()

# Build full stdlib skip list dynamically from this Python's stdlib
builtin_skip="$(python - <<'PY'
import sys
print(" ".join(getattr(sys, 'stdlib_module_names', set())))
PY
)"

# Gather imports from src/ and experiments/
while IFS= read -r mod; do
    # Skip stdlib modules
    if [[ " $builtin_skip " =~ " $mod " ]]; then
        continue
    fi
    # Skip if local module/package exists in repo
    if [ -e "src/$mod.py" ] || [ -d "src/$mod" ] || \
       [ -e "experiments/$mod.py" ] || [ -d "experiments/$mod" ]; then
        echo "🔹 Skipping local module: $mod"
        continue
    fi
    # Check if import works, else add to missing list
    if ! python -c "import $mod" &>/dev/null; then
        missing_pkgs+=("$mod")
    fi
done < <(
    grep -hE '^import |^from ' src/*.py src/**/*.py experiments/*.py experiments/**/*.py 2>/dev/null \
    | sed -E 's/^from ([^ ]+).*/\1/; s/^import (.*)/\1/' \
    | tr ',' '\n' \
    | sed -E 's/\s+as\s+\w+//; s/^[ \t]*//; s/[ \t]*$//' \
    | cut -d. -f1 | sort -u
)

# Install any real missing packages
if [ ${#missing_pkgs[@]} -gt 0 ]; then
    echo "📦 Installing missing packages: ${missing_pkgs[*]}"
    pip install "${missing_pkgs[@]}" || echo "⚠️ Some packages could not be installed"
else
    echo "✅ No extra imports missing"
fi

# --- Auto-commit hook start ---
# Toggle with: export WISER_AUTOCOMMIT=1 (default) or =0 to disable
if [ "${WISER_AUTOCOMMIT:-1}" = "1" ]; then
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if ! git diff --quiet || ! git diff --cached --quiet; then
      echo "${c_cyan}🔃 Auto-committing run artifacts...${c_reset}"
      git add run_pipeline.sh PROJECT_SUMMARY.md
      git commit -m "chore: update Step 0 dep check + summary [auto]" || true
      git push || true
      echo "${c_green}✅ Auto-commit complete${c_reset}"
    else
      echo "${c_yellow}ℹ️  No git changes to commit${c_reset}"
    fi
  else
    echo "${c_yellow}ℹ️  Git repo not detected; skipping auto-commit${c_reset}"
  fi
fi
# --- Auto-commit hook end ---



## AUTO-REFRESH-RUNTIMES
{
  SUMMARY="PROJECT_SUMMARY.md"
  REPO_URL="https://github.com/kkgodbless01/WISER_Optimization_VG"

  # Step 0 runtime
  if grep -q "^Runtime:" "$SUMMARY"; then
    STEP0_RUNTIME=$(grep "^Runtime:" "$SUMMARY" | head -n1 | awk '{print $2}')
  else
    STEP0_RUNTIME="N/A"
  fi

  # Step 1 runtime
  if [ -f outputs/step_1/metrics.json ]; then
    STEP1_RUNTIME=$(python3 - <<'PY'
import json
m=json.load(open("outputs/step_1/metrics.json"))
print(m.get("runtime_s", "N/A"))
PY
)
  else
    STEP1_RUNTIME="N/A"
  fi

  # Capture separate SHAs if possible
  if [ -f .step0_sha ]; then
    STEP0_SHA=$(cat .step0_sha)
  else
    STEP0_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo N/A)
  fi
  if [ -f .step1_sha ]; then
    STEP1_SHA=$(cat .step1_sha)
  else
    STEP1_SHA=$STEP0_SHA
  fi

  STEP0_SHA_LINK="${REPO_URL}/commit/${STEP0_SHA}"
  STEP1_SHA_LINK="${REPO_URL}/commit/${STEP1_SHA}"

  # Remove old table
  if [ -f "$SUMMARY" ]; then
    awk 'BEGIN{skip=0}
         /<!-- RUNTIMES-TABLE-START -->/{skip=1; next}
         /<!-- RUNTIMES-TABLE-END -->/{skip=0; next}
         {if (!skip) print}' "$SUMMARY" > "${SUMMARY}.tmp"
    mv "${SUMMARY}.tmp" "$SUMMARY"
  else
    touch "$SUMMARY"
  fi

  # Prepend new table with separate clickable SHAs
  TMPFILE=$(mktemp)
  {
    echo "<!-- RUNTIMES-TABLE-START -->"
    echo ""
    echo "| Step   | Runtime (s) | Git |"
    echo "|--------|-------------|-----|"
    echo "| Step 0 | ${STEP0_RUNTIME} | [${STEP0_SHA}](${STEP0_SHA_LINK}) |"
    echo "| Step 1 | ${STEP1_RUNTIME} | [${STEP1_SHA}](${STEP1_SHA_LINK}) |"
    echo ""
    echo "<!-- RUNTIMES-TABLE-END -->"
    echo ""
    cat "$SUMMARY"
  } > "$TMPFILE"
  mv "$TMPFILE" "$SUMMARY"

  # Cleanup temp SHA files
  rm -f .step0_sha .step1_sha
}
