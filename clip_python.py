import math

import clips

# =============================================================================
# 1. LÓGICA DE CLIPS (REGLAS SEPARADAS)
# =============================================================================
CLIPS_CONSTRUCTS = [
    # --- TEMPLATES ---
    """
    (deftemplate grid-info
       (slot n)    
       (slot m))   
    """,
    """
    (deftemplate cell
       (slot row)
       (slot col)
       (slot box) 
       (slot val)) 
    """,
    """
    (deftemplate possible
       (slot row)
       (slot col)
       (slot box)
       (slot val))
    """,
    # --- REGLAS ---
    """
    (defrule generate-candidates
       (grid-info (n ?n))
       (cell (row ?r) (col ?c) (box ?b) (val 0))
       =>
       (loop-for-count (?v 1 ?n) do
          (assert (possible (row ?r) (col ?c) (box ?b) (val ?v)))
       )
    )
    """,
    """
    (defrule prune-row
       (cell (row ?r) (val ?v&~0))
       ?f <- (possible (row ?r) (col ?c) (val ?v))
       =>
       (retract ?f))
    """,
    """
    (defrule prune-col
       (cell (col ?c) (val ?v&~0))
       ?f <- (possible (row ?r) (col ?c) (val ?v))
       =>
       (retract ?f))
    """,
    """
    (defrule prune-box
       (cell (box ?b) (val ?v&~0))
       ?f <- (possible (row ?r) (col ?c) (box ?b) (val ?v))
       =>
       (retract ?f))
    """,
    """
    (defrule single-candidate-assign
       ?f <- (possible (row ?r) (col ?c) (val ?v))
       (not (possible (row ?r) (col ?c) (val ?v2&~?v)))
       ?c-fact <- (cell (row ?r) (col ?c) (val 0))
       =>
       (modify ?c-fact (val ?v))
       (retract ?f)
    )
    """,
]


def read_sudoku_from_file_nxn(filename):
    """
    Lee la cuadrícula inicial de Sudoku desde un archivo de texto.
    """
    grid = []
    try:
        with open(filename, "r") as f:
            for line in f:
                # Extrae números, ignorando espacios extra
                row = [
                    int(n)
                    for n in line.split()
                    if n.isdigit() or (n.strip() == "0")
                ]
                if row:
                    grid.append(row)

        if not grid:
            return None, None, None

        N = len(grid)
        M = int(math.sqrt(N))
        if M * M != N:
            raise ValueError(f"N={N} no es un cuadrado perfecto.")

        return grid, N, M

    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return None, None, None


def solve_sudoku_clips(filename):
    # 1. Leer datos
    initial_grid, N, M = read_sudoku_from_file_nxn(filename)
    if initial_grid is None:
        return

    # 2. Inicializar el entorno CLIPS
    env = clips.Environment()

    # Cargar construcciones una por una
    for construct in CLIPS_CONSTRUCTS:
        try:
            env.build(construct)
        except clips.CLIPSError as e:
            print(f"❌ Error compilando regla CLIPS:\n{construct}\nError: {e}")
            return

    # Insertar información global
    env.assert_string(f"(grid-info (n {N}) (m {M}))")

    print(f"Sudoku inicial cargado (Tamaño {N}x{N}). Generando hechos...")

    # 3. Traducir la Grid de Python a Hechos de CLIPS
    for i in range(N):
        for j in range(N):
            val = initial_grid[i][j]
            row_idx = i + 1
            col_idx = j + 1

            # Cálculo del ID de la caja
            box_r = (row_idx - 1) // M
            box_c = (col_idx - 1) // M
            box_id = (box_r * M) + box_c + 1

            fact_str = f"(cell (row {row_idx}) (col {col_idx}) (box {box_id}) (val {val}))"
            env.assert_string(fact_str)

    # 4. Ejecutar el Motor
    env.run()

    # 5. Recoger resultados (CORREGIDO)
    result_grid = [[0] * N for _ in range(N)]
    is_solved = True

    # Iteramos sobre TODOS los hechos en memoria
    for fact in env.facts():
        # Verificamos si el hecho pertenece al template 'cell'
        if fact.template.name == "cell":
            r = fact["row"] - 1
            c = fact["col"] - 1
            v = fact["val"]
            result_grid[r][c] = v
            if v == 0:
                is_solved = False

    print("\n" + "=" * 50)
    if is_solved:
        print(f"✅ Sudoku {N}x{N} Resuelto con CLIPS:")
    else:
        print("⚠️ Sudoku incompleto (CLIPS se atascó sin adivinar):")

    for i in range(N):
        row_str = ""
        for j in range(N):
            val = result_grid[i][j]
            row_str += str(val).ljust(2) + " "
        print(row_str)


if __name__ == "__main__":
    # Asegúrate de tener input.txt
    solve_sudoku_clips("input2.txt")
