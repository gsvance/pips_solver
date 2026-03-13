"""Unit tests for the functionality of Pips game board objects."""

import unittest

from board import (
    Board,
    parse_region_conditions,
)
from conditions import (
    Equal,
    GreaterThan,
    LessThan,
    NotEqual,
    Number,
)
from regions import Region
from spaces import (
    LEFTMOST_COLUMN,
    Space,
    TOPMOST_ROW,
)


class TestBoard(unittest.TestCase):
    """Test case for the Pips board object."""

    def test_parse_region_conditions(self):
        """Test that the parse_region_conditions() utility function works."""
        string_1 = 'A =\nb =/=\n$ >4\n- 55\n9 <9\n'
        expectation_1 = {
            'A': Equal(),
            'b': NotEqual(),
            '$': GreaterThan(4),
            '-': Number(55),
            '9': LessThan(9),
        }
        conditions = parse_region_conditions(string_1)
        self.assertDictEqual(conditions, expectation_1)

        string_2 = "a =\nbc 4\nd <8"
        with self.assertRaisesRegex(ValueError, 'one character'):
            parse_region_conditions(string_2)

        string_3 = "% 6\n9 6\n% =\n"
        with self.assertRaisesRegex(ValueError, 'multiple conditions'):
            parse_region_conditions(string_3)

    def test_board_init(self):
        """Try to initialize an empty board object."""
        board = Board()
        self.assertSetEqual(board.spaces, set())
        self.assertDictEqual(board.regions, {})

    def test_board_add_space(self):
        """Check that spaces can be added to an empty board."""
        space_a = Space(TOPMOST_ROW, LEFTMOST_COLUMN)
        space_b = space_a.shift_by(delta_c=2)
        space_c = space_a.shift_by(delta_c=1)
        space_d = space_c.shift_by(delta_r=1)
        spaces_set = {space_a, space_b, space_c, space_d}

        board = Board()
        board.add_space(space_a)
        board.add_space(space_b)
        board.add_space(space_c)
        board.add_space(space_d)

        self.assertSetEqual(board.spaces, spaces_set)

        for space in spaces_set:
            with self.assertRaisesRegex(ValueError, 'already on the board'):
                board.add_space(space)

    def test_board_add_region_with_condition(self):
        """Test that regions with conditions can be added to a board."""
        space_a = Space(TOPMOST_ROW, LEFTMOST_COLUMN)
        space_b = space_a.shift_by(delta_c=1)
        space_c = space_a.shift_by(delta_r=1)
        space_d = space_a.shift_by(delta_c=1, delta_r=1)

        region_ac = Region([space_a, space_c])
        region_bd = Region([space_b, space_d])
        region_acd = Region([space_a, space_c, space_d])

        expected_regions_dict = {
            region_ac: LessThan(4),
            region_bd: NotEqual(),
        }

        board = Board()
        board.add_space(space_a)
        board.add_space(space_b)
        board.add_space(space_c)
        board.add_space(space_d)
        board.add_region_with_condition(region_ac, LessThan(4))
        board.add_region_with_condition(region_bd, NotEqual())

        self.assertDictEqual(board.regions, expected_regions_dict)

        for region in (region_ac, region_bd, region_acd):
            with self.assertRaisesRegex(ValueError, 'may not overlap'):
                board.add_region_with_condition(region, Number(14))

        with self.assertRaisesRegex(ValueError, 'not on the board'):
            board.add_region_with_condition(
                Region([space_d.shift_by(delta_r=10)]), GreaterThan(0),
            )

    def test_board_parse(self):
        """Test that a board object can be parsed from a string."""
        board_string = "ABB#\n B\n B\n\nA 6\nB ="

        expected_spaces = {
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 0),
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 1),
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 2),
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 3),
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1),
            Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 1),
        }
        expected_regions = {
            Region([Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 0)]): Number(6),
            Region([
                Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 1),
                Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 2),
                Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1),
                Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 1),
            ]): Equal(),
        }

        board = Board.parse(board_string)

        self.assertSetEqual(board.spaces, expected_spaces)
        self.assertDictEqual(board.regions, expected_regions)

        board_string += "\nX >5"

        with self.assertRaisesRegex(ValueError, 'no board spaces'):
            Board.parse(board_string)

    def test_board_num_properties(self):
        """Test the "num"-prefixed properties of the board class."""
        board = Board.parse("ABC\nADCEE\n\nA 4\nB 1\nC =\nD <1")

        self.assertEqual(board.num_spaces, 8)
        self.assertEqual(board.num_rows, 2)
        self.assertEqual(board.num_columns, 5)
        self.assertEqual(board.num_regions, 4)

    def test_board_iter_sorted_spaces(self):
        """Test iteration over a board's spaces in sorted order."""
        space_a = Space(TOPMOST_ROW, LEFTMOST_COLUMN)
        space_b = space_a.shift_by(delta_c=2)
        space_c = space_a.shift_by(delta_r=1)
        space_d = space_c.shift_by(delta_c=1)
        space_e = space_d.shift_by(delta_c=1)

        board = Board()
        board.add_space(space_b)
        board.add_space(space_e)
        board.add_space(space_d)
        board.add_space(space_c)
        board.add_space(space_a)

        self.assertListEqual(
            list(board.iter_sorted_spaces()),
            [space_a, space_b, space_c, space_d, space_e],
        )

    def test_board_iter_sorted_regions(self):
        """Test iteration over a board's regions in sorted order."""
        board = Board.parse("#$\nZD\n..\n\n. =/=\n# =\n$ 5\nD >3")

        expected_sorted_regions = [
            Region([Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 0)]),
            Region([Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 1)]),
            Region([Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1)]),
            Region([
                Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 0),
                Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 1),
            ]),
        ]

        self.assertListEqual(
            list(board.iter_sorted_regions()), expected_sorted_regions,
        )

    def test_board_get_condition(self):
        """Test looking up a condition on the board with a region as key."""
        board = Board.parse("ab\nc\n\na 5\nb =\nc >2")

        region_a = Region([Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 0)])
        region_b = Region([Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 1)])
        region_c = Region([Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 0)])

        self.assertEqual(board.get_condition(region_a), Number(5))
        self.assertEqual(board.get_condition(region_b), Equal())
        self.assertEqual(board.get_condition(region_c), GreaterThan(2))

    def test_board_contains(self):
        """Test that board objects work correctly with the "in" operator."""
        board = Board.parse("A\nB#C\n\nA 5\nB 2\nC <1")
        top_left = Space(TOPMOST_ROW, LEFTMOST_COLUMN)

        self.assertTrue(top_left in board)
        self.assertFalse(top_left.shift_by(delta_r=15) in board)

        self.assertTrue(Region([top_left]) in board)
        self.assertFalse(
            Region([top_left, top_left.shift_by(delta_r=1)]) in board
        )
        self.assertFalse(Region([top_left.shift_by(delta_c=20)]) in board)

    def test_board_repr(self):
        """Test that a board can produce a sensible string repr."""
        board = Board.parse("A..BBB\n\nA 3\nB =")
        expected_repr = "<Board with 6 spaces and 2 regions>"
        self.assertEqual(repr(board), expected_repr)
