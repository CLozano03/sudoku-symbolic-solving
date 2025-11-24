from ortools.sat.python import cp_model
import numpy as np
import math

def read_sudoku_from_file_nxn(filename):
    """
    Lee la cuadrícula inicial de Sudoku desde un archivo de texto para un tamaño N x N.
    
    Determina N automáticamente a partir del número de filas y columnas.
    """
    grid = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                # Intenta extraer todos los números y '0' de la línea
                row = [int(n) for n in line.split() if n.isdigit() or (n.strip() == '0')]
                if row:
                    grid.append(row)
        
        if not grid:
            raise ValueError("El archivo está vacío o no contiene datos válidos.")
            
        N = len(grid)
        if N != len(grid[0]):
            raise ValueError(f"La cuadrícula debe ser cuadrada (N x N). Se encontró {N} filas y {len(grid[0])} columnas.")

        # Verificar que N sea un cuadrado perfecto para que exista una subcuadrícula M x M
        M = int(math.sqrt(N))
        if M * M != N:
            raise ValueError(f"El tamaño de la cuadrícula N={N} no permite una subcuadrícula M x M (N debe ser un cuadrado perfecto).")

        return grid, N, M
        
    except FileNotFoundError:
        print(f"❌ Error: Archivo '{filename}' no encontrado.")
        return None, None, None
    except ValueError as e:
        print(f"❌ Error de formato en el archivo: {e}")
        return None, None, None

def solve_sudoku_nxn(filename):
    """
    Resuelve un Sudoku de tamaño N x N utilizando Google OR-Tools (CP-SAT Solver).
    """
    
    # 1. Leer el Sudoku y determinar N (tamaño de la cuadrícula) y M (tamaño de la subcuadrícula)
    initial_grid, N, M = read_sudoku_from_file_nxn(filename)
    
    if initial_grid is None:
        return

    # Rango de valores para las variables (1 a N)
    value_range = N 
    
    # 2. Crear el modelo de CP-SAT
    model = cp_model.CpModel()

    # 3. Definir las variables de decisión: cada celda (i, j) es una variable en [1, N]
    grid_vars = {}
    for i in range(N):
        for j in range(N):
            # La variable tendrá valores de 1 a N (ej. 1 a 9 para 9x9, 1 a 16 para 16x16)
            grid_vars[i, j] = model.NewIntVar(1, value_range, f'cell_{i}_{j}')

    # 4. Aplicar las Restricciones GENERALIZADAS

    # Restricción A: Todas las celdas en cada fila deben ser diferentes.
    for i in range(N):
        row_vars = [grid_vars[i, j] for j in range(N)]
        model.AddAllDifferent(row_vars)

    # Restricción B: Todas las celdas en cada columna deben ser diferentes.
    for j in range(N):
        col_vars = [grid_vars[i, j] for i in range(N)]
        model.AddAllDifferent(col_vars)

    # Restricción C: Todas las celdas en cada subcuadrícula de M x M deben ser diferentes.
    for box_row_start in range(0, N, M):
        for box_col_start in range(0, N, M):
            box_vars = []
            for i in range(M):
                for j in range(M):
                    row = box_row_start + i
                    col = box_col_start + j
                    box_vars.append(grid_vars[row, col])
            model.AddAllDifferent(box_vars)
            
    # Restricción D: Imponer los valores iniciales (leídos del archivo)
    print(f"Sudoku inicial cargado (Tamaño {N}x{N}):")
    for i in range(N):
        for j in range(N):
            if initial_grid[i][j] != 0:
                model.Add(grid_vars[i, j] == initial_grid[i][j])
        print(" ".join(map(str, initial_grid[i])))


    # 5. Crear el Solucionador (Solver) y Resolver
    solver = cp_model.CpSolver()
    # solver.parameters.log_search_progress = True # Puedes descomentar para ver el progreso

    status = solver.Solve(model)

    # 6. Mostrar el resultado
    print("\n" + "="*50)
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"✅ Sudoku {N}x{N} Resuelto con éxito:")
        
        for i in range(N):
            row_str = ""
            for j in range(N):
                value = solver.Value(grid_vars[i, j])
                row_str += str(value).ljust(2) + " " # Usar ljust para alinear números de doble dígito (ej. 16)
            print(row_str)
        
    elif status == cp_model.INFEASIBLE:
        print("❌ No se encontró solución. El Sudoku es imposible o está mal modelado.")
    else:
        print("⚠️ Error o el problema no fue resuelto a un estado final.")

if __name__ == '__main__':
    # Usar el nombre de archivo con tu entrada (ejemplo 9x9)
    # Crea un archivo llamado 'sudoku_puzzle_nxn.txt' con tu entrada
    solve_sudoku_nxn("s2.txt")