import os
import tempfile
import math

from pyswip import Prolog

# --- 1. Prolog Logic Definition (Global Constant) ---
PROLOG_CODE = """
:- use_module(library(clpfd)).

% sudoku_solve(+Rows, +K)
sudoku_solve(Rows, K) :-
    length(Rows, N),
    maplist(same_length(Rows), Rows),

    K*K #= N,

    append(Rows, Vs),
    Vs ins 1..N,

    maplist(all_distinct, Rows),
    transpose(Rows, Columns),
    maplist(all_distinct, Columns),

    blocks(Rows, K),
    maplist(label, Rows).

% ---------- BLOQUES KxK ----------

blocks([], _).
blocks(Rows, K) :-
    length(RowsBlock, K),
    append(RowsBlock, RestRows, Rows),
    blocks_in_rows(RowsBlock, K),
    blocks(RestRows, K).

blocks_in_rows(Rows, K) :-
    maplist(split_k(K), Rows, Heads, Tails),
    append(Heads, Block),
    all_distinct(Block),
    (   maplist(=([]), Tails)
    ->  true
    ;   blocks_in_rows(Tails, K)
    ).

split_k(K, Row, Head, Tail) :-
    length(Head, K),
    append(Head, Tail, Row).
"""

# Initialize a global Prolog instance
prolog = Prolog()

# Disable redefine warnings to keep the output clean
list(prolog.query("set_prolog_flag(redefine_warnings, off)"))

# Create a temporary file to load the Prolog logic
temp_file_path = ""
try:
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".pl", delete=False
    ) as temp_pl:
        temp_pl.write(PROLOG_CODE)
        temp_file_path = temp_pl.name

    # Consult (load) the Prolog logic into memory
    prolog.consult(temp_file_path.replace("\\", "/"))

finally:
    # Once loaded into memory, we can safely delete the temporary file
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)


def solve(grid):
    import math

    N = len(grid)
    if any(len(row) != N for row in grid):
        print("Error: Grid must be NxN")
        return None

    K = int(math.sqrt(N))
    if K * K != N:
        print("Error: N must be a perfect square")
        return None

    sudoku_str = grid_to_prolog(grid)
    query_string = f"Rows = {sudoku_str}, sudoku_solve(Rows, {K})"

    try:
        solutions = list(prolog.query(query_string))
        if not solutions:
            return None

        solved_rows = solutions[0]["Rows"]
        for i in range(N):
            for j in range(N):
                grid[i][j] = int(solved_rows[i][j])

        return grid

    except Exception as e:
        print(f"Prolog Error: {e}")
        return None
    
def grid_to_prolog(grid):
    rows = []
    for row in grid:
        prolog_row = []
        for cell in row:
            if cell == 0:
                prolog_row.append("_")
            else:
                prolog_row.append(str(cell))
        rows.append(f"[{', '.join(prolog_row)}]")
    return f"[{', '.join(rows)}]"

