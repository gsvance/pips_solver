"""Unit tests for the functionality of the Space data class."""

import unittest

from basics import Space, TOPMOST_ROW, LEFTMOST_COLUMN


class TestSpace(unittest.TestCase):

    def test_space_init(self):
        space = Space(2, 3)
        self.assertEqual(space.r, 2)
        self.assertEqual(space.c, 3)

    def test_space_str(self):
        space = Space(6, 4)
        self.assertEqual(str(space), '6,4')

    def test_space_shift_by(self):
        space = Space(5, 8)
        self.assertEqual(space.shift_by(delta_r=1), Space(6, 8))
        self.assertEqual(space.shift_by(delta_r=-1), Space(4, 8))
        self.assertEqual(space.shift_by(delta_c=1), Space(5, 9))
        self.assertEqual(space.shift_by(delta_c=-1), Space(5, 7))
        self.assertEqual(space.shift_by(delta_r=0, delta_c=0), space)
        self.assertEqual(space.shift_by(delta_r=-4, delta_c=2), Space(1, 10))
