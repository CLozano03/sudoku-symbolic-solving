import os
import tempfile

from pyswip import Prolog

# --- 1. Prolog Logic Definition (Global Constant) ---
PROLOG_CODE = """
:- use_module(library(clpfd)).

% Main predicate to solve the Sudoku
sudoku_solve(Rows) :-
    length(Rows, 9), maplist(same_length(Rows), Rows),
    append(Rows, Vs), Vs ins 1..9,
    maplist(all_distinct, Rows),
    transpose(Rows, Columns),
    maplist(all_distinct, Columns),
    Rows = [As,Bs,Cs,Ds,Es,Fs,Gs,Hs,Is],
    blocks(As, Bs, Cs),
    blocks(Ds, Es, Fs),
    blocks(Gs, Hs, Is),
    maplist(label, Rows).

% Helper predicate to validate 3x3 blocks
blocks([], [], []).
blocks([N1,N2,N3|Ns1], [N4,N5,N6|Ns2], [N7,N8,N9|Ns3]) :-
    all_distinct([N1,N2,N3,N4,N5,N6,N7,N8,N9]),
    blocks(Ns1, Ns2, Ns3).
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
    """
    Receives a Sudoku matrix (9x9) and solves it IN-PLACE using the pre-loaded Prolog logic.
    Returns the same matrix reference with the solved values.

    If no solution is found or the grid is not 9x9, returns None.
    """

    # Validation: Ensure the grid is 9x9
    if len(grid) != 9 or len(grid[0]) != 9:
        print("Error: This Prolog solver is strictly for 9x9 Sudokus.")
        return None

    try:
        sudoku_str = str(grid).replace("0", "_")
        query_string = f"Rows = {sudoku_str}, sudoku_solve(Rows)"

        # Execute Query
        solutions = list(prolog.query(query_string))

        if solutions:
            # PySwip returns a list of dictionaries.
            solved_rows = solutions[0]["Rows"]

            # Update the original grid IN-PLACE
            for i in range(9):
                for j in range(9):
                    grid[i][j] = int(solved_rows[i][j])

            return grid
        else:
            return None

    except Exception as e:
        print(f"Prolog Error: {e}")
        return None
