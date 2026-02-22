"""The Pips board is a collection of spaces and regions with conditions."""

from collections.abc import Iterator
from typing import Self

from conditions import Condition, parse_condition
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
