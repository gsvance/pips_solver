"""Fundamental data classes representing some basic ideas from Pips."""

from collections.abc import Iterator
import dataclasses
from typing import Final, Self


TOPMOST_ROW: Final[int] = 1
LEFTMOST_COLUMN: Final[int] = 1


@dataclasses.dataclass(order=True, frozen=True, slots=True)
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
    # columns on the Pips board
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
    # or empty left columns if either of those exist
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


MIN_DOTS: Final[int] = 0
MAX_DOTS: Final[int] = 6


@dataclasses.dataclass(frozen=True, match_args=False, slots=True)
class Domino:
    """A single Pips domino piece with two associated dots values."""
    dots: tuple[int, int]

    # Internally, the two dots values are always stored in sorted order, but I
    # want to remember the order they were input for user-friendliness reasons
    flip_dots: bool = dataclasses.field(init=False, repr=False, compare=False)

    def __init__(self, dots_1: int, dots_2: int, /) -> None:
        flip_dots = dots_1 > dots_2
        if flip_dots:
            dots_1, dots_2 = dots_2, dots_1
        if not MIN_DOTS <= dots_1 <= dots_2 <= MAX_DOTS:
            raise ValueError(
                f'domino dots values must range from {MIN_DOTS} to {MAX_DOTS}'
            )
        object.__setattr__(self, 'dots', (dots_1, dots_2))
        object.__setattr__(self, 'flip_dots', flip_dots)

    @classmethod
    def parse(cls, domino_string: str) -> Self:
        """Parse a terse two-digit string representation of a domino."""
        digit_1, digit_2 = domino_string.strip()
        return cls(int(digit_1), int(digit_2))

    def __iter__(self) -> Iterator[int]:
        if self.flip_dots:
            return reversed(self.dots)
        return iter(self.dots)

    def __len__(self) -> int:
        return len(self.dots)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{tuple(self)!r}'

    def __str__(self) -> str:
        return '|'.join(map(str, self))


def parse_dominoes(dominoes_string: str) -> list[Domino]:
    """Parse many domino strings separated by whitespace and return a list."""
    return list(map(Domino.parse, dominoes_string.strip().split()))
