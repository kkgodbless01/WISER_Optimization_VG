#!/usr/bin/env bash
set -euo pipefail
REPO_URL="https://github.com/kkgodbless01/WISER_Optimization_VG"

# Colors
if [ "${WISER_NO_COLOR:-0}" = "1" ]; then
  c_ok=""; c_info=""; c_warn=""; c_err=""; c_reset=""
else
  c_ok="$(tput setaf 2 2>/dev/null || true)"
  c_info="$(tput setaf 6 2>/dev/null || true)"
  c_warn="$(tput setaf 3 2>/dev/null || true)"
  c_err="$(tput setaf 1 2>/dev/null || true)"
  c_reset="$(tput sgr0 2>/dev/null || true)"
fi

echo "=== Step 1: Static solver ==="
python3 -m step_1.runner --input "data/problem.json" --outdir "outputs/step_1" --debug || {
  echo "${c_err}Step 1 failed${c_reset}"; exit 1;
}

# Extract metrics with Python
read BESTCOST RUNTIME SHA PYVER <<EOF
$(python3 - <<'PY'
import json
m=json.load(open("outputs/step_1/metrics.json"))
print(m.get("best_cost"), m.get("runtime_s"), m.get("git_sha"), m.get("python"))
PY
)
EOF

# Remove old block safely
if [ -f PROJECT_SUMMARY.md ]; then
  awk 'BEGIN{skip=0}
       /<!-- STEP1-START -->/{skip=1; next}
       /<!-- STEP1-END -->/{skip=0; next}
       { if (!skip) print }' PROJECT_SUMMARY.md > PROJECT_SUMMARY.md.tmp
  mv PROJECT_SUMMARY.md.tmp PROJECT_SUMMARY.md
else
  touch PROJECT_SUMMARY.md
fi

# Append new block
{
  echo ""
  echo "<!-- STEP1-START -->"
  echo "## Step 1: Static solver results (auto)"
  echo "- **Objective:** min leftover budget (greedy baseline)"
  echo "- **Best cost:** ${BESTCOST}"
  echo "- **Runtime:** ${RUNTIME}s"
  echo "- **Artifacts:** [solution](outputs/step_1/solution.json) | [metrics](outputs/step_1/metrics.json)"
  echo "- **Git:** [${SHA}](${REPO_URL}/commit/${SHA})"
  echo "<!-- STEP1-END -->"
} >> PROJECT_SUMMARY.md

echo "${c_ok}Step 1 complete.${c_reset} Summary updated."
