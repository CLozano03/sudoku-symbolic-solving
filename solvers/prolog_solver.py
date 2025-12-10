import os
import tempfile

from pyswip import Prolog

# --- 1. Definición de la lógica (Global) ---
PROLOG_CODE = """
:- use_module(library(clpfd)).

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

blocks([], [], []).
blocks([N1,N2,N3|Ns1], [N4,N5,N6|Ns2], [N7,N8,N9|Ns3]) :-
    all_distinct([N1,N2,N3,N4,N5,N6,N7,N8,N9]),
    blocks(Ns1, Ns2, Ns3).
"""

# --- 2. Inicialización del motor Prolog (Se ejecuta UNA vez) ---
# Inicializamos Prolog fuera de la función
prolog = Prolog()
temp_file_path = ""

# Opcional: Desactivamos warnings desde Python ANTES de cargar nada
list(prolog.query("set_prolog_flag(redefine_warnings, off)"))

# Creamos y cargamos el archivo temporal una sola vez al arrancar el script
try:
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".pl", delete=False
    ) as temp_pl:
        temp_pl.write(PROLOG_CODE)
        temp_file_path = temp_pl.name

    # Cargamos la lógica en memoria
    # El replace es vital para Windows
    prolog.consult(temp_file_path.replace("\\", "/"))

finally:
    # Una vez cargado en memoria RAM, podemos borrar el archivo físico
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)


# --- 3. Función de resolución (Limpia y Rápida) ---
def solve(grid):
    """
    Recibe una matriz Sudoku (9x9) y la resuelve usando la lógica Prolog ya cargada.
    """

    # Validación simple
    if len(grid) != 9 or len(grid[0]) != 9:
        print("Error: El solver solo acepta Sudokus 9x9.")
        return None

    try:
        # Preparar la Query
        # Convertimos 0 de Python a variable anónima de Prolog (_)
        sudoku_str = str(grid).replace("0", "_")
        query_string = f"Rows = {sudoku_str}, sudoku_solve(Rows)"

        # Ejecutar Query
        # Nota: Ya no hacemos consult aquí dentro
        solutions = list(prolog.query(query_string))

        if solutions:
            solved_rows = solutions[0]["Rows"]

            # Actualizamos la grid original
            for i in range(9):
                for j in range(9):
                    grid[i][j] = int(solved_rows[i][j])
            return grid
        else:
            return None

    except Exception as e:
        print(f"Prolog Error: {e}")
        return None
