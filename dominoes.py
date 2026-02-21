"""Dominoes are the rectangular two-valued Pips game pieces."""

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Final, Self


# One half of a domino never has fewer than zero dots or more than six dots.
MIN_DOTS: Final[int] = 0
MAX_DOTS: Final[int] = 6


@dataclass(frozen=True, match_args=False, slots=True)
class Domino:
    """A single Pips domino piece with two associated dots values."""
    dots: tuple[int, int]

    # Internally, the two dots values are always stored in sorted order, but I
    # want to remember the order they were input for user-friendliness reasons.
    flip_dots: bool = field(init=False, repr=False, compare=False)

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

    def is_symmetric(self) -> bool:
        """Return True if the domino has two copies of the same dots value."""
        dots_1, dots_2 = self
        return dots_1 == dots_2


def parse_dominoes(dominoes_string: str) -> list[Domino]:
    """Parse many domino strings separated by whitespace and return a list."""
    return list(map(Domino.parse, dominoes_string.strip().split()))
