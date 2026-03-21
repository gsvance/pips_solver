"""Unit tests for the space pairs that we call "spots" officially."""

from dataclasses import FrozenInstanceError
import random
import unittest

from dominoes import (
    Domino,
    MAX_DOTS,
    MIN_DOTS,
)
from puzzle import Puzzle
from spaces import (
    LEFTMOST_COLUMN,
    Space,
    TOPMOST_ROW,
)
from spots import (
    get_sorted_spots,
    Spot,
)


class TestSpots(unittest.TestCase):
    """Test case for the Pips domino spots."""

    def test_spot_init(self):
        """Test the initialization of spot objects."""
        space_a = Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 1)
        space_b = space_a.shift_by(delta_r=1)
        space_c = space_a.shift_by(delta_c=1)

        spot_ab = Spot(space_a, space_b)
        self.assertListEqual(list(spot_ab.spaces), [space_a, space_b])
        spot_ba = Spot(space_b, space_a)
        self.assertListEqual(list(spot_ba.spaces), [space_b, space_a])
        spot_ac = Spot(space_a, space_c)
        self.assertListEqual(list(spot_ac.spaces), [space_a, space_c])
        spot_ca = Spot(space_c, space_a)
        self.assertListEqual(list(spot_ca.spaces), [space_c, space_a])

        invalid_shifts = [
            (2, 0), (0, 2), (1, 1), (0, 0), (2, 1), (-1, 2),
            (-2, 0), (0, -2), (-1, -1), (-1, 1), (1, -1),
        ]
        for dr, dc in invalid_shifts:
            with self.assertRaisesRegex(ValueError, 'two adjacent spaces'):
                Spot(space_a, space_a.shift_by(delta_r=dr, delta_c=dc))

    def test_spot_iter(self):
        """Test that spots can be iterated over."""
        space_a = Space(TOPMOST_ROW + 3, LEFTMOST_COLUMN + 1)
        space_b = space_a.shift_by(delta_c=1)

        spot_ab = Spot(space_a, space_b)
        self.assertListEqual(list(iter(spot_ab)), [space_a, space_b])
        spot_ba = Spot(space_b, space_a)
        self.assertListEqual(list(iter(spot_ba)), [space_b, space_a])

    def test_spot_parse(self):
        """Test parsing of spot objects from string coordinate pairs."""
        space_1 = Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 4)
        space_2 = space_1.shift_by(delta_r=1)
        space_3 = space_1.shift_by(delta_c=1)

        space_pairs = [
            (space_1, space_2), (space_2, space_1),
            (space_1, space_3), (space_3, space_1),
        ]

        for space_a, space_b in space_pairs:
            spot_str = str(space_a) + ':' + str(space_b)
            self.assertEqual(Spot.parse(spot_str), Spot(space_a, space_b))

    def test_spot_repr_and_str(self):
        """Check the repr and str methods on the spot class."""
        space_a = Space(TOPMOST_ROW + 5, LEFTMOST_COLUMN + 8)
        space_b = space_a.shift_by(delta_r=-1)
        spot = Spot(space_a, space_b)

        expected_repr = 'Spot(' + repr(space_a) + ', ' + repr(space_b) + ')'
        self.assertEqual(repr(spot), expected_repr)
        expected_str = str(space_a) + ':' + str(space_b)
        self.assertEqual(str(spot), expected_str)

    def test_spot_is_sorted(self):
        """Test that spots can tell if their spaces appear in sorted order."""
        space_a = Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 3)
        space_b = space_a.shift_by(delta_r=1)
        space_c = space_a.shift_by(delta_c=1)

        self.assertTrue(Spot(space_a, space_b).is_sorted())
        self.assertTrue(Spot(space_a, space_c).is_sorted())
        self.assertFalse(Spot(space_b, space_a).is_sorted())
        self.assertFalse(Spot(space_c, space_a).is_sorted())

    def test_spot_is_horizontal_and_is_vertical(self):
        """Check that spots can correctly tell which way they're oriented."""
        space_a = Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 0)
        space_b = Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 0)
        space_c = Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 1)

        spot_ab = Spot(space_a, space_b)
        spot_ba = Spot(space_b, space_a)
        self.assertTrue(spot_ab.is_vertical())
        self.assertTrue(spot_ba.is_vertical())
        self.assertFalse(spot_ab.is_horizontal())
        self.assertFalse(spot_ba.is_horizontal())

        spot_ac = Spot(space_a, space_c)
        spot_ca = Spot(space_c, space_a)
        self.assertTrue(spot_ac.is_horizontal())
        self.assertTrue(spot_ca.is_horizontal())
        self.assertFalse(spot_ac.is_vertical())
        self.assertFalse(spot_ca.is_vertical())

    def test_spot_overlaps_with(self):
        """Ensure that spots can tell if they overlap one another."""
        space_a = Space(TOPMOST_ROW, LEFTMOST_COLUMN + 1)
        space_b = space_a.shift_by(delta_r=1)
        space_c = space_b.shift_by(delta_r=1)
        space_d = space_c.shift_by(delta_c=-1)

        spot_ab = Spot(space_a, space_b)
        spot_cd = Spot(space_c, space_d)
        spot_bc = Spot(space_b, space_c)

        self.assertFalse(spot_ab.overlaps_with(spot_cd))
        self.assertFalse(spot_cd.overlaps_with(spot_ab))

        self.assertTrue(spot_ab.overlaps_with(spot_bc))
        self.assertTrue(spot_bc.overlaps_with(spot_ab))
        self.assertTrue(spot_cd.overlaps_with(spot_bc))
        self.assertTrue(spot_bc.overlaps_with(spot_cd))

    def test_spot_ordering(self):
        """Check that comparisons between unequal spots work as expected."""
        space_a = Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 0)
        space_b = Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 1)
        space_c = Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 0)
        space_d = Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1)
        spaces = [space_a, space_b, space_c, space_d]

        spot_tuples = []
        for space_1 in spaces:
            for space_2 in spaces:
                if (
                    space_1 != space_2
                    and (space_1.r == space_2.r or space_1.c == space_2.c)
                ):
                    spot_tuples.append((space_1, space_2))
        expected_sorted_spots = [
            Spot(*spot_tuple) for spot_tuple in sorted(spot_tuples)
        ]

        spots = [Spot(*spot_tuple) for spot_tuple in spot_tuples]
        random.shuffle(spots)
        spots.sort()
        self.assertListEqual(spots, expected_sorted_spots)

    def test_spot_frozen(self):
        """Test that spot objects are functionally immutable."""
        space_a = Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1)
        space_b = Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 1)
        spot_ab = Spot(space_a, space_b)
        with self.assertRaises(FrozenInstanceError):
            setattr(spot_ab, 'spaces', (space_b, space_a))

    def test_get_sorted_spots(self):
        """Test the function that generates all sorted spots for a puzzle."""
        space_a = Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 1)
        space_b = Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1)
        space_c = Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 0)
        space_d = Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 1)

        spaces = [space_a, space_b, space_c, space_d]
        regions = {}
        dominoes = [Domino(MIN_DOTS, MIN_DOTS), Domino(MAX_DOTS, MAX_DOTS)]

        puzzle = Puzzle(spaces, regions, dominoes)
        spots = get_sorted_spots(puzzle)

        expected_spots = [
            Spot(space_a, space_b), Spot(space_b, space_a),
            Spot(space_b, space_d), Spot(space_c, space_d),
            Spot(space_d, space_b), Spot(space_d, space_c),
        ]
        self.assertListEqual(spots, expected_spots)
