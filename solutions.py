"""A solution contains the set of moves needed to solve a Pips puzzle."""

from collections.abc import Iterator
from pathlib import Path
from typing import Self

from dominoes import Domino
from spaces import Space
from spots import Spot


class Solution:
    """A collection of moves that are used to solve a Pips puzzle."""

    __slots__ = ('moves',)

    def __init__(self) -> None:
        self.moves: list[tuple[Domino, Spot]] = []

    def add_move(self, domino: Domino, spot: Spot) -> None:
        """Add one domino move to the Pips solution."""
        for existing_domino, existing_spot in self:
            if domino == existing_domino:
                raise ValueError('duplicate domino added to solution')
            if spot.overlaps_with(existing_spot):
                raise ValueError('overlapping spot added to solution')
        self.moves.append((domino, spot))

    def __iter__(self) -> Iterator[tuple[Domino, Spot]]:
        return iter(self.moves)

    def save_file(self, file_path: Path) -> None:
        """Save a solution object to a text file."""
        with file_path.open('w', encoding='utf-8') as f:
            for domino, spot in self:
                f.write(f'{domino!s} {spot!s}\n')

    @classmethod
    def load_file(cls, file_path: Path) -> Self:
        """Load a solution object from a text file."""
        solution = cls()
        with file_path.open('r', encoding='utf-8') as f:
            for line in f:
                domino_string, spot_string = line.strip().split()
                domino = Domino.parse(domino_string)
                spot = Spot.parse(spot_string)
                solution.add_move(domino, spot)
        return solution
