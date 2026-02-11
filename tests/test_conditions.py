"""Unit testing for the series of region Condition subclasses."""

import unittest

from conditions import (
    Number, Equal, NotEqual, GreaterThan, LessThan, parse_condition,
)


class TestConditions(unittest.TestCase):

    def test_number_condition(self):
        condition = parse_condition('4')
        self.assertIsInstance(condition, Number)
        self.assertEqual(condition.number, 4)  # type: ignore
        self.assertEqual(repr(condition), 'Number(4)')
        self.assertEqual(condition.as_terse_string(), '4')
        with self.assertRaises(ValueError):
            Number(-2)
        self.assertEqual(Number.maybe_parse('10'), Number(10))
        self.assertIsNone(Number.maybe_parse('>4'))
        self.assertIsNone(Number.maybe_parse('<1'))
        self.assertIsNone(Number.maybe_parse('32a'))

    def test_equal_condition(self):
        condition = parse_condition('=')
        self.assertIsInstance(condition, Equal)
        self.assertEqual(repr(condition), 'Equal()')
        self.assertEqual(condition.as_terse_string(), '=')
        self.assertEqual(Equal.maybe_parse('='), Equal())
        self.assertIsNone(Equal.maybe_parse('=/='))
        self.assertIsNone(Equal.maybe_parse('!='))

    def test_not_equal_condition(self):
        condition = parse_condition('=/=')
        self.assertIsInstance(condition, NotEqual)
        self.assertEqual(repr(condition), 'NotEqual()')
        self.assertEqual(condition.as_terse_string(), '=/=')
        self.assertEqual(NotEqual.maybe_parse('=/='), NotEqual())
        self.assertIsNone(NotEqual.maybe_parse('='))
        self.assertIsNone(NotEqual.maybe_parse('=='))

    def test_greater_than_condition(self):
        condition = parse_condition('>6')
        self.assertIsInstance(condition, GreaterThan)
        self.assertEqual(condition.number, 6)  # type: ignore
        self.assertEqual(repr(condition), 'GreaterThan(6)')
        self.assertEqual(condition.as_terse_string(), '>6')
        with self.assertRaises(ValueError):
            GreaterThan(-1)
        self.assertEqual(GreaterThan.maybe_parse('>15'), GreaterThan(15))
        self.assertIsNone(GreaterThan.maybe_parse('<4'))
        self.assertIsNone(GreaterThan.maybe_parse('20'))
        self.assertIsNone(GreaterThan.maybe_parse('=2'))

    def test_less_than_condition(self):
        condition = parse_condition('<3')
        self.assertIsInstance(condition, LessThan)
        self.assertEqual(condition.number, 3)  # type: ignore
        self.assertEqual(repr(condition), 'LessThan(3)')
        self.assertEqual(condition.as_terse_string(), '<3')
        with self.assertRaises(ValueError):
            LessThan(0)
        self.assertEqual(LessThan.maybe_parse('<11'), LessThan(11))
        self.assertIsNone(LessThan.maybe_parse('>5'))
        self.assertIsNone(LessThan.maybe_parse('18'))
        self.assertIsNone(LessThan.maybe_parse('=3'))
