"""A Pips puzzle consists of dominoes, spaces, and regions with conditions."""

from collections.abc import Iterable, Iterator, Mapping
from typing import Self

from conditions import Condition, parse_condition
from dominoes import Domino, parse_dominoes
from regions import Region
from spaces import parse_board_layout, Space


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


class Puzzle:
    """A Pips puzzle including the game board parts and list of dominoes."""

    __slots__ = ('spaces', 'regions', 'dominoes')

    def __init__(
        self,
        spaces: Iterable[Space],
        regions: Mapping[Region, Condition],
        dominoes: Iterable[Domino],
    ) -> None:
        """Create a new Pips puzzle object using the given components."""
        self.spaces: set[Space] = set()
        self.regions: dict[Region, Condition] = {}
        self.dominoes: list[Domino] = []

        for space in spaces:
            self.add_space(space)
        for region, condition in regions.items():
            self.add_region_with_condition(region, condition)
        for domino in dominoes:
            self.dominoes.append(domino)

        unique_dominoes = frozenset(self.dominoes)
        if len(unique_dominoes) < len(self.dominoes):
            raise ValueError('puzzle contains at least one duplicate domino')
        del unique_dominoes

        spaces_needed_for_dominoes = 0
        for domino in self.dominoes:
            spaces_needed_for_dominoes += len(domino)
        if spaces_needed_for_dominoes != self.num_spaces:
            raise ValueError(
                f'puzzle has {self.num_spaces} spaces for dominoes, '
                + f'but needs {spaces_needed_for_dominoes}'
            )
        del spaces_needed_for_dominoes

    def add_space(self, space: Space) -> None:
        """Add one new space to the Pips puzzle."""
        if space in self.spaces:
            raise ValueError('that space is already in the puzzle')
        self.spaces.add(space)

    def add_region_with_condition(
        self, region: Region, condition: Condition,
    ) -> None:
        """Add one region to the Pips puzzle with an attached condition."""
        for existing_region in self.regions:
            if region.overlaps_with(existing_region):
                raise ValueError(
                    'condition regions in the puzzle may not overlap'
                )
        for region_space in region:
            if region_space not in self.spaces:
                raise ValueError(
                    'region contains a space that is not in the puzzle'
                )
        self.regions[region] = condition

    @classmethod
    def parse(cls, puzzle_string: str) -> Self:
        """Parse the contents of a Pips puzzle file as a puzzle object."""
        board_layout_string, region_conditions_string, dominoes_string = (
            puzzle_string.rstrip().rsplit('\n\n', maxsplit=2)
        )

        spaces = parse_board_layout(board_layout_string)
        conditions = parse_region_conditions(region_conditions_string)

        space_chars = frozenset(spaces.values())
        for char in conditions:
            if char not in space_chars:
                raise ValueError(
                    f'region {char!r} has a condition but no puzzle spaces'
                )
        del space_chars

        regions: dict[Region, Condition] = {}
        for condition_char, condition in conditions.items():
            region = Region(
                space for space, space_char in spaces.items()
                if space_char == condition_char
            )
            regions[region] = condition

        dominoes = parse_dominoes(dominoes_string)
        return cls(spaces.keys(), regions, dominoes)

    @property
    def num_spaces(self) -> int:
        """The total number of spaces in the puzzle."""
        return len(self.spaces)

    @property
    def num_rows(self) -> int:
        """The total number of rows (including empty ones) in the puzzle."""
        min_r = min(space.r for space in self.spaces)
        max_r = max(space.r for space in self.spaces)
        return max_r - min_r + 1

    @property
    def num_columns(self) -> int:
        """The total number of columns (including empty ones) in the puzzle."""
        min_c = min(space.c for space in self.spaces)
        max_c = max(space.c for space in self.spaces)
        return max_c - min_c + 1

    @property
    def num_regions(self) -> int:
        """The total number of regions in the puzzle."""
        return len(self.regions)

    @property
    def num_dominoes(self) -> int:
        """The number of domino pieces for the puzzle."""
        return len(self.dominoes)

    def iter_sorted_spaces(self) -> Iterator[Space]:
        """Return an iterator over the puzzle's spaces in sorted order."""
        return iter(sorted(self.spaces))

    def iter_sorted_regions(self) -> Iterator[Region]:
        """Return an iterator over the puzzle's regions in sorted order."""
        return iter(sorted(self.regions.keys()))

    def get_condition(self, region: Region) -> Condition:
        """Return the condition associated with one of the puzzle's regions."""
        return self.regions[region]

    def iter_dominoes(self) -> Iterator[Domino]:
        """Return an iterator over the puzzle's domino pieces."""
        return iter(self.dominoes)

    def __contains__(
        self, space_or_region_or_domino: Space | Region | Domino,
    ) -> bool:
        if isinstance(space_or_region_or_domino, Space):
            return space_or_region_or_domino in self.spaces
        if isinstance(space_or_region_or_domino, Region):
            return space_or_region_or_domino in self.regions
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
