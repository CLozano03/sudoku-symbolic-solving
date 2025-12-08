import os
import tempfile

# It needs an installation of SWI-Prolog in the system.
from pyswip import Prolog

# Prolog Logic Definition
PROLOG_CODE = """
:- use_module(library(clpfd)).

% Main predicate to solve the sudoku
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

% Helper predicate for 3x3 blocks
blocks([], [], []).
blocks([N1,N2,N3|Ns1], [N4,N5,N6|Ns2], [N7,N8,N9|Ns3]) :-
    all_distinct([N1,N2,N3,N4,N5,N6,N7,N8,N9]),
    blocks(Ns1, Ns2, Ns3).
"""


def solve(grid):
    """
    Receives a Sudoku matrix (9x9) and solves it IN-PLACE using Prolog (PySwip).
    Returns the same matrix reference with the solved values.

    If no solution is found or the grid is not 9x9, returns None.
    """

    # Validation: This specific Prolog logic only supports 9x9
    if len(grid) != 9 or len(grid[0]) != 9:
        print("Error: This Prolog solver is strictly for 9x9 Sudokus.")
        return None

    prolog = Prolog()
    temp_file_path = ""

    try:
        # 1. Write the Prolog code to a temporary file to consult it
        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".pl", delete=False
        ) as temp_pl:
            temp_pl.write(PROLOG_CODE)
            temp_file_path = temp_pl.name

        # 2. Load the Prolog logic
        # Note: formatting the path is necessary for Windows compatibility in Prolog
        prolog.consult(temp_file_path.replace("\\", "/"))

        # 3. Prepare the Query
        # We need to convert Python's 0 to Prolog's anonymous variable (_)
        # Example: [5, 0, 3] -> [5, _, 3]
        sudoku_str = str(grid).replace("0", "_")

        query_string = f"Rows = {sudoku_str}, sudoku_solve(Rows)"

        # 4. Execute Query
        solutions = list(prolog.query(query_string))

        if solutions:
            # PySwip returns a list of dictionaries.
            # We extract the 'Rows' variable from the first solution.
            solved_rows = solutions[0]["Rows"]

            # 5. Update the original grid IN-PLACE
            for i in range(9):
                for j in range(9):
                    grid[i][j] = int(solved_rows[i][j])

            return grid
        else:
            return None

    except Exception as e:
        print(f"Prolog Error: {e}")
        return None

    finally:
        # Cleanup: Remove the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
