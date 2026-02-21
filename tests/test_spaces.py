"""Unit tests for the functionality of the Pips board spaces."""

from dataclasses import FrozenInstanceError
import random
import unittest

from spaces import (
    LEFTMOST_COLUMN,
    parse_board_layout,
    Space,
    TOPMOST_ROW,
)


class TestSpaces(unittest.TestCase):
    """Test case for the Pips board spaces."""

    def test_space_init(self):
        """Check that space objects can be initialized correctly."""
        valid_rc_pairs = [
            (TOPMOST_ROW + 2, LEFTMOST_COLUMN + 3),
            (TOPMOST_ROW, LEFTMOST_COLUMN),
            (TOPMOST_ROW, LEFTMOST_COLUMN + 1),
            (TOPMOST_ROW + 4, LEFTMOST_COLUMN),
        ]
        for r, c in valid_rc_pairs:
            space = Space(r, c)
            self.assertEqual(space.r, r)
            self.assertEqual(space.c, c)
        invalid_rc_pairs = [
            (TOPMOST_ROW - 1, LEFTMOST_COLUMN + 7),
            (TOPMOST_ROW + 8, LEFTMOST_COLUMN - 1),
            (TOPMOST_ROW - 2, LEFTMOST_COLUMN - 3),
        ]
        for r, c in invalid_rc_pairs:
            with self.assertRaises(ValueError):
                Space(r, c)

    def test_space_init_unchecked(self):
        """Ensure that unchecked initialization works for space objects."""
        rc_pairs = [
            (TOPMOST_ROW + 4, LEFTMOST_COLUMN + 6),
            (TOPMOST_ROW - 2, LEFTMOST_COLUMN + 3),
            (TOPMOST_ROW + 5, LEFTMOST_COLUMN - 3),
            (TOPMOST_ROW - 1, LEFTMOST_COLUMN - 10),
        ]
        for r, c in rc_pairs:
            space = Space(r, c, unchecked=True)
            self.assertEqual(space.r, r)
            self.assertEqual(space.c, c)

    def test_space_str_and_repr(self):
        """Check that the space object's str and repr methods work."""
        r, c = TOPMOST_ROW + 6, LEFTMOST_COLUMN + 4
        space = Space(r, c)
        expected_str = str(r) + ',' + str(c)
        self.assertEqual(str(space), expected_str)
        expected_repr = 'Space(r=' + str(r) + ', c=' + str(c) + ')'
        self.assertEqual(repr(space), expected_repr)

    def test_space_shift_by(self):
        """Ensure that the space shifting method works correctly."""
        r, c = TOPMOST_ROW + 2, LEFTMOST_COLUMN + 6
        space = Space(r, c)
        for dr in [1, -1, 15, -30, 0]:
            shifted = space.shift_by(delta_r=dr)
            self.assertEqual(shifted.r, r + dr)
            self.assertEqual(shifted.c, c)
        for dc in [1, -1, 20, -45, 0]:
            shifted = space.shift_by(delta_c=dc)
            self.assertEqual(shifted.r, r)
            self.assertEqual(shifted.c, c + dc)
        for dr, dc in [(0, 0), (4, 2), (-20, -30), (-25, 5), (3, -16)]:
            shifted = space.shift_by(delta_r=dr, delta_c=dc)
            self.assertEqual(shifted.r, r + dr)
            self.assertEqual(shifted.c, c + dc)
        with self.assertRaises(TypeError):
            space.shift_by()

    def test_space_ordering(self):
        """Check that spaces are ordered by row then column as expected."""
        sorted_spaces = [
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 0),
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 1),
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 0),
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1),
        ]
        shuffled = list(sorted_spaces)  # Make copy
        while shuffled == sorted_spaces:
            random.shuffle(shuffled)
        shuffled.sort()
        self.assertListEqual(shuffled, sorted_spaces)

    def test_space_frozen(self):
        """Make sure that space objects are indeed frozen."""
        space = Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 1)
        with self.assertRaises(FrozenInstanceError):
            setattr(space, 'r', TOPMOST_ROW + 4)
        with self.assertRaises(FrozenInstanceError):
            setattr(space, 'c', LEFTMOST_COLUMN + 3)

    def test_parse_board_layout(self):
        """Check that a very simple board layout can be correctly parsed."""
        board_layout_string = '\n\n\n AA B\n CDDD#\n'
        expected_spaces = {
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 0): 'A',
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 1): 'A',
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 3): 'B',
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 0): 'C',
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1): 'D',
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 2): 'D',
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 3): 'D',
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 4): '#',
        }
        self.assertDictEqual(
            parse_board_layout(board_layout_string), expected_spaces,
        )
