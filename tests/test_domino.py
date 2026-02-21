"""Unit tests for the Domino data class and related functions."""

import unittest

from dominoes import Domino, MIN_DOTS, MAX_DOTS, parse_dominoes


class TestDomino(unittest.TestCase):

    def test_domino_init(self):
        domino_a = Domino(3, 5)
        self.assertSetEqual(set(domino_a.dots), {3, 5})
        domino_b = Domino(4, 1)
        self.assertSetEqual(set(domino_b.dots), {1, 4})
        domino_c = Domino(6, 6)
        self.assertSetEqual(set(domino_c.dots), {6})
        with self.assertRaises(ValueError):
            Domino(3, MIN_DOTS - 1)
        with self.assertRaises(ValueError):
            Domino(MAX_DOTS + 1, 3)

    def test_domino_eq_and_ne(self):
        self.assertEqual(Domino(4, 4), Domino(4, 4))
        self.assertEqual(Domino(3, 4), Domino(3, 4))
        self.assertEqual(Domino(5, 1), Domino(1, 5))
        self.assertNotEqual(Domino(4, 2), Domino(4, 1))
        self.assertNotEqual(Domino(3, 0), Domino(0, 2))

    def test_domino_parse(self):
        self.assertEqual(Domino.parse('45'), Domino(4, 5))
        self.assertEqual(Domino.parse('00'), Domino(0, 0))
        self.assertEqual(Domino.parse('21'), Domino(2, 1))

    def test_domino_iter(self):
        domino_a = Domino(2, 3)
        self.assertListEqual(list(iter(domino_a)), [2, 3])
        domino_b = Domino(3, 3)
        self.assertListEqual(list(iter(domino_b)), [3, 3])
        domino_c = Domino(5, 2)
        self.assertListEqual(list(iter(domino_c)), [5, 2])

    def test_domino_len(self):
        self.assertEqual(len(Domino(1, 1)), 2)
        self.assertEqual(len(Domino(2, 6)), 2)
        self.assertEqual(len(Domino(3, 0)), 2)

    def test_domino_repr(self):
        self.assertEqual(repr(Domino(1, 2)), 'Domino(1, 2)')
        self.assertEqual(repr(Domino(5, 5)), 'Domino(5, 5)')
        self.assertEqual(repr(Domino(6, 0)), 'Domino(6, 0)')

    def test_domino_str(self):
        self.assertEqual(str(Domino(1, 3)), '1|3')
        self.assertEqual(str(Domino(4, 4)), '4|4')
        self.assertEqual(str(Domino(5, 2)), '5|2')

    def test_parse_dominoes(self):
        self.assertListEqual(
            parse_dominoes('45 66 21\n55 22'),
            [
                Domino(4, 5), Domino(6, 6), Domino(2, 1),
                Domino(5, 5), Domino(2, 2),
            ],
        )
