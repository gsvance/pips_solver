"""Unit tests for the series of region Condition subclasses."""

from dataclasses import FrozenInstanceError
from typing import Final
import unittest

from conditions import (
    Condition,
    Equal,
    EQUAL_SYMBOL,
    GreaterThan,
    GREATER_THAN_PREFIX,
    LessThan,
    LESS_THAN_PREFIX,
    NotEqual,
    NOT_EQUAL_SYMBOL,
    Number,
    parse_condition,
)


# Test fixture: a constant list containing a bunch of strings that shouldn't
# parse correctly as *any* type of condition.
INVALID_CONDITION_STRINGS: Final[list[str]] = [
    '32a', 'b4', 'abc', 'x6y', 'f',
    '', ' ', '\t', '\n',
    '>', '<', '4>', '5<', '>=', '<=', '>=2', '<=3',
    '=5', '==7', '1=', '=8=',
    '!=', '==', '=\\=', '/=', '=/', '\\=', '=\\',
]


class TestConditions(unittest.TestCase):
    """Test case for the Pips region conditions."""

    def test_number_condition(self):
        """Make sure "number" conditions behave correctly."""
        condition = parse_condition('4')

        self.assertIsInstance(condition, Condition)
        self.assertIsInstance(condition, Number)
        assert isinstance(condition, Number)  # For the type checker

        self.assertEqual(condition, Number(4))
        self.assertEqual(condition.number, 4)
        with self.assertRaises(FrozenInstanceError):
            setattr(condition, 'number', 6)

        self.assertEqual(repr(condition), 'Number(4)')
        self.assertEqual(condition.as_terse_string(), '4')

        with self.assertRaises(ValueError):
            Number(-2)

        self.assertEqual(Number.maybe_parse('10'), Number(10))
        self.assertIsNone(Number.maybe_parse(GREATER_THAN_PREFIX + '4'))
        self.assertIsNone(Number.maybe_parse(LESS_THAN_PREFIX + '1'))
        self.assertIsNone(Number.maybe_parse(EQUAL_SYMBOL))
        self.assertIsNone(Number.maybe_parse(NOT_EQUAL_SYMBOL))

        for invalid in INVALID_CONDITION_STRINGS:
            self.assertIsNone(Number.maybe_parse(invalid))

    def test_equal_condition(self):
        """Make sure "equal" conditions behave correctly."""
        condition = parse_condition(EQUAL_SYMBOL)

        self.assertIsInstance(condition, Condition)
        self.assertIsInstance(condition, Equal)

        self.assertEqual(condition, Equal())

        self.assertEqual(repr(condition), 'Equal()')
        self.assertEqual(condition.as_terse_string(), EQUAL_SYMBOL)

        self.assertEqual(Equal.maybe_parse(EQUAL_SYMBOL), Equal())
        self.assertIsNone(Equal.maybe_parse(NOT_EQUAL_SYMBOL))
        self.assertIsNone(Equal.maybe_parse('6'))
        self.assertIsNone(Equal.maybe_parse(GREATER_THAN_PREFIX + '14'))
        self.assertIsNone(Equal.maybe_parse(LESS_THAN_PREFIX + '11'))

        for invalid in INVALID_CONDITION_STRINGS:
            self.assertIsNone(Equal.maybe_parse(invalid))

    def test_not_equal_condition(self):
        """Make sure "not equal" conditions behave correctly."""
        condition = parse_condition(NOT_EQUAL_SYMBOL)

        self.assertIsInstance(condition, Condition)
        self.assertIsInstance(condition, NotEqual)

        self.assertEqual(condition, NotEqual())

        self.assertEqual(repr(condition), 'NotEqual()')
        self.assertEqual(condition.as_terse_string(), NOT_EQUAL_SYMBOL)

        self.assertEqual(NotEqual.maybe_parse(NOT_EQUAL_SYMBOL), NotEqual())
        self.assertIsNone(NotEqual.maybe_parse(EQUAL_SYMBOL))
        self.assertIsNone(NotEqual.maybe_parse('9'))
        self.assertIsNone(NotEqual.maybe_parse(GREATER_THAN_PREFIX + '5'))
        self.assertIsNone(NotEqual.maybe_parse(LESS_THAN_PREFIX + '3'))

        for invalid in INVALID_CONDITION_STRINGS:
            self.assertIsNone(NotEqual.maybe_parse(invalid))

    def test_greater_than_condition(self):
        """Make sure "greater than" conditions behave correctly."""
        condition = parse_condition(GREATER_THAN_PREFIX + '6')

        self.assertIsInstance(condition, Condition)
        self.assertIsInstance(condition, GreaterThan)
        assert isinstance(condition, GreaterThan)  # For the type checker

        self.assertEqual(condition, GreaterThan(6))
        self.assertEqual(condition.number, 6)
        with self.assertRaises(FrozenInstanceError):
            setattr(condition, 'number', 1)

        self.assertEqual(repr(condition), 'GreaterThan(6)')
        self.assertEqual(
            condition.as_terse_string(), GREATER_THAN_PREFIX + '6',
        )

        with self.assertRaises(ValueError):
            GreaterThan(-1)

        self.assertEqual(
            GreaterThan.maybe_parse(GREATER_THAN_PREFIX + '15'),
            GreaterThan(15),
        )
        self.assertIsNone(GreaterThan.maybe_parse(LESS_THAN_PREFIX + '4'))
        self.assertIsNone(GreaterThan.maybe_parse('20'))
        self.assertIsNone(GreaterThan.maybe_parse(EQUAL_SYMBOL))
        self.assertIsNone(GreaterThan.maybe_parse(NOT_EQUAL_SYMBOL))

        for invalid in INVALID_CONDITION_STRINGS:
            self.assertIsNone(GreaterThan.maybe_parse(invalid))

    def test_less_than_condition(self):
        """Make sure "less than" conditions behave correctly."""
        condition = parse_condition('<3')

        self.assertIsInstance(condition, Condition)
        self.assertIsInstance(condition, LessThan)
        assert isinstance(condition, LessThan)  # For the type checker

        self.assertEqual(condition, LessThan(3))
        self.assertEqual(condition.number, 3)
        with self.assertRaises(FrozenInstanceError):
            setattr(condition, 'number', 12)

        self.assertEqual(repr(condition), 'LessThan(3)')
        self.assertEqual(condition.as_terse_string(), '<3')

        with self.assertRaises(ValueError):
            LessThan(0)

        self.assertEqual(
            LessThan.maybe_parse(LESS_THAN_PREFIX + '11'), LessThan(11),
        )
        self.assertIsNone(LessThan.maybe_parse(GREATER_THAN_PREFIX + '5'))
        self.assertIsNone(LessThan.maybe_parse('18'))
        self.assertIsNone(LessThan.maybe_parse(EQUAL_SYMBOL))
        self.assertIsNone(LessThan.maybe_parse(NOT_EQUAL_SYMBOL))

        for invalid in INVALID_CONDITION_STRINGS:
            self.assertIsNone(LessThan.maybe_parse(invalid))

    def test_parse_condition_for_invalid(self):
        """Make sure that parse_condition() raises for invalid inputs."""
        for invalid in INVALID_CONDITION_STRINGS:
            with self.assertRaises(ValueError):
                parse_condition(invalid)
