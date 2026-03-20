#!/usr/bin/env python3
"""The simplest CLI interface to interact with the Pips solver codebase.

Pass in the name of a puzzle file as the first argument and the script will
print instructions for how to place dominoes in order to solve it.
"""

from pathlib import Path
import sys

from pips_ilp import formulate_ilp
from puzzle import Puzzle


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

    solution = puzzle_ilp.solve(msg=True)
    if solution is None:
        print('ERROR: ILP MODEL FAILED TO SOLVE OPTIMALLY')
        return

    print()
    print('Solution Instructions:')
    for domino, spot in solution:
        (dot_1, dot_2), (space_1, space_2) = domino, spot
        domino_str = '[' + '|'.join(str(domino)) + ']'
        if spot.is_horizontal():
            print(
                f'Place {domino_str} in row {space_1.r}',
                f'with [{dot_1}| in column {space_1.c}',
                f'and |{dot_2}] in column {space_2.c}',
            )
        else:  # The spot is vertical
            print(
                f'Place {domino_str} in column {space_1.c}',
                f'with [{dot_1}| in row {space_1.r}',
                f'and |{dot_2}] in row {space_2.r}',
            )
    print()


if __name__ == '__main__':
    _, arg_1 = sys.argv
    main(Path(arg_1))
