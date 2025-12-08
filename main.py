import copy
import math
import sys
import time

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


def read_sudoku(file_path):
    """Reads the sudoku from a text file and returns a matrix of integers."""
    grid = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                row = [int(num) for num in line.strip().split()]
                if row:
                    grid.append(row)
        return grid
    except FileNotFoundError:
        print(f"FileNotFoundError: {file_path} not found.")
        sys.exit(1)


def print_grid(grid):
    """Helper to visualize the result in the console."""
    for row in grid:
        print(" ".join(str(n) for n in row))


def check_filled(grid):
    """
    Checks if the grid is completely filled (contains no zeros).
    Returns True if filled, False if any empty cell remains.
    """
    return all(cell != 0 for row in grid for cell in row)


def check_correct(grid):
    """
    Validates if the Sudoku solution is correct according to the rules:
    1. Rows contain unique numbers from 1 to N.
    2. Columns contain unique numbers from 1 to N.
    3. Blocks (boxes) contain unique numbers from 1 to N.
    """
    N = len(grid)
    M = int(math.isqrt(N))

    if M * M != N:
        print(f"Error: Invalid grid size {N}x{N} (N is not a perfect square).")
        return False

    # The expected set of numbers for every row/col/box: {1, 2, ..., N}
    expected_set = set(range(1, N + 1))

    # --- A) Check ROWS ---
    for row in grid:
        # Converting to set removes duplicates and ignores order
        if set(row) != expected_set:
            return False

    # --- B) Check COLUMNS ---
    for c in range(N):
        # Construct the column list iterating through rows
        column = [grid[r][c] for r in range(N)]
        if set(column) != expected_set:
            return False

    # --- C) Check BLOCKS (Boxes) ---
    # Iterate through the top-left corner of each block
    for box_row_start in range(0, N, M):
        for box_col_start in range(0, N, M):
            block = []
            # Iterate through cells inside the block
            for i in range(M):
                for j in range(M):
                    block.append(grid[box_row_start + i][box_col_start + j])

            if set(block) != expected_set:
                return False

    return True


def validate_solution(grid):
    return check_filled(grid) and check_correct(grid)


def run_solver(name, module, original_sudoku):
    print(f"--- Running: {name} ---")

    # Deep copy to avoid in-place modifications affecting other solvers
    input_grid = copy.deepcopy(original_sudoku)

    start_time = time.time()
    try:
        # Call the standardized solve() function
        result = module.solve(input_grid)
        end_time = time.time()

        elapsed_time = end_time - start_time

        if result and validate_solution(result):
            print(f"Solved in {elapsed_time:.5f} seconds!")
            print_grid(result)
        else:
            print("No solution found.")

    except Exception as e:
        print(f"Error during execution of {name}: {e}")
    print("\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <sudoku_file>")
        sys.exit(1)

    sudoku_path = sys.argv[1]
    base_sudoku = read_sudoku(sudoku_path)

    print(
        f"Sudoku loaded ({len(base_sudoku)}x{len(base_sudoku[0])}) from {sudoku_path}\n"
    )

    # List of tuples (Readable Name, Imported Module)
    solvers = [
        ("Google OR-Tools (CP-SAT)", googleORTools_solver),
        ("Z3 Solver (SMT)", z3_solver),
        ("Prolog (PySwip)", prolog_solver),
        ("CLIPS", clips_solver),
        ("PySAT (Glucose4)", pysat_solver),
    ]

    for name, mod in solvers:
        run_solver(name, mod, base_sudoku)


if __name__ == "__main__":
    main()
