"""Unit tests for the dominoes that act as playing pieces for Pips."""

from dataclasses import FrozenInstanceError
import itertools
import random
from typing import Final
import unittest

from dominoes import (
    Domino,
    MAX_DOTS,
    MIN_DOTS,
    parse_dominoes,
)


# Test fixture: a constant list containing all valid domino dots values.
VALID_DOTS: Final[list[int]] = list(range(MIN_DOTS, MAX_DOTS + 1))


class TestDominoes(unittest.TestCase):
    """Test case for the Pips domino pieces."""

    def test_domino_init(self):
        """Check that domino objects can be initialized correctly."""
        for dots_1, dots_2 in itertools.product(VALID_DOTS, VALID_DOTS):
            domino = Domino(dots_1, dots_2)
            self.assertSetEqual(set(domino.dots), {dots_1, dots_2})
        invalid_dots = [
            MIN_DOTS - 4, MIN_DOTS - 3, MIN_DOTS - 2, MIN_DOTS - 1,
            MAX_DOTS + 1, MAX_DOTS + 2, MAX_DOTS + 3, MAX_DOTS + 4,
        ]
        for dots_1, dots_2 in itertools.product(
            invalid_dots + VALID_DOTS, invalid_dots + VALID_DOTS,
        ):
            if dots_1 in invalid_dots or dots_2 in invalid_dots:
                with self.assertRaises(ValueError):
                    Domino(dots_1, dots_2)

    def test_domino_eq_and_ne(self):
        """Ensure that domino equality is independent of the dots order."""
        for dots_a, dots_b in itertools.product(VALID_DOTS, VALID_DOTS):
            domino_ab = Domino(dots_a, dots_b)
            domino_ba = Domino(dots_b, dots_a)
            self.assertEqual(domino_ab, domino_ba)
        for dots_a, dots_b, dots_c, dots_d in itertools.product(
            VALID_DOTS, VALID_DOTS, VALID_DOTS, VALID_DOTS,
        ):
            if {dots_a, dots_b} != {dots_c, dots_d}:
                domino_ab = Domino(dots_a, dots_b)
                domino_ba = Domino(dots_b, dots_a)
                domino_cd = Domino(dots_c, dots_d)
                domino_dc = Domino(dots_d, dots_c)
                self.assertNotEqual(domino_ab, domino_cd)
                self.assertNotEqual(domino_ba, domino_cd)
                self.assertNotEqual(domino_ab, domino_dc)
                self.assertNotEqual(domino_ba, domino_dc)

    def test_domino_parse(self):
        """Test parsing of simple terse domino strings."""
        for dots_1, dots_2 in itertools.product(VALID_DOTS, VALID_DOTS):
            dots_1_str = str(dots_1)
            self.assertEqual(len(dots_1_str), 1)
            dots_2_str = str(dots_2)
            self.assertEqual(len(dots_2_str), 1)
            domino_str = dots_1_str + dots_2_str
            self.assertEqual(len(domino_str), 2)
            self.assertEqual(Domino.parse(domino_str), Domino(dots_1, dots_2))

    def test_domino_iter(self):
        """Check that domino dots values can be iterated over."""
        for dots_1, dots_2 in itertools.product(VALID_DOTS, VALID_DOTS):
            domino = Domino(dots_1, dots_2)
            self.assertListEqual(list(iter(domino)), [dots_1, dots_2])

    def test_domino_len(self):
        """Test that a domino's length is always 2."""
        for dots_1, dots_2 in itertools.product(VALID_DOTS, VALID_DOTS):
            domino = Domino(dots_1, dots_2)
            self.assertEqual(len(domino), 2)

    def test_domino_str_and_repr(self):
        """Make sure the domino str and repr methods work as expected."""
        for dots_1, dots_2 in itertools.product(VALID_DOTS, VALID_DOTS):
            domino = Domino(dots_1, dots_2)
            expected_str = str(dots_1) + '|' + str(dots_2)
            self.assertEqual(str(domino), expected_str)
            expected_repr = 'Domino(' + str(dots_1) + ', ' + str(dots_2) + ')'
            self.assertEqual(repr(domino), expected_repr)

    def test_domino_frozen(self):
        """Ensure that domino objects have frozen attributes."""
        domino = Domino(MAX_DOTS, MIN_DOTS)
        with self.assertRaises(FrozenInstanceError):
            setattr(domino, 'dots', (MIN_DOTS, MAX_DOTS))

    def test_domino_is_symmetric(self):
        """Test that dominoes know when they are symmetric."""
        for dots_1, dots_2 in itertools.product(VALID_DOTS, VALID_DOTS):
            domino = Domino(dots_1, dots_2)
            if dots_1 == dots_2:
                self.assertTrue(domino.is_symmetric())
            else:
                self.assertFalse(domino.is_symmetric())

    def test_parse_dominoes(self):
        """Try parsing a long string of whitespace-separated dominoes."""
        dominoes = [
            Domino(dots_1, dots_2)
            for dots_1, dots_2 in itertools.product(VALID_DOTS, VALID_DOTS)
        ]
        random.shuffle(dominoes)

        whitespace = [' ', '\t', '\n']
        string_parts = []

        # Random leading whitespace
        for _ in range(random.randint(0, 2)):
            string_parts.append(random.choice(whitespace))

        # Two-digit domino strings separated by random whitespace
        for i, domino in enumerate(dominoes):
            if i > 0:
                for _ in range(random.randint(1, 3)):
                    string_parts.append(random.choice(whitespace))
            dots_1, dots_2 = domino
            string_parts.append(str(dots_1))
            string_parts.append(str(dots_2))

        # Random trailing whitespace
        for _ in range(random.randint(0, 2)):
            string_parts.append(random.choice(whitespace))

        string = ''.join(string_parts)
        self.assertListEqual(parse_dominoes(string), dominoes)
