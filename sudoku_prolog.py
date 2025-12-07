import os
import tempfile

from pyswip import Prolog

# ==========================================
# 1. Definición de Reglas (Tu código Prolog)
# ==========================================
codigo_prolog = """
:- use_module(library(clpfd)).

solve(Rows) :-
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

# ==========================================
# 2. Funciones Auxiliares de Python
# ==========================================


def leer_sudoku(archivo):
    """Lee el archivo input.txt y devuelve una lista de listas."""
    tablero = []
    try:
        with open(archivo, "r") as f:
            for linea in f:
                # Convertimos cada caracter en entero.
                # Asumimos que están separados por espacios o son seguidos.
                # Esta lógica busca números en la línea.
                fila = [
                    int(num) for num in linea.strip().split() if num.isdigit()
                ]
                if len(fila) == 9:
                    tablero.append(fila)
        return tablero
    except FileNotFoundError:
        print(f"Error: No se encuentra {archivo}")
        return []


def imprimir_sudoku(tablero):
    """Imprime el tablero de forma legible."""
    print("-" * 25)
    for i, fila in enumerate(tablero):
        linea = ""
        for j, valor in enumerate(fila):
            linea += f" {valor} "
            if (j + 1) % 3 == 0 and j < 8:
                linea += "|"
        print(linea)
        if (i + 1) % 3 == 0 and i < 8:
            print("-" * 25)
    print("-" * 25)


# ==========================================
# 3. Ejecución Principal
# ==========================================

prolog = Prolog()

# Creamos el archivo temporal
with tempfile.NamedTemporaryFile(
    mode="w+", suffix=".pl", delete=False
) as temp_pl:
    temp_pl.write(codigo_prolog)
    temp_nombre = temp_pl.name

try:
    # 1. Cargamos las reglas
    prolog.consult(temp_nombre)
    print("Reglas cargadas correctamente.")

    # 2. Leemos el input
    # Si no tienes el archivo, pon aquí una lista manual para probar
    sudoku_input = leer_sudoku("input.txt")

    if not sudoku_input:
        print("No se pudo cargar el Sudoku. Usando ejemplo por defecto...")
        sudoku_input = [
            [0, 0, 0, 2, 6, 0, 7, 0, 1],
            [6, 8, 0, 0, 7, 0, 0, 9, 0],
            [1, 9, 0, 0, 0, 4, 5, 0, 0],
            [8, 2, 0, 1, 0, 0, 0, 4, 0],
            [0, 0, 4, 6, 0, 2, 9, 0, 0],
            [0, 5, 0, 0, 0, 3, 0, 2, 8],
            [0, 0, 9, 3, 0, 0, 0, 7, 4],
            [0, 4, 0, 0, 5, 0, 0, 3, 6],
            [7, 0, 3, 0, 1, 8, 0, 0, 0],
        ]

    print("\n--- Sudoku Original ---")
    imprimir_sudoku(sudoku_input)

    # 3. Preparamos la query
    # PySwip necesita recibir la lista como string de Prolog.
    # El truco clave: Reemplazar los 0 de Python por variables anónimas (_) de Prolog
    sudoku_str = str(sudoku_input).replace("0", "_")

    # La query será: Rows = [[_,2,...], ...], solve(Rows).
    query = f"Rows = {sudoku_str}, solve(Rows)"

    # 4. Buscamos la solución
    soluciones = list(prolog.query(query))

    if soluciones:
        # PySwip devuelve un diccionario. 'Rows' contiene la solución.
        solucion_final = soluciones[0]["Rows"]
        print("\n--- Sudoku Resuelto ---")
        imprimir_sudoku(solucion_final)
    else:
        print("\nNo se encontró solución (o el Sudoku es inválido).")

except Exception as e:
    print(f"Ocurrió un error: {e}")

finally:
    # Limpieza
    if os.path.exists(temp_nombre):
        os.remove(temp_nombre)
