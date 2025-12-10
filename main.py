import copy
import glob
import math
import os
import re
import statistics
import sys
import time

# Import solvers
try:
    from solvers import (
        clips_solver,
        googleORTools_solver,
        prolog_solver,
        pysat_solver,
        z3_solver,
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

# --- Helper Functions (Reading and Validation) ---


def read_sudoku(file_path):
    """Reads the sudoku from a text file and returns a matrix of integers."""
    grid = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                nums = re.findall(r"\d+", line)
                row = [int(num) for num in nums]
                if row:
                    grid.append(row)
        return grid
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def check_filled(grid):
    """Checks if the grid is completely filled (no zeros)."""
    return all(cell != 0 for row in grid for cell in row)


def check_correct(grid):
    """
    Validates if the Sudoku solution is correct according to rules:
    1. Rows contain unique numbers from 1 to N.
    2. Columns contain unique numbers from 1 to N.
    3. Blocks (boxes) contain unique numbers from 1 to N.
    """
    N = len(grid)
    M = int(math.isqrt(N))
    if M * M != N:
        return False
    expected_set = set(range(1, N + 1))

    # Check Rows
    for row in grid:
        if set(row) != expected_set:
            return False

    # Check Columns
    for c in range(N):
        column = [grid[r][c] for r in range(N)]
        if set(column) != expected_set:
            return False

    # Check Blocks
    for box_row_start in range(0, N, M):
        for box_col_start in range(0, N, M):
            block = []
            for i in range(M):
                for j in range(M):
                    block.append(grid[box_row_start + i][box_col_start + j])
            if set(block) != expected_set:
                return False
    return True


def validate_solution(grid):
    """Combines filling check and logic check."""
    if not grid:
        return False
    return check_filled(grid) and check_correct(grid)


# --- Benchmark Logic ---


def run_benchmark(solvers):
    sudoku_files = glob.glob("sudokus/*.txt")
    if not sudoku_files:
        print("No .txt files found in the 'sudokus/' folder.")
        sys.exit(1)

    print(f"--- Starting Benchmark with {len(sudoku_files)} sudokus ---\n")

    stats = {
        name: {"times": [], "failures": 0, "errors": 0} for name, _ in solvers
    }

    for i, file_path in enumerate(sudoku_files):
        file_name = os.path.basename(file_path)
        base_sudoku = read_sudoku(file_path)

        if not base_sudoku:
            continue

        print(f"[{i + 1}/{len(sudoku_files)}] Processing: {file_name}")

        for name, module in solvers:
            # Deep copy to ensure fresh input for every solver
            input_grid = copy.deepcopy(base_sudoku)

            start_time = time.time()
            try:
                # Execute solver
                result = module.solve(input_grid)
                end_time = time.time()
                elapsed = end_time - start_time

                if result and validate_solution(result):
                    stats[name]["times"].append(elapsed)
                else:
                    stats[name]["failures"] += 1
            except Exception:
                # Catch execution errors (crashes)
                stats[name]["errors"] += 1
                # print(f"  [!] Error in {name}: {e}")

    print_results_table(stats, len(sudoku_files))


def print_results_table(stats, total_sudokus):
    print("\n" + "=" * 85)
    print(
        f"{'RANK':<5} | {'SOLVER':<20} | {'SOLVED':<8} | {'AVG TIME (s)':<12} | {'MIN (s)':<8} | {'MAX (s)':<8}"
    )
    print("=" * 85)

    # Ranking criteria:
    # 1. Highest number of solved puzzles (descending)
    # 2. Lowest average time (ascending)
    ranking_data = []

    for name, data in stats.items():
        solved_count = len(data["times"])
        if solved_count > 0:
            avg_time = statistics.mean(data["times"])
            min_time = min(data["times"])
            max_time = max(data["times"])
        else:
            avg_time = float("inf")
            min_time = 0
            max_time = 0

        ranking_data.append(
            {
                "name": name,
                "solved": solved_count,
                "avg": avg_time,
                "min": min_time,
                "max": max_time,
            }
        )

    # Sort
    ranking_data.sort(key=lambda x: (-x["solved"], x["avg"]))

    for rank, item in enumerate(ranking_data, 1):
        solved_str = f"{item['solved']}/{total_sudokus}"
        avg_str = f"{item['avg']:.4f}" if item["solved"] > 0 else "-"
        min_str = f"{item['min']:.4f}" if item["solved"] > 0 else "-"
        max_str = f"{item['max']:.4f}" if item["solved"] > 0 else "-"

        print(
            f"{rank:<5} | {item['name']:<20} | {solved_str:<8} | {avg_str:<12} | {min_str:<8} | {max_str:<8}"
        )

    print("=" * 85)
    print(f"Total sudokus processed: {total_sudokus}")


if __name__ == "__main__":
    solvers = [
        ("Google OR-Tools", googleORTools_solver),
        ("Z3 Solver", z3_solver),
        ("Prolog (PySwip)", prolog_solver),
        # ("CLIPS", clips_solver),
        ("PySAT (Glucose4)", pysat_solver),
    ]
    run_benchmark(solvers)
