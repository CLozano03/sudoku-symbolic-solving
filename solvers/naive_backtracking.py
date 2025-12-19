def is_valid(grid, row, col, num):
    N = len(grid)
    M = int(N**0.5)

    # Check row
    for x in range(N):
        if grid[row][x] == num:
            return False

    # Check column
    for x in range(N):
        if grid[x][col] == num:
            return False

    # Check subgrid
    start_row = row - row % M
    start_col = col - col % M
    for i in range(M):
        for j in range(M):
            if grid[i + start_row][j + start_col] == num:
                return False

    return True


def solve(grid):
    """
    Receives a Sudoku matrix (N x N) and solves it IN-PLACE using Naive Backtracking
    Returns the same matrix reference with the solved values.

    If no solution is found, returns None.
    """
    # Dynamic size calculation
    N = len(grid)

    row, col = -1, -1
    empty_found = False

    for i in range(N):
        for j in range(N):
            if grid[i][j] == 0:
                row, col = i, j
                empty_found = True
                break
        if empty_found:
            break

    if not empty_found:
        return grid  # Solved

    for num in range(1, N + 1):
        if is_valid(grid, row, col, num):
            grid[row][col] = num

            if solve(grid):
                return grid

            grid[row][col] = 0  # Backtrack

    return None  # Trigger backtracking
