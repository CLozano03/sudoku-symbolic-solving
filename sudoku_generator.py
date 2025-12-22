import os
import random


def generate_sudoku_16x16():
    base = 5
    side = base * base

    def pattern(r, c):
        return (base * (r % base) + r // base + c) % side

    def shuffle(s):
        return random.sample(s, len(s))

    r_base = range(base)
    rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
    cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
    nums = shuffle(range(1, side + 1))

    board = [[nums[pattern(r, c)] for c in cols] for r in rows]

    total_cells = side * side
    cells_to_keep = random.randint(
        int(total_cells * 0.35), int(total_cells * 0.45)
    )

    indices = list(range(total_cells))
    random.shuffle(indices)
    cells_to_remove = indices[: (total_cells - cells_to_keep)]

    for idx in cells_to_remove:
        r, c = divmod(idx, side)
        board[r][c] = 0

    return board


def save_sudokus(count=5, directory="solvers/16x16"):
    if not os.path.exists(directory):
        os.makedirs(directory)

    for i in range(1, count + 1):
        filename = f"in{str(i).zfill(2)}.txt"
        filepath = os.path.join(directory, filename)

        board = generate_sudoku_16x16()

        with open(filepath, "w") as f:
            for row in board:
                line = " ".join(map(str, row))
                f.write(line + "\n")

    print(f"{count} Sudoku puzzles saved in '{directory}' directory.")


if __name__ == "__main__":
    save_sudokus(count=5, directory="sudokus/25x25")
