# sudoku_optapy.py
import sys
from typing import List, Optional
from optapy import (
    planning_entity,
    planning_id,
    planning_variable,
    planning_solution,
    problem_fact_collection_property,
    value_range_provider,
    planning_entity_collection_property,
    planning_score,
    problem_fact,
)
from optapy import solver_factory_create
from optapy.types import SolverConfig, Duration, HardSoftScore
from optapy import constraint_provider
from optapy.types import Joiners

# ---------- Domain classes----------

@problem_fact
class Value:
    def __init__(self, v: int): self.v = v
    def __repr__(self): return f"Value({self.v})"

@planning_entity
class Cell:
    def __init__(self, id: int, row: int, col: int, initial_value: int = None, value: Value = None):
        self.id, self.row, self.col, self.initial_value, self.value = id, row, col, initial_value, value
    @planning_id
    def get_id(self): return self.id
    @planning_variable(Value, value_range_provider_refs=["valueRange"])
    def get_value(self): return self.value
    def set_value(self, new_value): self.value = new_value
    def block_index(self): return (self.row // 3) * 3 + (self.col // 3)
    def __repr__(self):
        iv = self.initial_value if self.initial_value is not None else "."
        vv = self.value.v if self.value is not None else "."
        return f"Cell({self.row},{self.col},init={iv},val={vv})"

@planning_solution
class Sudoku:
    def __init__(self, value_list, cell_list, score=None):
        self.value_list, self.cell_list, self.score = value_list, cell_list, score
    @problem_fact_collection_property(Value)
    @value_range_provider(range_id="valueRange")
    def get_value_list(self): return self.value_list
    @planning_entity_collection_property(Cell)
    def get_cell_list(self): return self.cell_list
    @planning_score(HardSoftScore)
    def get_score(self): return self.score
    def set_score(self, score): self.score = score

# ---------- Constraints----------

@constraint_provider
def define_constraints(constraint_factory):
    return [
        fixed_cells_must_keep_value(constraint_factory),
        row_conflict(constraint_factory),
        column_conflict(constraint_factory),
        block_conflict(constraint_factory),
    ]

def fixed_cells_must_keep_value(constraint_factory):
    return (
        constraint_factory.for_each(Cell)
        .filter(lambda c: c.initial_value is not None)
        .filter(lambda c: c.get_value() is None or c.get_value().v != c.initial_value)
        .penalize("Fixed cell changed", HardSoftScore.ONE_HARD)
    )

def row_conflict(constraint_factory):
    return (
        constraint_factory.for_each_unique_pair(Cell,
            Joiners.equal(lambda c: c.row),
            Joiners.equal(lambda c: c.get_value().v if c.get_value() is not None else None)
        )
        .penalize("Row conflict", HardSoftScore.ONE_HARD)
    )

def column_conflict(constraint_factory):
    return (
        constraint_factory.for_each_unique_pair(Cell,
            Joiners.equal(lambda c: c.col),
            Joiners.equal(lambda c: c.get_value().v if c.get_value() is not None else None)
        )
        .penalize("Column conflict", HardSoftScore.ONE_HARD)
    )

def block_conflict(constraint_factory):
    return (
        constraint_factory.for_each_unique_pair(Cell,
            Joiners.equal(lambda c: c.block_index()),
            Joiners.equal(lambda c: c.get_value().v if c.get_value() is not None else None)
        )
        .penalize("Block conflict", HardSoftScore.ONE_HARD)
    )

# ---------- Helper----------

def build_sudoku_from_matrix(matrix):
    # (Se mantiene la lógica para construir el modelo a partir de la matriz)
    values = [Value(i) for i in range(1, 10)]
    cells = []
    cid = 0
    for r in range(9):
        for c in range(9):
            iv = matrix[r][c]
            assigned_value = next((v for v in values if v.v == iv), None)
            cell = Cell(id=cid, row=r, col=c, initial_value=(iv if iv != 0 else None), value=assigned_value)
            cells.append(cell)
            cid += 1

    return Sudoku(value_list=values, cell_list=cells)


def solve(grid: List[List[int]], seconds=10) -> Optional[Sudoku]:
    # Build the Sudoku model from the provided grid
    sudoku = build_sudoku_from_matrix(grid)
    
    # Configure the solver
    solver_config = (
        SolverConfig()
        .withEntityClasses(Cell)
        .withSolutionClass(Sudoku)
        .withConstraintProviderClass(define_constraints)
        .withTerminationSpentLimit(Duration.ofSeconds(seconds))
    )
    
    # Create the solver and solve the Sudoku
    solver = solver_factory_create(solver_config).buildSolver()
    solution = solver.solve(sudoku)

    if solution.get_score().getHardScore() == 0:
        return solution
    else:
        print(f"\n Falló la resolución: HardScore final {solution.get_score().getHardScore()}. Tiempo insuficiente.")
        return None

