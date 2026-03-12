#!/usr/bin/env python3
"""See Pips solutions visualized in the terminal using unicode box characters.

Pass in the name of a puzzle file as the first argument and this script will
print a textual visualization of a domino arrangement that solves the puzzle.
"""

from pathlib import Path
import sys
from typing import Final

from dominoes import Domino
from pips_ilp import formulate_ilp, Spot
from puzzle import Puzzle
from spaces import LEFTMOST_COLUMN, Space, TOPMOST_ROW


# Unicode visualization drawing options:
# Side length of half a domino, should be odd and no less than 3
SPACE_SIZE: Final[int] = 3
# Offset to use for the dots values
HALF_SIZE: Final[int] = SPACE_SIZE // 2
# How many extra blank spaces to add around the visualization
OUTER_BORDER: Final[int] = 1
# Full length of the long side of a domino
DOMINO_LENGTH: Final[int] = SPACE_SIZE * 2


# Characters for drawing dominoes: straight pieces
VERTICAL: Final[str] = chr(0x2502)
HORIZONTAL: Final[str] = chr(0x2500)

# Characters for drawing dominoes: corner pieces
UPPER_LEFT: Final[str] = chr(0x256d)
UPPER_RIGHT: Final[str] = chr(0x256e)
LOWER_LEFT: Final[str] = chr(0x2570)
LOWER_RIGHT: Final[str] = chr(0x256f)

# Characters for drawing dominoes: internal fillers
BLANK: Final[str] = ' '


def create_blank_grid(puzzle: Puzzle) -> list[list[str]]:
    """Create a blank grid of characters to be filled for the visualization."""
    grid_height = SPACE_SIZE * puzzle.num_rows + OUTER_BORDER * 2
    grid_width = SPACE_SIZE * puzzle.num_columns + OUTER_BORDER * 2
    grid: list[list[str]] = []
    for _y in range(grid_height):
        grid.append([])
        for _x in range(grid_width):
            grid[-1].append(BLANK)
    return grid


def transform_coordinates(space: Space) -> tuple[int, int]:
    """Transform a Pips space into coordinates for the character grid.

    The y and x values returned are the position where the space's dots value
    should be rendered.
    """
    zero_based_r = space.r - TOPMOST_ROW
    zero_based_c = space.c - LEFTMOST_COLUMN
    transform_slope = SPACE_SIZE
    transform_intercept = OUTER_BORDER + HALF_SIZE
    y = transform_slope * zero_based_r + transform_intercept
    x = transform_slope * zero_based_c + transform_intercept
    return y, x


def draw_domino(grid: list[list[str]], domino: Domino, spot: Spot) -> None:
    """Draw a domino in a given board spot on the character grid."""
    space_1, space_2 = spot
    y1, x1 = transform_coordinates(space_1)
    y2, x2 = transform_coordinates(space_2)

    y_top = min(y1, y2) - HALF_SIZE
    x_left = min(x1, x2) - HALF_SIZE
    height = SPACE_SIZE if spot.is_horizontal() else DOMINO_LENGTH
    width = SPACE_SIZE if spot.is_vertical() else DOMINO_LENGTH
    y_bottom = y_top + height - 1
    x_right = x_left + width - 1

    # Draw the domino dots values
    dot_1, dot_2 = domino
    grid[y1][x1] = str(dot_1)
    grid[y2][x2] = str(dot_2)

    # Draw the domino corners
    grid[y_top][x_left] = UPPER_LEFT
    grid[y_top][x_right] = UPPER_RIGHT
    grid[y_bottom][x_left] = LOWER_LEFT
    grid[y_bottom][x_right] = LOWER_RIGHT

    # Draw the straight domino edges
    if spot.is_horizontal():

        # Top and bottom edges of left half
        for i in range(1, SPACE_SIZE):
            grid[y_top][x_left + i] = HORIZONTAL
            grid[y_bottom][x_left + i] = HORIZONTAL

        # Top and bottom edges of right half
        for i in range(1, SPACE_SIZE):
            grid[y_top][x_right - i] = HORIZONTAL
            grid[y_bottom][x_right - i] = HORIZONTAL

        # Left and right edges
        for i in range(1, SPACE_SIZE - 1):
            grid[y_top + i][x_left] = VERTICAL
            grid[y_top + i][x_right] = VERTICAL

    else:  # The spot is vertical

        # Left and right edges of top half
        for i in range(1, SPACE_SIZE):
            grid[y_top + i][x_left] = VERTICAL
            grid[y_top + i][x_right] = VERTICAL

        # Left and right edges of bottom half
        for i in range(1, SPACE_SIZE):
            grid[y_bottom - i][x_left] = VERTICAL
            grid[y_bottom - i][x_right] = VERTICAL

        # Top and bottom edges
        for i in range(1, SPACE_SIZE - 1):
            grid[y_top][x_left + i] = HORIZONTAL
            grid[y_bottom][x_left + i] = HORIZONTAL


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

    solution = puzzle_ilp.solve()
    if solution is None:
        print('ERROR: ILP MODEL FAILED TO SOLVE OPTIMALLY')
        return

    grid = create_blank_grid(puzzle)
    for domino, spot in solution:
        draw_domino(grid, domino, spot)

    print('Solution Visualization:')
    print(*(''.join(grid_row).rstrip() for grid_row in grid), sep='\n')


if __name__ == '__main__':
    _, arg_1 = sys.argv
    main(Path(arg_1))
