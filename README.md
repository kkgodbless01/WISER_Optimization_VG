# WISER Vanguard optimization challenge — benchmarking classical and quantum solvers

Repository for Womanium’s WISER Quantum 2025 Vanguard Optimization Challenge — a hands-on exploration of classical and quantum-inspired solvers for high-dimensional, constraint-heavy portfolio construction. This repo emphasizes clear benchmarks, transparent documentation, and fully reproducible workflows.

---

## 1. Challenge overview

Vanguard’s portfolio construction process balances risk, return, and investor preferences across a wide landscape of asset classes and constraints. As portfolios scale to thousands of securities with intricate guardrails and near–real-time trading demands, classical optimization tools like GUROBI can hit limits in speed, scalability, and solution diversity. This challenge explores sampling-based quantum optimization to overcome those barriers using hybrid quantum–classical algorithms and decomposition pipelines.

**Goals:**
- Efficiently solve high-dimensional, constraint-heavy portfolio optimization problems.
- Deliver near-optimal asset allocations within tight runtime windows.
- Scale to real-world use cases like fixed income ETF creation and index tracking.
- Preserve critical business metrics such as tracking error, excess return, and risk exposure.

We use binary decision variables and quadratic objectives to simulate realistic trading scenarios. The challenge is to achieve computational gains while maintaining interpretability, robustness, and alignment with core investment principles.

---

## 2. Challenge duration

- 4 weeks total
- Teams start: July 15, 2025
- Submission deadline: August 10, 2025

---

## 3. Team guidelines

- Team size: maximum 3 participants.
- All team members must be enrolled in Womanium WISER Quantum 2025.
- Everyone is eligible to participate and win Womanium grants.
- Top participants may be selected for Womanium QSL fellowships with Vanguard.

---

## 4. Tasks and deliverables

1) Review the mathematical formulation focusing on binary decision variables, linear constraints, and the quadratic objective.  
2) Convert the constrained binary optimization problem to a formulation compatible with a quantum optimization algorithm (e.g., unconstrained form).  
3) Implement a quantum optimization routine (e.g., VQE or your best-judged method) for problems of type (2).  
4) Challenge: Solve the problem in (1) using your quantum formulation.  
5) Challenge subtask: Validate your solution in (4) using a classical routine; compare solution quality against a classical benchmark with metrics like cost function value, convergence traces, and scaling behavior.

Note: The “show-and-tell” session replaces formal presentations; you’ll demo your prototype live.

---

## 5. Benchmarking pipeline and solver comparison

This repository benchmarks classical and quantum-inspired variants on realistic constraints. We track runtime, objective value, constraint satisfaction, and scaling behavior. Notebooks and CSV outputs make comparisons auditable and repeatable.

- **Inputs:** problem instances in `data/`, formulation code in `src/`
- **Runs:** executed in `notebooks/` with seeds and config captured
- **Outputs:** metrics and artifacts in `results/` (CSV/JSON/plots)

### 5.1 Example solver comparison table

Replace the placeholder values with your actual metrics after running the notebooks.

| Solver variant         | Runtime (s) | Objective value | Constraints met | Optimality gap (%) | Notes                                 |
|------------------------|------------:|----------------:|----------------:|-------------------:|---------------------------------------|
| python-mip (baseline)  |     TBD     |        TBD      |       ✅/❌      |          TBD       | Default params                         |
| python-mip (tuned)     |     TBD     |        TBD      |       ✅/❌      |          TBD       | Heuristics/cuts/tolerances adjusted    |
| Quantum-inspired (VQE) |     TBD     |        TBD      |       ✅/❌      |          TBD       | Ansatz, optimizer, shots documented    |
| Other variant          |     TBD     |        TBD      |       ✅/❌      |          TBD       | e.g., decomposed or hybrid approach    |

- Full results: see `results/` (e.g., `mip_vs_tuned.csv`) and `notebooks/benchmark_summary.ipynb`.

---

## 6. Setup and environment

### 6.1 Quickstart

```bash
# Clone the repo
git clone https://github.com/kkgodbless01/WISER_Optimization_VG.git
cd WISER_Optimization_VG

# Create a virtual environment
python -m venv .venv

# Activate it
# Windows (PowerShell)
. .\.venv\Scripts\Activate.ps1
# Windows (Git Bash)
source .venv/Scripts/activate
# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

### 6.2 Key packages

- `python-mip`
- `numpy`, `pandas`
- `matplotlib`, `seaborn`
- `jupyter`, `ipykernel`
- `qiskit` (if running VQE or quantum experiments)

> 💡 Tip: Pin versions in `requirements.txt` to guarantee reproducibility across machines

## 7. Reproducibility checklist

- ✅ Python version recorded (e.g., 3.10.x) and environment isolated in `.venv`
- ✅ `requirements.txt` created via `pip freeze > requirements.txt`
- ✅ Notebooks executed top-to-bottom with a fixed random seed
- ✅ All metrics exported to `results/` (CSV/JSON) with timestamps
- ✅ Config/tuning parameters logged in notebook headers or YAML
- ✅ Hardware specs and time limits noted for each run
- ✅ Plots and tables generated directly from saved results

WISER_Optimization_VG/
├─ notebooks/                 # Jupyter notebooks for experiments
│  ├─ benchmark_summary.ipynb # Aggregates metrics and tables
│  └─ <other_experiments>.ipynb
├─ results/                   # CSV/JSON metrics, plots, logs
│  ├─ mip_vs_tuned.csv
│  └─ figures/
├─ src/                       # Problem formulation and solvers
│  ├─ data_loading.py
│  ├─ formulation.py
│  └─ solvers/
├─ data/                      # Input instances (or links/instructions)
├─ docs/                      # Design notes, solver write-ups
├─ README.md
├─ requirements.txt
└─ LICENSE.txt

## 9. How to run benchmarks

To reproduce solver results and compare optimization routines:

1. **Activate environment** — `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate.bat` (Windows)  
2. **Install dependencies** — `pip install -r requirements.txt`  
3. **Set random seed for reproducibility** — Set manually at the top of each notebook (e.g., `np.random.seed(42)` or `random_state=42`)  
4. **Run solver variants** — Execute notebooks in `experiments/`, one at a time, top to bottom  
5. **Export metrics** — Each notebook saves CSV and JSON results to `results/` with timestamps  
6. **Generate plots and tables** — Final notebook (`readme_notebook.ipynb`) imports saved results and renders plots  
7. **Compare configurations** — Use tables and YAML logs to compare solver settings across runs  
8. **Hardware specs** — Recommended: Run `benchmark_utils/hardware_report.py` to capture device specs for reproducibility

## 10. Judging criteria

Submissions are evaluated against internal benchmarks at Vanguard based on:

- **Speed** — wall-clock runtime and time-to-feasible  
- **Optimality** — final cost function value, gap, and constraint satisfaction  
- **Scalability** — performance as problem size increases

## 11. Resources

- **Example VQE portfolio workflow**  
  https://eric08000800.medium.com/portfolio-optimization-with-variational-quantum-eigensolver-vqe-2-477a0ee4e988

- **Variational quantum optimization paper**  
  https://quantum-journal.org/papers/q-2020-04-20-256/

- **Program orientation video**  
  *“2025 QUANTUM PROGRAM ▯ Day 7 ▯ Projects Orientation Part 2”* — Available on YouTube

## 12. Contributing

- Open an issue to discuss enhancements or new solver variants  
- Use clear commit messages and include result CSVs for any reported metrics  
- Prefer PRs that add a notebook and a short `docs/` note explaining changes

## 13. Finalizing metrics (optional)

If you want, I can replace the **TBDs** with your latest numbers and link directly to the exact CSVs and notebooks you just pushed.
