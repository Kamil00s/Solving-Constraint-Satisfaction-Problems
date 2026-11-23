import contextlib
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from parser import load_domains, load_grid, to_string
from solver import solve_with_stats
from validator import validate


def run_all(
    fc: bool = False,
    heuristic: bool = False,
    ac3: bool = False,
    timeout_sec: float = 60.0,
):
    instances_dir = ROOT / "instances"
    instance_files = sorted(instances_dir.glob("*.txt"))

    print(f"\n### MODE: fc={fc}, heuristic={heuristic}, ac3={ac3} ###")
    for inst_path in instance_files:
        grid = load_grid(inst_path)
        n = grid.shape[0]
        domains = load_domains(inst_path)  # CSP constructed before timer starts

        stats = solve_with_stats(
            domains,
            n,
            fc=fc,
            heuristic=heuristic,
            ac3_enabled=ac3,
            timeout_sec=timeout_sec,
        )

        print("=" * 60)
        print(f"Instance: {inst_path.name} ({n}x{n})")
        print(to_string(grid))
        print(f"Timed out: {stats['timed_out']}")
        print(f"Duration (s): {stats['elapsed_sec']:.4f}")
        print(f"Variable assignments: {stats['assignments']}")
        print(f"Backtracking steps: {stats['backtracks']}")

        if stats["solution"] is not None:
            with contextlib.redirect_stdout(io.StringIO()):
                valid = validate(stats["solution"])  # Suppress validation output
            print(f"Solution ({'valid' if valid else 'invalid'}):")
            print(to_string(stats["solution"]))
        else:
            print("Solution: None (aborted or unsatisfiable)")


if __name__ == "__main__":
    run_all(fc=False, heuristic=False, ac3=False, timeout_sec=60.0)
    run_all(fc=True, heuristic=False, ac3=False, timeout_sec=60.0)
    run_all(fc=True, heuristic=True, ac3=False, timeout_sec=60.0)
    run_all(fc=True, heuristic=True, ac3=True, timeout_sec=60.0)