from ortools.sat.python import cp_model


def solve(grid):
    """
    Receives a Sudoku matrix (N x N) and solves it IN-PLACE using Google OR-Tools CP-SAT Solver.
    Returns the same matrix reference with the solved values.

    If no solution is found, returns None.
    """

    N = len(grid)
    M = int(N**0.5)

    model = cp_model.CpModel()

    # 1. Create variables
    grid_vars = {}
    for i in range(N):
        for j in range(N):
            # Use 'grid' directly to read initial values
            if grid[i][j] != 0:
                # Constant value
                grid_vars[i, j] = model.NewIntVar(
                    grid[i][j], grid[i][j], f"cell_{i}_{j}"
                )
            else:
                grid_vars[i, j] = model.NewIntVar(1, N, f"cell_{i}_{j}")

    # 2. Constraints

    # a) Rows: All different
    for i in range(N):
        model.AddAllDifferent([grid_vars[i, j] for j in range(N)])

    # b) Columns: All different
    for j in range(N):
        model.AddAllDifferent([grid_vars[i, j] for i in range(N)])

    # c) Blocks M x M: All different
    for box_row in range(0, N, M):
        for box_col in range(0, N, M):
            box_vars = []
            for i in range(M):
                for j in range(M):
                    box_vars.append(grid_vars[box_row + i, box_col + j])
            model.AddAllDifferent(box_vars)

    # 3. Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for i in range(N):
            for j in range(N):
                # Write directly into the input 'grid' matrix
                grid[i][j] = solver.Value(grid_vars[i, j])
        return grid  # Return the reference to the modified matrix
    else:
        return None
