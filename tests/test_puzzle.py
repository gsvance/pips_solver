"""Unit tests for the functionality of Pips puzzle objects."""

import unittest

from conditions import (
    Equal,
    GreaterThan,
    LessThan,
    NotEqual,
    Number,
)
from puzzle import (
    parse_region_conditions,
    Puzzle,
)
from regions import Region
from spaces import (
    LEFTMOST_COLUMN,
    Space,
    TOPMOST_ROW,
)


class TestPuzzle(unittest.TestCase):
    """Test case for the Pips puzzle object."""

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

    def test_puzzle_init(self):
        """Try to initialize an empty puzzle object."""
        puzzle = Puzzle([], {}, [])
        self.assertSetEqual(puzzle.spaces, set())
        self.assertDictEqual(puzzle.regions, {})
        self.assertListEqual(puzzle.dominoes, [])

    def test_puzzle_add_space(self):
        """Check that spaces can be added to an empty puzzle."""
        space_a = Space(TOPMOST_ROW, LEFTMOST_COLUMN)
        space_b = space_a.shift_by(delta_c=2)
        space_c = space_a.shift_by(delta_c=1)
        space_d = space_c.shift_by(delta_r=1)
        spaces_set = {space_a, space_b, space_c, space_d}

        puzzle = Puzzle([], {}, [])
        puzzle.add_space(space_a)
        puzzle.add_space(space_b)
        puzzle.add_space(space_c)
        puzzle.add_space(space_d)

        self.assertSetEqual(puzzle.spaces, spaces_set)

        for space in spaces_set:
            with self.assertRaisesRegex(ValueError, 'already in the puzzle'):
                puzzle.add_space(space)

    def test_puzzle_add_region_with_condition(self):
        """Test that regions with conditions can be added to a puzzle."""
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

        puzzle = Puzzle([], {}, [])
        puzzle.add_space(space_a)
        puzzle.add_space(space_b)
        puzzle.add_space(space_c)
        puzzle.add_space(space_d)
        puzzle.add_region_with_condition(region_ac, LessThan(4))
        puzzle.add_region_with_condition(region_bd, NotEqual())

        self.assertDictEqual(puzzle.regions, expected_regions_dict)

        for region in (region_ac, region_bd, region_acd):
            with self.assertRaisesRegex(ValueError, 'may not overlap'):
                puzzle.add_region_with_condition(region, Number(14))

        with self.assertRaisesRegex(ValueError, 'not in the puzzle'):
            puzzle.add_region_with_condition(
                Region([space_d.shift_by(delta_r=10)]), GreaterThan(0),
            )

    def test_puzzle_parse(self):
        """Test that a puzzle object can be parsed from a string."""
        puzzle_string = "ABB#\n B\n B\n\nA 6\nB ="
        dominoes_suffix = "\n\n34 56 21"

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

        puzzle = Puzzle.parse(puzzle_string + dominoes_suffix)

        self.assertSetEqual(puzzle.spaces, expected_spaces)
        self.assertDictEqual(puzzle.regions, expected_regions)

        puzzle_string += "\nX >5"

        with self.assertRaisesRegex(ValueError, 'no puzzle spaces'):
            puzzle.parse(puzzle_string + dominoes_suffix)

    def test_puzzle_num_properties(self):
        """Test the "num"-prefixed properties of the puzzle class."""
        puzzle = Puzzle.parse(
            "ABC\nADCEE\n\nA 4\nB 1\nC =\nD <1\n\n12 23 34 45"
        )

        self.assertEqual(puzzle.num_spaces, 8)
        self.assertEqual(puzzle.num_rows, 2)
        self.assertEqual(puzzle.num_columns, 5)
        self.assertEqual(puzzle.num_regions, 4)

    def test_puzzle_iter_sorted_spaces(self):
        """Test iteration over a puzzle's spaces in sorted order."""
        space_a = Space(TOPMOST_ROW, LEFTMOST_COLUMN)
        space_b = space_a.shift_by(delta_c=2)
        space_c = space_a.shift_by(delta_r=1)
        space_d = space_c.shift_by(delta_c=1)
        space_e = space_d.shift_by(delta_c=1)

        puzzle = Puzzle([], {}, [])
        puzzle.add_space(space_b)
        puzzle.add_space(space_e)
        puzzle.add_space(space_d)
        puzzle.add_space(space_c)
        puzzle.add_space(space_a)

        self.assertListEqual(
            list(puzzle.iter_sorted_spaces()),
            [space_a, space_b, space_c, space_d, space_e],
        )

    def test_puzzle_iter_sorted_regions(self):
        """Test iteration over a puzzle's regions in sorted order."""
        puzzle = Puzzle.parse(
            "#$\nZD\n..\n\n. =/=\n# =\n$ 5\nD >3\n\n30 20 11"
        )

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
            list(puzzle.iter_sorted_regions()), expected_sorted_regions,
        )

    def test_puzzle_get_condition(self):
        """Test looking up a condition on the puzzle with a region as key."""
        puzzle = Puzzle.parse("ab\ncd\n\na 5\nb =\nc >2\nd =/=\n\n01 12")

        region_a = Region([Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 0)])
        region_b = Region([Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 1)])
        region_c = Region([Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 0)])
        region_d = Region([Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1)])

        self.assertEqual(puzzle.get_condition(region_a), Number(5))
        self.assertEqual(puzzle.get_condition(region_b), Equal())
        self.assertEqual(puzzle.get_condition(region_c), GreaterThan(2))
        self.assertEqual(puzzle.get_condition(region_d), NotEqual())

    def test_puzzle_contains(self):
        """Test that puzzle objects work correctly with the "in" operator."""
        puzzle = Puzzle.parse("A\nB#C\n\nA 5\nB 2\nC <1\n\n43 21")
        top_left = Space(TOPMOST_ROW, LEFTMOST_COLUMN)

        self.assertTrue(top_left in puzzle)
        self.assertFalse(top_left.shift_by(delta_r=15) in puzzle)

        self.assertTrue(Region([top_left]) in puzzle)
        self.assertFalse(
            Region([top_left, top_left.shift_by(delta_r=1)]) in puzzle
        )
        self.assertFalse(Region([top_left.shift_by(delta_c=20)]) in puzzle)

    def test_puzzle_repr(self):
        """Test that a puzzle can produce a sensible string repr."""
        puzzle = Puzzle.parse("A..BBB\n\nA 3\nB =\n\n21 35 06")
        expected_repr = "<Puzzle with 6 spaces, 2 regions, and 3 dominoes>"
        self.assertEqual(repr(puzzle), expected_repr)
