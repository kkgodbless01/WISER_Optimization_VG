#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

log(){ printf "\n==> %s\n" "$*"; }

# 2.1 Compute metrics from model JSON and update the comparison table
log "Deriving accuracy from model JSON (targets + guardrails)"
python3 tools/metrics_from_portfolio.py || { echo "Model-derived metrics failed; keeping existing table."; }

# 2.2 Fill recruiter-facing files from the table (placeholder-aware)
log "Updating PROJECT_SUMMARY.md and LINKEDIN_POST.txt"
scripts/fill_metrics_from_table.sh results/comparison_tables/solver_vs_baseline.md

# 2.3 Commit & push
log "Git commit & push"
git add results/comparison_tables/solver_vs_baseline.md PROJECT_SUMMARY.md LINKEDIN_POST.txt 2>/dev/null || true
ts=$(date -u +'%Y-%m-%d %H:%M:%SZ')
git commit -m "Docs: update metrics from model-derived accuracy [$ts]" || true
git push || true

log "Done"
