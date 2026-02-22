#!/usr/bin/env python3
"""See Pips solutions visualized in the terminal using unicode boxes.

Pass in the name of a puzzle file as the first argument and the script will
print a textual visualization of a domino arrangement that solves the puzzle.
"""

from pathlib import Path
import sys
from typing import Final

import pulp as pl

from pips_ilp import formulate_ilp
from puzzle import Puzzle


# Box characters for drawing dominoes: straight pieces
VERTICAL: Final[str] = chr(0x2502)
HORIZONTAL: Final[str] = chr(0x2500)

# Box characters for drawing dominoes: corner pieces
UPPER_LEFT: Final[str] = chr(0x256d)
UPPER_RIGHT: Final[str] = chr(0x256e)
LOWER_LEFT: Final[str] = chr(0x2570)
LOWER_RIGHT: Final[str] = chr(0x256f)

# Box characters for drawing dominoes: tee pieces
TEE_VERTICAL_RIGHT: Final[str] = chr(0x251c)
TEE_VERTICAL_LEFT: Final[str] = chr(0x2524)
TEE_HORIZONTAL_DOWN: Final[str] = chr(0x252c)
TEE_HORIZONTAL_UP: Final[str] = chr(0x2534)

# Box characters for drawing dominoes: empty space
BLANK: Final[str] = ' '


def get_binary_value(var: pl.LpVariable) -> int:
    """Extract the value of a PuLP variable that is expected to be binary."""
    float_value = pl.value(var)
    assert isinstance(float_value, float)
    int_value = round(float_value)
    assert int_value in (0, 1)
    return int_value


def main(puzzle_file: Path) -> None:
    """Read, solve, and print a visual for a single Pips puzzle file."""
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

    min_r = min(space.r for space in puzzle.iter_sorted_spaces())
    max_r = max(space.r for space in puzzle.iter_sorted_spaces())
    min_c = min(space.c for space in puzzle.iter_sorted_spaces())
    max_c = max(space.c for space in puzzle.iter_sorted_spaces())

    grid = []
    for y in range((max_r - min_r + 1) * 3 + (max_r - min_r + 2) * 1):
        grid.append([])
        for x in range((max_c - min_c + 1) * 3 + (max_c - min_c + 2) * 1):
            grid[-1].append(BLANK)

    for (domino, spot), placement_var in puzzle_ilp.placement_vars.items():
        if get_binary_value(placement_var) == 0:
            continue
        dot_1, dot_2 = domino
        space_1, space_2 = spot
        y_1, x_1 = (space_1.r - 1) * 4 + 2, (space_1.c - 1) * 4 + 2
        y_2, x_2 = (space_2.r - 1) * 4 + 2, (space_2.c - 1) * 4 + 2
        grid[y_1][x_1] = str(dot_1)
        grid[y_2][x_2] = str(dot_2)
        grid[min(y_1, y_2) - 1][min(x_1, x_2) - 1] = UPPER_LEFT
        grid[min(y_1, y_2) - 1][max(x_1, x_2) + 1] = UPPER_RIGHT
        grid[max(y_1, y_2) + 1][min(x_1, x_2) - 1] = LOWER_LEFT
        grid[max(y_1, y_2) + 1][max(x_1, x_2) + 1] = LOWER_RIGHT
        if space_1.r == space_2.r:
            grid[y_1 - 1][min(x_1, x_2) + 0] = HORIZONTAL
            grid[y_1 - 1][min(x_1, x_2) + 1] = HORIZONTAL
            grid[y_1 - 1][min(x_1, x_2) + 2] = TEE_HORIZONTAL_DOWN
            grid[y_1 - 1][min(x_1, x_2) + 3] = HORIZONTAL
            grid[y_1 - 1][min(x_1, x_2) + 4] = HORIZONTAL
            grid[y_1][min(x_1, x_2) - 1] = VERTICAL
            grid[y_1][min(x_1, x_2) + 2] = VERTICAL
            grid[y_1][min(x_1, x_2) + 5] = VERTICAL
            grid[y_1 + 1][min(x_1, x_2) + 0] = HORIZONTAL
            grid[y_1 + 1][min(x_1, x_2) + 1] = HORIZONTAL
            grid[y_1 + 1][min(x_1, x_2) + 2] = TEE_HORIZONTAL_UP
            grid[y_1 + 1][min(x_1, x_2) + 3] = HORIZONTAL
            grid[y_1 + 1][min(x_1, x_2) + 4] = HORIZONTAL
        elif space_1.c == space_2.c:
            grid[min(y_1, y_2) + 0][x_1 - 1] = VERTICAL
            grid[min(y_1, y_2) + 1][x_1 - 1] = VERTICAL
            grid[min(y_1, y_2) + 2][x_1 - 1] = TEE_VERTICAL_RIGHT
            grid[min(y_1, y_2) + 3][x_1 - 1] = VERTICAL
            grid[min(y_1, y_2) + 4][x_1 - 1] = VERTICAL
            grid[min(y_1, y_2) - 1][x_1] = HORIZONTAL
            grid[min(y_1, y_2) + 2][x_1] = HORIZONTAL
            grid[min(y_1, y_2) + 5][x_1] = HORIZONTAL
            grid[min(y_1, y_2) + 0][x_1 + 1] = VERTICAL
            grid[min(y_1, y_2) + 1][x_1 + 1] = VERTICAL
            grid[min(y_1, y_2) + 2][x_1 + 1] = TEE_VERTICAL_LEFT
            grid[min(y_1, y_2) + 3][x_1 + 1] = VERTICAL
            grid[min(y_1, y_2) + 4][x_1 + 1] = VERTICAL
        else:
            assert False, f'invalid spot: {spot!r}'
    print()

    print('Solution Visualization:')
    for grid_row in grid:
        print(''.join(grid_row))


if __name__ == '__main__':
    _, arg_1 = sys.argv
    main(Path(arg_1))


"""print()

print(
    UPPER_LEFT, HORIZONTAL*2, TEE_HORIZONTAL_DOWN, HORIZONTAL*2, UPPER_RIGHT,
    ' '*2, '###|###', sep='',
)
print(
    VERTICAL, 3, BLANK, VERTICAL, BLANK, 5, VERTICAL,
    ' '*2, '###|###', sep='',
)
print(
    LOWER_LEFT, HORIZONTAL*2, TEE_HORIZONTAL_UP, HORIZONTAL*2, LOWER_RIGHT,
    ' '*2, '###|###', sep='',
)

print()

print(UPPER_LEFT, HORIZONTAL, UPPER_RIGHT, ' '*2, '###', sep='')
print(VERTICAL, 3, VERTICAL, ' '*2, '###', sep='')
print(VERTICAL, BLANK, VERTICAL, ' '*2, '###', sep='')
print(TEE_VERTICAL_RIGHT, HORIZONTAL, TEE_VERTICAL_LEFT, ' '*2, '---', sep='')
print(VERTICAL, BLANK, VERTICAL, ' '*2, '###', sep='')
print(VERTICAL, 5, VERTICAL, ' '*2, '###', sep='')
print(LOWER_LEFT, HORIZONTAL, LOWER_RIGHT, ' '*2, '###', sep='')

print()"""
