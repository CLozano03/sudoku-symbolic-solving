import ast
import math
import os
import subprocess


def solve(grid):
    n = len(grid)
    sub_n = int(math.sqrt(n))
    grid_str = str(grid)

    picat_code = f"""
import cp.

main =>
    Input = {grid_str},
    N = {n},
    SubN = {sub_n},


    Sol = [new_list(N) : _ in 1..N],
    SolVars = vars(Sol),
    SolVars :: 1..N,

    foreach(R in 1..N, C in 1..N)
        if Input[R,C] > 0 then
            Sol[R,C] #= Input[R,C]
        end
    end,

    % Constraints
    foreach(Row in Sol) all_different(Row) end,
    foreach(C in 1..N) all_different([Sol[R,C] : R in 1..N]) end,
    foreach(R in 1..SubN..N, C in 1..SubN..N)
        all_different([Sol[I,J] : I in R..R+SubN-1, J in C..C+SubN-1])
    end,

    % Heuristic: first-fail
    if solve([ff], SolVars) then
        printf("%w", Sol)
    else
        printf("FAIL")
    end.
"""
    filename = "temp_solver.pi"
    with open(filename, "w") as f:
        f.write(picat_code)

    try:
        result = subprocess.run(
            ["picat", filename], capture_output=True, text=True
        )
        output = result.stdout.strip()

        if not output or "FAIL" in output or result.returncode != 0:
            return None

        solved_grid = ast.literal_eval(output)

        for i in range(n):
            for j in range(n):
                grid[i][j] = solved_grid[i][j]
        return grid

    except Exception:
        return None
    finally:
        if os.path.exists(filename):
            os.remove(filename)
