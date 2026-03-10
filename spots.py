"""Spots are ordered pairs of adjacent spaces where dominos may be placed."""

from collections.abc import Iterator
from dataclasses import dataclass

from puzzle import Puzzle
from spaces import Space


@dataclass(order=True, frozen=True, match_args=False, slots=True)
class Spot:
    """An ordered pair of adjacent spaces where a domino could be placed."""
    spaces: tuple[Space, Space]

    def __init__(self, space_1: Space, space_2: Space, /) -> None:
        if abs(space_2.r - space_1.r) + abs(space_2.c - space_1.c) != 1:
            raise ValueError('spot must be made up of two adjacent spaces')
        object.__setattr__(self, 'spaces', (space_1, space_2))

    def __iter__(self) -> Iterator[Space]:
        return iter(self.spaces)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{tuple(self)!r}'

    def __str__(self) -> str:
        return ':'.join(map(str, self))

    def is_sorted(self) -> bool:
        """Return True if this spot's two spaces occur in sorted order."""
        space_1, space_2 = self
        return space_1 < space_2

    def is_horizontal(self) -> bool:
        """Return True if the spot is horizontal and False if vertical."""
        space_1, space_2 = self
        if space_1.r == space_2.r:
            return True  # Same row == horizontal
        if space_1.c == space_2.c:
            return False  # Same column == vertical
        assert False, 'unreachable code'

    def is_vertical(self) -> bool:
        """Return True if the spot is vertical and False if horizontal."""
        return not self.is_horizontal()


def get_sorted_spots(puzzle: Puzzle) -> list[Spot]:
    """Return a sorted list of every spot where a domino could be placed."""
    spots: set[Spot] = set()
    for space in puzzle.iter_sorted_spaces():
        neighbors = (
            space.shift_by(delta_r=+1), space.shift_by(delta_r=-1),
            space.shift_by(delta_c=+1), space.shift_by(delta_c=-1),
        )
        for neighbor in neighbors:
            if neighbor in puzzle:
                spots.add(Spot(space, neighbor))
    return sorted(spots)
