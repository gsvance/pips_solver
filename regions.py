"""Pips regions are colored collections of spaces with conditions attached."""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Self

from spaces import Space


@dataclass(order=True, frozen=True, match_args=False, slots=True)
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
