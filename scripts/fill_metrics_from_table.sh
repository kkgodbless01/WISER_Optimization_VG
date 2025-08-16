#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

TABLE="${1:-results/comparison_tables/solver_vs_baseline.md}"
LINKEDIN="LINKEDIN_POST.txt"
SUMMARY="PROJECT_SUMMARY.md"

if [ ! -f "$TABLE" ]; then
  echo "Table not found: $TABLE" >&2
  exit 1
fi

# Helper to get a field value by matching a row label and picking a column
extract_field() {
  local row_label="$1" col="$2"
  awk -F'|' -v col="$col" -v lbl="$row_label" '
    $0 ~ lbl {
      gsub(/^[ \t]+|[ \t]+$/, "", $col)
      print $col; exit
    }' "$TABLE"
}

# Read values from the comparison table
solver_rt="$(extract_field '^\\|[[:space:]]*Average Runtime \\(s\\)' 3)"
base_rt="$(extract_field   '^\\|[[:space:]]*Average Runtime \\(s\\)' 4)"
solver_acc="$(extract_field '^\\|[[:space:]]*Solution Accuracy \\(%\\)' 3)"
base_acc="$(extract_field   '^\\|[[:space:]]*Solution Accuracy \\(%\\)' 4)"
speedup="$(extract_field    '^\\|[[:space:]]*Speedup Factor' 3)"

# Replace None/empty/dash with 'pending'
fallback() { local v="${1:-}"; case "$v" in ""|"None"|"—"|"-") echo "pending" ;; *) echo "$v" ;; esac; }
solver_rt="$(fallback "$solver_rt")"
base_rt="$(fallback "$base_rt")"
solver_acc="$(fallback "$solver_acc")"
base_acc="$(fallback "$base_acc")"
speedup="$(fallback "$speedup")"

# Update LINKEDIN_POST.txt
if [ -f "$LINKEDIN" ]; then
  sed -i -E \
    -e "s#^• Runtime:.*#• Runtime: Solver = ${solver_rt} s vs Baseline = ${base_rt} s#g" \
    -e "s#^• Accuracy:.*#• Accuracy: Solver = ${solver_acc} % vs Baseline = ${base_acc} %#g" \
    "$LINKEDIN"
fi

# Update PROJECT_SUMMARY.md (replace existing rows cleanly)
if [ -f "$SUMMARY" ]; then
  sed -i -E \
    -e "s#^\\|[[:space:]]*Average Runtime \\(s\\)[^|]*\\|[^|]*\\|[^|]*\\|#| Average Runtime (s) | ${solver_rt} | ${base_rt} |#g" \
    -e "s#^\\|[[:space:]]*Solution Accuracy \\(%\\)[^|]*\\|[^|]*\\|[^|]*\\|#| Solution Accuracy (%) | ${solver_acc} | ${base_acc} |#g" \
    -e "s#^\\|[[:space:]]*Speedup Factor[^|]*\\|[^|]*\\|[^|]*\\|#| Speedup Factor | ${speedup} | — |#g" \
    "$SUMMARY"
fi

echo "Updated:"
[ -f "$LINKEDIN" ] && echo " - $LINKEDIN"
[ -f "$SUMMARY" ] && echo " - $SUMMARY"
