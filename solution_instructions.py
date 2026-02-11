#!/usr/bin/env python3
"""The simplest CLI interface to interact with the Pips solver codebase.

Pass in the name of a puzzle file as the first argument and the script will
print instructions for how to place dominoes in order to solve it.
"""

from pathlib import Path
import sys

import pulp as pl

from pips_ilp import formulate_ilp
from puzzle import Puzzle


def get_binary_value(var: pl.LpVariable) -> int:
    """Extract the value of a PuLP variable that is expected to be binary."""
    float_value = pl.value(var)
    assert isinstance(float_value, float)
    int_value = round(float_value)
    assert int_value in (0, 1)
    return int_value


def main(puzzle_file: Path) -> None:
    """Read, solve, and print instructions for a single Pips puzzle file."""
    print()
    puzzle_text = puzzle_file.read_text(encoding='ascii')
    print(f'Opened Pips puzzle file: {puzzle_file!s}')
    puzzle = Puzzle.parse(puzzle_text)
    print(f'Parsed Pips puzzle: {puzzle!r}')
    puzzle_ilp = formulate_ilp(puzzle)
    print('Formulated PuLP ILP. Solving...')
    print()

    puzzle_ilp.problem.solve()
    if pl.LpStatus[puzzle_ilp.problem.status] != 'Optimal':
        print('ERROR: ILP MODEL FAILED TO SOLVE OPTIMALLY')
        return

    print('Solution Instructions:')
    for (domino, spot), placement_var in puzzle_ilp.placement_vars.items():
        if get_binary_value(placement_var) == 0:
            continue
        dot_1, dot_2 = domino
        space_1, space_2 = spot
        if space_1.r == space_2.r:
            print(
                f'Place [{domino!s}] in row {space_1.r}',
                f'with [{dot_1}] in column {space_1.c}',
                f'and [{dot_2}] in column {space_2.c}',
            )
        elif space_1.c == space_2.c:
            print(
                f'Place [{domino!s}] in column {space_1.c}',
                f'with [{dot_1}] in row {space_1.r}',
                f'and [{dot_2}] in row {space_2.r}',
            )
        else:
            assert False, f'invalid spot: {spot!r}'
    print()


if __name__ == '__main__':
    _, arg_1 = sys.argv
    main(Path(arg_1))
