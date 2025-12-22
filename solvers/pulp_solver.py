import math
import pulp



@staticmethod
def solve(grid):
    """
    Resuelve un sudoku NxN usando ILP (PuLP).
    grid: matriz NxN con 0 para celdas vacías
    return: matriz NxN resuelta
    """

    N = len(grid)
    k = int(math.sqrt(N))

    if k * k != N:
        raise ValueError("El tamaño del sudoku debe ser un cuadrado perfecto (N = k^2)")

    # Crear problema
    prob = pulp.LpProblem("Sudoku", pulp.LpStatusOptimal)

    # Variables binarias x[r][c][n]
    x = pulp.LpVariable.dicts(
        "x",
        (range(N), range(N), range(1, N + 1)),
        cat="Binary"
    )

    # Cada celda tiene exactamente un número
    for r in range(N):
        for c in range(N):
            prob += pulp.lpSum(x[r][c][n] for n in range(1, N + 1)) == 1

    # Restricción de filas
    for r in range(N):
        for n in range(1, N + 1):
            prob += pulp.lpSum(x[r][c][n] for c in range(N)) == 1

    # Restricción de columnas
    for c in range(N):
        for n in range(1, N + 1):
            prob += pulp.lpSum(x[r][c][n] for r in range(N)) == 1

    # Restricción de bloques k×k
    for br in range(k):
        for bc in range(k):
            for n in range(1, N + 1):
                prob += pulp.lpSum(
                    x[r][c][n]
                    for r in range(br * k, br * k + k)
                    for c in range(bc * k, bc * k + k)
                ) == 1

    # Celdas fijas
    for r in range(N):
        for c in range(N):
            if grid[r][c] != 0:
                prob += x[r][c][grid[r][c]] == 1

    # Resolver
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    if pulp.LpStatus[prob.status] != "Optimal":
        raise ValueError("El sudoku no tiene solución")

    # Construir solución
    solution = [[0] * N for _ in range(N)]
    for r in range(N):
        for c in range(N):
            for n in range(1, N + 1):
                if pulp.value(x[r][c][n]) == 1:
                    solution[r][c] = n
                    break

    return solution
