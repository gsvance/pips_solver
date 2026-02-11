"""Data classes for representing Pips color region conditions."""

import abc
import dataclasses
from typing import Final, Self


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
