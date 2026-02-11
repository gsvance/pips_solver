"""Unit tests for the functionality of the Space data class."""

import unittest

from basics import Space, TOPMOST_ROW, LEFTMOST_COLUMN, parse_board_layout


class TestSpace(unittest.TestCase):

    def test_space_init(self):
        space = Space(2, 3)
        self.assertEqual(space.r, 2)
        self.assertEqual(space.c, 3)
        with self.assertRaises(ValueError):
            Space(TOPMOST_ROW - 1, 7)
        with self.assertRaises(ValueError):
            Space(8, LEFTMOST_COLUMN - 1)

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

    def test_parse_board_layout(self):
        board_layout_string = '\n\n AAB\n CDD#\n'
        expected_spaces = {
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 0): 'A',
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 1): 'A',
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 2): 'B',
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 0): 'C',
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1): 'D',
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 2): 'D',
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 3): '#',
        }
        self.assertDictEqual(
            parse_board_layout(board_layout_string), expected_spaces,
        )
