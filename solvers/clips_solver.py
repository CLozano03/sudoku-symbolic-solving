import math
import os
import tempfile

import clips

# =============================================================================
# CLIPS LOGIC (Rules & Templates)
# =============================================================================
CLIPS_SOURCE = """
;; --- TEMPLATES ---

(deftemplate grid-info
   (slot n)
   (slot m))

(deftemplate cell
   (slot row)
   (slot col)
   (slot box)
   (slot val))

(deftemplate possible
   (slot row)
   (slot col)
   (slot box)
   (slot val))

;; --- RULES ---

;; 1. Generate Candidates
(defrule generate-candidates
   (grid-info (n ?n))
   (cell (row ?r) (col ?c) (box ?b) (val 0))
   =>
   (loop-for-count (?v 1 ?n) do
      (assert (possible (row ?r) (col ?c) (box ?b) (val ?v)))
   )
)

;; 2. Prune Row
(defrule prune-row
   (cell (row ?r) (val ?v&~0))
   ?f <- (possible (row ?r) (val ?v))
   =>
   (retract ?f))

;; 3. Prune Column
(defrule prune-col
   (cell (col ?c) (val ?v&~0))
   ?f <- (possible (col ?c) (val ?v))
   =>
   (retract ?f))

;; 4. Prune Box
(defrule prune-box
   (cell (box ?b) (val ?v&~0))
   ?f <- (possible (box ?b) (val ?v))
   =>
   (retract ?f))

;; 5. Naked Single
(defrule single-candidate-assign
   ?f <- (possible (row ?r) (col ?c) (val ?v))
   (not (possible (row ?r) (col ?c) (val ?v2&~?v)))
   ?c-fact <- (cell (row ?r) (col ?c) (val 0))
   =>
   (modify ?c-fact (val ?v))
   (retract ?f)
)
"""


def solve(grid):
    """
    Attempts to solve a Sudoku (N x N) using CLIPS Expert System rules.
    Returns the modified grid IN-PLACE.
    """
    N = len(grid)
    M = int(math.sqrt(N))

    # Validation
    if M * M != N:
        print(f"CLIPS Error: Grid size {N}x{N} is not a perfect square.")
        return None

    env = clips.Environment()
    temp_file_path = ""

    try:
        # 1. Write CLIPS rules to a temporary file
        # We use 'delete=False' so we can close it and let CLIPS open it by name
        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".clp", delete=False
        ) as tmp:
            tmp.write(CLIPS_SOURCE)
            temp_file_path = tmp.name

        # 2. Load the rules from the file
        # This handles multiple rules/templates correctly
        env.load(temp_file_path)

        # 3. Assert Initial Facts
        env.assert_string(f"(grid-info (n {N}) (m {M}))")

        for i in range(N):
            for j in range(N):
                val = grid[i][j]
                row_idx = i + 1
                col_idx = j + 1

                # Calculate Box ID
                box_r = (row_idx - 1) // M
                box_c = (col_idx - 1) // M
                box_id = (box_r * M) + box_c + 1

                env.assert_string(
                    f"(cell (row {row_idx}) (col {col_idx}) (box {box_id}) (val {val}))"
                )

        # 4. Run the engine
        env.run()

        # 5. Retrieve Results
        solved_count = 0
        for fact in env.facts():
            if fact.template.name == "cell":
                r = fact["row"] - 1
                c = fact["col"] - 1
                v = fact["val"]

                grid[r][c] = v  # Update IN-PLACE

                if v != 0:
                    solved_count += 1

        if solved_count == N * N:
            return grid
        else:
            print(
                f"Warning: CLIPS stuck. Solved cells: {solved_count}/{N * N}"
            )
            return grid

    except clips.CLIPSError as e:
        print(f"CLIPS Error: {e}")
        return None
    except Exception as e:
        print(f"General Error: {e}")
        return None
    finally:
        # Cleanup
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
