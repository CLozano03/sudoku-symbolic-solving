from z3 import *


def solve(grid):
    """
    Receives a Sudoku matrix (N x N) and solves it IN-PLACE using Z3 (SMT Solver).
    Returns the same matrix reference with the solved values.

    If no solution is found, returns None.
    """
    # Dynamic size calculation
    N = len(grid)
    M = int(N**0.5)

    # 1. Create Z3 variables matrix
    # X[i][j] represents the cell at row i, column j
    X = [[Int(f"x_{i}_{j}") for j in range(N)] for i in range(N)]

    s = Solver()

    # 2. Basic Constraints: Range 1 to N
    for i in range(N):
        for j in range(N):
            s.add(X[i][j] >= 1, X[i][j] <= N)

    # 3. Sudoku Rules

    # a) Rows: All distinct
    for i in range(N):
        s.add(Distinct(X[i]))

    # b) Columns: All distinct
    for j in range(N):
        col = [X[i][j] for i in range(N)]
        s.add(Distinct(col))

    # c) Blocks M x M: All distinct
    for box_row in range(0, N, M):
        for box_col in range(0, N, M):
            box_vars = []
            for i in range(M):
                for j in range(M):
                    box_vars.append(X[box_row + i][box_col + j])
            s.add(Distinct(box_vars))

    # 4. Initial Constraints (Input values)
    for i in range(N):
        for j in range(N):
            if grid[i][j] != 0:
                s.add(X[i][j] == grid[i][j])

    # 5. Solve
    if s.check() == sat:
        m = s.model()
        for i in range(N):
            for j in range(N):
                # We update the python list directly.
                # .as_long() converts the Z3 integer object to a standard Python int
                grid[i][j] = m[X[i][j]].as_long()
        return grid
    else:
        return None
