def replace_metric_lines(text: str, label: str, solver_val: str, base_val: str) -> str:
    """Safely replace metric lines without regex back-reference pitfalls."""
    new_lines = []
    for line in text.splitlines():
        low = line.lower()
        if label.lower() in low and "solver" in low and "baseline" in low:
            # Overwrite the whole line in a clean format
            line = f"• {label}: Solver = {solver_val} vs Baseline = {base_val}"
        new_lines.append(line)
    return "\n".join(new_lines)

