"""A collection of Python types for representing parts of a Pips puzzle."""

import abc
from collections.abc import Iterable, Iterator
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


@dataclasses.dataclass(order=True, frozen=True, match_args=False, slots=True)
class Region:
    """A sorted frozen set containing one or more Pips board spaces."""
    spaces: tuple[Space, ...]

    def __init__(self, spaces: Iterable[Space]) -> None:
        spaces_tuple = tuple(sorted(spaces))
        if len(spaces_tuple) < 1:
            raise ValueError('region must contain at least one space')
        if len(frozenset(spaces_tuple)) < len(spaces_tuple):
            raise ValueError('spaces inside a region must be unique')
        object.__setattr__(self, 'spaces', spaces_tuple)
        self._check_connectedness()

    def __repr__(self) -> str:
        spaces_list = list(self.spaces)
        return f'{self.__class__.__name__}({spaces_list!r})'

    def __iter__(self) -> Iterator[Space]:
        return iter(self.spaces)

    def __len__(self) -> int:
        return len(self.spaces)

    def __contains__(self, space: Space) -> bool:
        return space in self.spaces

    def _check_connectedness(self) -> None:
        """Raise an error if the region's spaces are not connected together."""
        # The technique here is to use a breadth-first search (BFS) to explore
        # all the spaces starting with the first one. If we can eventually
        # reach all spaces by stepping to neighbors, then the region is
        # connected. If not, then we need to raise an error.
        visited: set[Space] = set()
        frontier: set[Space] = set()
        frontier.add(next(iter(self)))

        while len(frontier) > 0:
            space = frontier.pop()
            visited.add(space)

            neighbors = (
                space.shift_by(delta_r=+1), space.shift_by(delta_r=-1),
                space.shift_by(delta_c=+1), space.shift_by(delta_c=-1),
            )
            for neighbor in neighbors:
                if neighbor in self and neighbor not in visited:
                    frontier.add(neighbor)

        if len(visited) != len(self):
            raise ValueError('spaces in a region must all be connected')

    def overlaps_with(self, other: Self) -> bool:
        """Determine whether two regions have any spaces in common."""
        set_intersection = frozenset(self).intersection(other)
        return len(set_intersection) > 0


class Condition(abc.ABC):
    """Abstract base class for any condition on a region of a Pips board."""

    @classmethod
    @abc.abstractmethod
    def maybe_parse(cls, condition_string: str) -> Self | None:
        """Parse a condition string if it is valid. Otherwise, return None."""

    @abc.abstractmethod
    def as_terse_string(self) -> str:
        """Generate a terse condition string representing this condition."""


@dataclasses.dataclass(frozen=True, slots=True)
class Number(Condition):
    """The Pips condition where dots must add up to a certain number."""
    number: int

    def __post_init__(self) -> None:
        if self.number < 0:
            raise ValueError('number condition cannot have a negative number')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.number})'

    @classmethod
    def maybe_parse(cls, condition_string: str) -> Self | None:
        try:
            return cls(int(condition_string.strip()))
        except ValueError:
            return None

    def as_terse_string(self) -> str:
        return str(self.number)


EQUAL_SYMBOL: Final[str] = '='


@dataclasses.dataclass(frozen=True, slots=True)
class Equal(Condition):
    """The Pips condition where dots must all be equal."""

    @classmethod
    def maybe_parse(cls, condition_string: str) -> Self | None:
        if condition_string.strip() == EQUAL_SYMBOL:
            return cls()
        return None

    def as_terse_string(self) -> str:
        return EQUAL_SYMBOL


NOT_EQUAL_SYMBOL: Final[str] = '=/='


@dataclasses.dataclass(frozen=True, slots=True)
class NotEqual(Condition):
    """The Pips condition where dots must all be different."""

    @classmethod
    def maybe_parse(cls, condition_string: str) -> Self | None:
        if condition_string.strip() == NOT_EQUAL_SYMBOL:
            return cls()
        return None

    def as_terse_string(self) -> str:
        return NOT_EQUAL_SYMBOL


GREATER_THAN_PREFIX: Final[str] = '>'


@dataclasses.dataclass(frozen=True, slots=True)
class GreaterThan(Condition):
    """The Pips condition where dots must sum to more than some number."""
    number: int

    def __post_init__(self) -> None:
        if self.number < 0:
            raise ValueError(
                'greater than condition cannot have a negative number'
            )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.number})'

    @classmethod
    def maybe_parse(cls, condition_string: str) -> Self | None:
        trimmed_string = condition_string.strip()
        if not trimmed_string.startswith(GREATER_THAN_PREFIX):
            return None
        number_string = trimmed_string.removeprefix(GREATER_THAN_PREFIX)
        if not number_string.isdigit():
            return None
        try:
            return cls(int(number_string))
        except ValueError:
            return None

    def as_terse_string(self) -> str:
        return f'{GREATER_THAN_PREFIX}{self.number}'


LESS_THAN_PREFIX: Final[str] = '<'


@dataclasses.dataclass(frozen=True, slots=True)
class LessThan(Condition):
    """The Pips condition where dots must sum to less than some number."""
    number: int

    def __post_init__(self) -> None:
        if self.number <= 0:
            raise ValueError('less than condition must have a positive number')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.number})'

    @classmethod
    def maybe_parse(cls, condition_string: str) -> Self | None:
        trimmed_string = condition_string.strip()
        if not trimmed_string.startswith(LESS_THAN_PREFIX):
            return None
        number_string = trimmed_string.removeprefix(LESS_THAN_PREFIX)
        if not number_string.isdigit():
            return None
        try:
            return cls(int(number_string))
        except ValueError:
            return None

    def as_terse_string(self) -> str:
        return f'{LESS_THAN_PREFIX}{self.number}'


CONDITION_TYPES: Final[list[type[Condition]]] = [
    Number, Equal, NotEqual, GreaterThan, LessThan,
]


def parse_condition(condition_string: str) -> Condition:
    """Parse a terse string representation of any Pips region condition."""
    for ConditionType in CONDITION_TYPES:
        condition = ConditionType.maybe_parse(condition_string)
        if condition is not None:
            return condition
    raise ValueError(f'invalid terse condition string: {condition_string!r}')


def parse_region_conditions(
    region_conditions_string: str,
) -> dict[str, Condition]:
    """Process an ASCII string of Pips region conditions and return a dict."""
    conditions: dict[str, Condition] = {}
    for line in region_conditions_string.strip().splitlines():
        char, condition_string = line.strip().split()
        if len(char) != 1:
            raise ValueError(
                f'region must be identified by one character, not {char!r}'
            )
        if char in conditions:
            raise ValueError(f'multiple conditions for region {char!r}')
        conditions[char] = parse_condition(condition_string)
    return conditions


class Board:
    """The game board for a Pips puzzle including the region conditions."""

    __slots__ = ('spaces', 'regions')

    def __init__(self) -> None:
        """Create an empty Pips board with no spaces or region conditions."""
        self.spaces: set[Space] = set()
        self.regions: dict[Region, Condition] = {}

    def add_space(self, space: Space) -> None:
        """Add one new space to the Pips board."""
        if space in self.spaces:
            raise ValueError('that space is already on the board')
        self.spaces.add(space)

    def add_region_with_condition(
        self, region: Region, condition: Condition,
    ) -> None:
        """Add one region to the Pips board with an attached condition."""
        for existing_region in self.regions:
            if region.overlaps_with(existing_region):
                raise ValueError(
                    'condition regions on the board may not overlap'
                )
        self.regions[region] = condition

    @classmethod
    def parse(cls, board_string: str) -> Self:
        """Set up a board by parsing strings for its layout and conditions."""
        board_layout_string, region_conditions_string = (
            board_string.rstrip().rsplit('\n\n', maxsplit=1)
        )

        spaces = parse_board_layout(board_layout_string)
        conditions = parse_region_conditions(region_conditions_string)

        space_chars = frozenset(spaces.values())
        for char in conditions:
            if char not in space_chars:
                raise ValueError(
                    f'region {char!r} has a condition but no board spaces'
                )
        del space_chars

        board = cls()
        for space in spaces:
            board.add_space(space)
        for condition_char, condition in conditions.items():
            region = Region(
                space for space, space_char in spaces.items()
                if space_char == condition_char
            )
            board.add_region_with_condition(region, condition)
        return board

    @property
    def num_spaces(self) -> int:
        """The total number of spaces on the board."""
        return len(self.spaces)

    @property
    def num_regions(self) -> int:
        """The total number of regions on the board."""
        return len(self.regions)

    def iter_sorted_spaces(self) -> Iterator[Space]:
        """Return an iterator over the board's spaces in sorted order."""
        return iter(sorted(self.spaces))

    def iter_sorted_regions(self) -> Iterator[Region]:
        """Return an iterator over the board's regions in sorted order."""
        return iter(sorted(self.regions.keys()))

    def get_condition(self, region: Region) -> Condition:
        """Return the condition associated with one of the board's regions."""
        return self.regions[region]

    def __contains__(self, space_or_region: Space | Region) -> bool:
        if isinstance(space_or_region, Space):
            return space_or_region in self.spaces
        if isinstance(space_or_region, Region):
            return space_or_region in self.regions
        return False

    def __repr__(self) -> str:
        return ''.join([
            '<',
            self.__class__.__name__,
            ' with ',
            f'{self.num_spaces} spaces',
            ' and ',
            f'{self.num_regions} regions',
            '>',
        ])


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


class Puzzle:
    """A full Pips puzzle made up of a game board and a list of dominoes."""

    __slots__ = ('board', 'dominoes')

    def __init__(self, board: Board, dominoes: list[Domino]) -> None:
        self.board: Board = board
        self.dominoes: list[Domino] = dominoes

        unique_dominoes = frozenset(self.dominoes)
        if len(unique_dominoes) < len(self.dominoes):
            raise ValueError('puzzle contains at least one duplicate domino')
        del unique_dominoes

        spaces_needed_for_dominoes = 0
        for domino in self.dominoes:
            spaces_needed_for_dominoes += len(domino)
        if spaces_needed_for_dominoes != self.board.num_spaces:
            raise ValueError(
                f'board has {self.board.num_spaces} spaces for dominoes, '
                + f'but needs {spaces_needed_for_dominoes}'
            )
        del spaces_needed_for_dominoes

    @classmethod
    def parse(cls, puzzle_string: str) -> Self:
        """Parse the contents of a Pips puzzle file as a board and dominoes."""
        board_string, dominoes_string = (
            puzzle_string.rstrip().rsplit('\n\n', maxsplit=1)
        )
        board = Board.parse(board_string)
        dominoes = parse_dominoes(dominoes_string)
        return cls(board, dominoes)

    @property
    def num_spaces(self) -> int:
        """The total number of spaces on the board."""
        return self.board.num_spaces

    @property
    def num_regions(self) -> int:
        """The total number of regions on the board."""
        return self.board.num_regions

    @property
    def num_dominoes(self) -> int:
        """The number of domino pieces for the puzzle."""
        return len(self.dominoes)

    def iter_sorted_spaces(self) -> Iterator[Space]:
        """Return an iterator over the board's spaces in sorted order."""
        return self.board.iter_sorted_spaces()

    def iter_sorted_regions(self) -> Iterator[Region]:
        """Return an iterator over the board's regions in sorted order."""
        return self.board.iter_sorted_regions()

    def get_condition(self, region: Region) -> Condition:
        """Return the condition associated with one of the board's regions."""
        return self.board.get_condition(region)

    def iter_dominoes(self) -> Iterator[Domino]:
        """Return an iterator over the puzzle's domino pieces."""
        return iter(self.dominoes)

    def __contains__(
        self, space_or_region_or_domino: Space | Region | Domino,
    ) -> bool:
        if isinstance(space_or_region_or_domino, (Space, Region)):
            return space_or_region_or_domino in self.board
        if isinstance(space_or_region_or_domino, Domino):
            return space_or_region_or_domino in self.dominoes
        return False

    def __repr__(self) -> str:
        return ''.join([
            '<',
            self.__class__.__name__,
            ' with ',
            f'{self.num_spaces} spaces',
            ', ',
            f'{self.num_regions} regions',
            ', and ',
            f'{self.num_dominoes} dominoes',
            '>',
        ])


if __name__ == '__main__':

    import sys
    from pathlib import Path

    _, arg_1 = sys.argv
    puzzle = Puzzle.parse(Path(arg_1).read_text(encoding='ascii'))

    print()
    print('Puzzle:', repr(puzzle))
    print('Board:', repr(puzzle.board))
    print()
    print('Dominoes:', *(puzzle.iter_dominoes()), sep='  ')
    print()
    print('Spaces:', *(puzzle.iter_sorted_spaces()), sep='  ')
    print()
    print('Regions:')
    for reg in puzzle.iter_sorted_regions():
        con = puzzle.get_condition(reg)
        print('    ', repr(con), '    ', repr(reg), sep='')
    print()
