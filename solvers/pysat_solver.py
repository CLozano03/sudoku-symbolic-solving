from pysat.card import CardEnc
from pysat.solvers import Solver


def solve(grid):
    """
    Receives a Sudoku matrix (N x N) and solves it IN-PLACE using PySAT.

    CORRECTION: Now manages 'top_id' to prevent variable collision if
    the encoding generates auxiliary variables.
    """
    N = len(grid)
    M = int(N**0.5)

    # 1. Variable Mapping
    # r, c in 0..N-1, v in 1..N
    var = lambda r, c, v: (r * N * N) + (c * N) + v

    # Max variable used by our grid logic
    max_id = N * N * N

    # Current top variable ID (starts at max_id)
    # We will update this every time we add a constraint that might need new vars
    current_top = max_id

    with Solver(name="g4") as s:
        # --- 2. CONSTRAINTS ---

        # Helper to add constraints safely updating top_id
        def add_exactly_one(literals):
            nonlocal current_top
            # We allow PySAT to choose the best encoding (default) or force one.
            # Passing top_id is crucial to avoid clashes.
            cnf = CardEnc.equals(lits=literals, bound=1, top_id=current_top)

            s.append_formula(cnf)
            # Update the known top variable count from the generated CNF
            current_top = cnf.nv

        # A) Cells
        for r in range(N):
            for c in range(N):
                literals = [var(r, c, v) for v in range(1, N + 1)]
                add_exactly_one(literals)

        # B) Rows
        for r in range(N):
            for v in range(1, N + 1):
                literals = [var(r, c, v) for c in range(N)]
                add_exactly_one(literals)

        # C) Columns
        for c in range(N):
            for v in range(1, N + 1):
                literals = [var(r, c, v) for r in range(N)]
                add_exactly_one(literals)

        # D) Blocks
        for box_r in range(0, N, M):
            for box_c in range(0, N, M):
                for v in range(1, N + 1):
                    literals = []
                    for i in range(M):
                        for j in range(M):
                            literals.append(var(box_r + i, box_c + j, v))
                    add_exactly_one(literals)

        # --- 3. FIXED VALUES ---
        for r in range(N):
            for c in range(N):
                if grid[r][c] != 0:
                    val = grid[r][c]
                    s.add_clause([var(r, c, val)])

        # --- 4. SOLVE ---
        if s.solve():
            model = s.get_model()
            model_set = set(model)

            for r in range(N):
                for c in range(N):
                    for v in range(1, N + 1):
                        if var(r, c, v) in model_set:
                            grid[r][c] = v
                            break
            return grid
        else:
            return None
