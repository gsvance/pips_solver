"""Spaces are the individual half-domino squares that make up a Pips board."""

from dataclasses import dataclass
from typing import Final, Self


# The topmost row on a Pips board is always row 1. The leftmost column is
# always column 1.
TOPMOST_ROW: Final[int] = 1
LEFTMOST_COLUMN: Final[int] = 1


@dataclass(order=True, frozen=True, slots=True)
class Space:
    """Row and column coordinates for one space on a Pips board."""
    r: int  # Row number
    c: int  # Column number

    def __init__(self, r: int, c: int, *, unchecked: bool = False) -> None:
        if not unchecked:
            if r < TOPMOST_ROW:
                raise ValueError(
                    f'row number cannot be less than {TOPMOST_ROW}'
                )
            if c < LEFTMOST_COLUMN:
                raise ValueError(
                    f'column number cannot be less than {LEFTMOST_COLUMN}'
                )
        object.__setattr__(self, 'r', r)
        object.__setattr__(self, 'c', c)

    def __str__(self) -> str:
        return f'{self.r},{self.c}'

    def shift_by(
        self, *, delta_r: int | None = None, delta_c: int | None = None,
    ) -> Self:
        """Return another space shifted by some number of rows or columns."""
        if delta_r is None and delta_c is None:
            raise TypeError('must specify at least one of delta_r or delta_c')
        new_r = self.r if delta_r is None else self.r + delta_r
        new_c = self.c if delta_c is None else self.c + delta_c
        return self.__class__(new_r, new_c, unchecked=True)


def parse_board_layout(board_layout_string: str) -> dict[Space, str]:
    """Process an ASCII layout of a Pips board and return a dict of spaces."""
    # Note that we *do not* strip any whitespace here because the board layout
    # string could contain leading spaces that ensure correct alignment of the
    # columns on the Pips board.
    board_layout_lines = board_layout_string.splitlines()

    spaces: dict[Space, str] = {}
    for r, line in enumerate(board_layout_lines, start=TOPMOST_ROW):
        for c, char in enumerate(line, start=LEFTMOST_COLUMN):
            if char.isspace():
                continue
            assert len(char) == 1
            space = Space(r, c)
            assert space not in spaces
            spaces[space] = char

    # Shift the space coordinates mathematically to remove any empty top rows
    # or empty left columns if either of those exist.
    r_min = min(space.r for space in spaces)
    c_min = min(space.c for space in spaces)
    if r_min != TOPMOST_ROW or c_min != LEFTMOST_COLUMN:
        delta_r = TOPMOST_ROW - r_min
        delta_c = LEFTMOST_COLUMN - c_min
        spaces = {
            space.shift_by(delta_r=delta_r, delta_c=delta_c): char
            for (space, char) in spaces.items()
        }

    return spaces
