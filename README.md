<div align="center">
    <h1>Sudoku symbolic solving</h1>
</div>


This repository contains a practical assignment for the **Reasoning Models** course (Master in Artificial Intelligence, UPM). The project explores and compares different **symbolic reasoning** techniques for automatic Sudoku solving.

The main objective is to perform a *benchmark* (performance comparison) between different solving paradigms, such as Constraint Programming (CP), Satisfiability (SAT), SMT, and Logic Programming.

## :brain: Implemented Solvers

The system integrates several resolution engines, each in its own module within `solvers/`:

*   **Google OR-Tools**: Uses constraint programming (CP-SAT) to efficiently model the Sudoku.
*   **PySAT (Glucose4)**: Reduces the problem to a boolean formula (CNF) and uses a modern SAT solver.
*   **Z3 Solver**: Models the problem using SMT (Satisfiability Modulo Theories) theorems.
*   **Prolog (via PySwip)**: Uses predicate logic and Prolog's native backtracking.
*   **CLIPS** *(Experimental)*: Approach based on production systems and rules.

## :file_folder: Project Structure

*   `main.py`: **Entry point**. Runs the test battery, validates solutions, and displays a comparative table with execution times.
*   `solvers/`: Package containing the implementation of each solver.
*   `sudokus/`: Folder containing input files (`.txt`). Each file contains a Sudoku represented by numbers (0 or `.` for empty cells).
*   `requirements.txt`: List of project dependencies.

## :wrench: Requirements

To run this project you will need **Python 3.x** and the following libraries (depending on the solvers you want to test):

```bash
pip install -r requirements.txt
```

> **Note for Prolog:** `pyswip` requires **SWI-Prolog** to be installed on your operating system and accessible in the PATH.

## :rocket: Usage

1.  Clone the repository or download the code.
2.  Ensure the `sudokus/` folder contains the test files.
3.  Run the main script:

```bash
python main.py
```

The script will automatically detect available solvers (if a library is missing, it will simply skip that solver or show a controlled error) and process all puzzles.

### Example Results

Upon completion, you will see a ranking table similar to this:

```text
=====================================================================================
RANK  | SOLVER               | SOLVED   | AVG TIME (s) | MIN (s)  | MAX (s) 
=====================================================================================
1     | Google OR-Tools      | 50/50    | 0.0035       | 0.0020   | 0.0100  
2     | PySAT (Glucose4)     | 50/50    | 0.0048       | 0.0031   | 0.0120  
3     | Z3 Solver            | 50/50    | 0.0150       | 0.0100   | 0.0500  
...
=====================================================================================
Total sudokus processed: 50
```

## :memo: Additional Notes

*   The internal validator (`check_correct` in `main.py`) ensures that each solution complies with standard Sudoku rules (unique rows, columns, and blocks).
*   The project is designed to be modular: it is easy to add a new solver by implementing a class/module with a `solve(grid)` method.
