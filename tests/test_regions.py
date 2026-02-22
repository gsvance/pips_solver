"""Unit tests for the functionality of Pips board regions."""

from dataclasses import FrozenInstanceError
import random
import unittest

from regions import (
    Region,
)
from spaces import (
    LEFTMOST_COLUMN,
    Space,
    TOPMOST_ROW,
)


class TestRegions(unittest.TestCase):
    """Test case for the Pips board regions."""

    def test_region_init(self):
        """Test that regions can be initialized correctly."""
        spaces = {
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 0),
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1),
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 1),
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 2),
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 3),
        }

        region = Region(spaces)
        self.assertListEqual(list(region.spaces), sorted(spaces))

        with self.assertRaisesRegex(ValueError, 'must be unique'):
            Region(list(spaces) + [list(spaces)[0]])
        with self.assertRaisesRegex(ValueError, 'at least one space'):
            Region([])

    def test_region_init_disconnected(self):
        """Test that regions enforce connectedness."""
        disconnected_spaces = [
            [
                Space(TOPMOST_ROW, LEFTMOST_COLUMN),
                Space(TOPMOST_ROW, LEFTMOST_COLUMN + 2),
            ],
            [
                Space(TOPMOST_ROW, LEFTMOST_COLUMN),
                Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN),
            ],
            [
                Space(TOPMOST_ROW, LEFTMOST_COLUMN),
                Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1),
            ],
            [
                Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN),
                Space(TOPMOST_ROW, LEFTMOST_COLUMN + 1),
            ],
        ]
        for disconnected in disconnected_spaces:
            with self.assertRaisesRegex(ValueError, 'must all be connected'):
                Region(disconnected)

    def test_region_repr(self):
        """Check that the region object's repr method works."""
        spaces = [
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 0),
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 1),
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1),
            Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 1),
            Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 0),
        ]
        expected_repr = 'Region(' + repr(sorted(spaces)) + ')'
        self.assertEqual(repr(Region(spaces)), expected_repr)

    def test_region_iter(self):
        """Test that regions can be iterated over."""
        spaces = [
            Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 0),
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 0),
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 0),
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1),
        ]
        self.assertListEqual(list(iter(Region(spaces))), sorted(spaces))

    def test_region_len(self):
        """Test that a region's length is the number of spaces in it."""
        spaces = [
            Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 0),
            Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 1),
            Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 2),
            Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 3),
            Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 4),
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 4),
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 4),
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 3),
        ]
        for length in range(1, len(spaces) + 1):
            region = Region(spaces[:length])
            self.assertEqual(len(region), length)

    def test_region_contains(self):
        """Check that the "in" operator works correctly with regions."""
        spaces = [
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 0),
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 0),
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 1),
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1),
        ]
        not_included = [
            Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 1),
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 2),
            Space(TOPMOST_ROW + 2, LEFTMOST_COLUMN + 2),
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 3),
        ]
        region = Region(spaces)
        for space in spaces:
            self.assertIn(space, region)
        for nope in not_included:
            self.assertNotIn(nope, region)

    def test_region_ordering(self):
        """Check that regions are ordered by spaces tuples as expected."""
        regions = []
        while len(regions) < 50:
            spaces = set()
            for _ in range(8):
                space = Space(
                    TOPMOST_ROW + random.randrange(4),
                    LEFTMOST_COLUMN + random.randrange(4),
                )
                spaces.add(space)
            try:
                region = Region(spaces)
            except ValueError as exc:
                if 'connected' in exc.args[0]:
                    continue
                assert False, 'failed to generate random regions'
            regions.append(region)
        regions.sort()
        for i in range(len(regions) - 1):
            tuple_1 = tuple(iter(regions[i]))
            tuple_2 = tuple(iter(regions[i + 1]))
            self.assertLessEqual(tuple_1, tuple_2)

    def test_region_frozen(self):
        """Check that region objects are indeed frozen."""
        region = Region([
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1),
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 2),
        ])
        with self.assertRaises(FrozenInstanceError):
            setattr(region, 'spaces', ())

    def test_region_overlaps_with(self):
        """Check that regions are able to detect whether they overlap."""
        region_row_0 = Region([
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 0),
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 1),
        ])
        region_row_1 = Region([
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 0),
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1),
        ])
        region_col_0 = Region([
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 0),
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 0),
        ])
        region_col_1 = Region([
            Space(TOPMOST_ROW + 0, LEFTMOST_COLUMN + 1),
            Space(TOPMOST_ROW + 1, LEFTMOST_COLUMN + 1),
        ])
        regions = [region_row_0, region_row_1, region_col_0, region_col_1]

        for region in regions:
            self.assertTrue(region.overlaps_with(region))

        self.assertTrue(region_row_0.overlaps_with(region_col_0))
        self.assertTrue(region_row_0.overlaps_with(region_col_1))
        self.assertFalse(region_row_0.overlaps_with(region_row_1))

        self.assertTrue(region_row_1.overlaps_with(region_col_0))
        self.assertTrue(region_row_1.overlaps_with(region_col_1))
        self.assertFalse(region_row_1.overlaps_with(region_row_0))

        self.assertTrue(region_col_0.overlaps_with(region_row_0))
        self.assertTrue(region_col_0.overlaps_with(region_row_1))
        self.assertFalse(region_col_0.overlaps_with(region_col_1))

        self.assertTrue(region_col_1.overlaps_with(region_row_0))
        self.assertTrue(region_col_1.overlaps_with(region_row_1))
        self.assertFalse(region_col_1.overlaps_with(region_col_0))
