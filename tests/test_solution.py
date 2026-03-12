"""Unit tests for the Pips puzzle solution class."""

from pathlib import Path
import tempfile
import unittest

from dominoes import (
    Domino,
    MAX_DOTS,
    MIN_DOTS,
)
from solutions import Solution
from spaces import (
    LEFTMOST_COLUMN,
    Space,
    TOPMOST_ROW,
)
from spots import Spot


class TestSolution(unittest.TestCase):
    """Test case for the Pips solution class."""

    def test_solution_init(self):
        """Check that solution objects can be initialized correctly."""
        solution = Solution()
        self.assertListEqual(solution.moves, [])

    def test_solution_add_move(self):
        """Check that adding moves to a solution works correctly."""
        domino_a = Domino(MIN_DOTS, MAX_DOTS)
        domino_b = Domino(MIN_DOTS, MIN_DOTS)
        domino_c = Domino(MAX_DOTS, MAX_DOTS)

        space_a = Space(TOPMOST_ROW, LEFTMOST_COLUMN)
        space_b = space_a.shift_by(delta_c=1)
        space_c = space_a.shift_by(delta_r=1)
        space_d = space_c.shift_by(delta_c=1)
        space_e = space_b.shift_by(delta_c=1)
        space_f = space_d.shift_by(delta_c=1)

        solution = Solution()

        solution.add_move(domino_a, Spot(space_a, space_b))
        solution.add_move(domino_b, Spot(space_d, space_c))

        self.assertListEqual(
            solution.moves,
            [
                (domino_a, Spot(space_a, space_b)),
                (domino_b, Spot(space_d, space_c)),
            ],
        )

        with self.assertRaisesRegex(ValueError, 'duplicate domino'):
            solution.add_move(domino_a, Spot(space_e, space_f))

        with self.assertRaisesRegex(ValueError, 'overlapping spot'):
            solution.add_move(domino_c, Spot(space_b, space_d))

    def test_solution_iter(self):
        """Test that solution objects can be iterated over."""
        domino_a = Domino(MAX_DOTS, MAX_DOTS)
        domino_b = Domino(MAX_DOTS, MIN_DOTS)

        space_a = Space(TOPMOST_ROW, LEFTMOST_COLUMN)
        space_b = space_a.shift_by(delta_c=1)
        space_c = space_a.shift_by(delta_r=1)
        space_d = space_a.shift_by(delta_r=1, delta_c=1)

        solution = Solution()

        solution.add_move(domino_a, Spot(space_a, space_c))
        solution.add_move(domino_b, Spot(space_d, space_b))

        self.assertListEqual(
            list(iter(solution)),
            [
                (domino_a, Spot(space_a, space_c)),
                (domino_b, Spot(space_d, space_b)),
            ],
        )

    def test_solution_save_file(self):
        """Test saving a solution file to a temporary directory."""
        domino_a = Domino(MIN_DOTS, MAX_DOTS)
        domino_b = Domino(MAX_DOTS, MAX_DOTS)

        space_a = Space(TOPMOST_ROW, LEFTMOST_COLUMN)
        space_b = space_a.shift_by(delta_c=1)
        space_c = space_b.shift_by(delta_c=1)
        space_d = space_c.shift_by(delta_r=1)

        solution = Solution()
        solution.add_move(domino_a, Spot(space_a, space_b))
        solution.add_move(domino_b, Spot(space_d, space_c))

        expected_file_contents = (
            domino_a.as_terse_string() + ' '
            + str(Spot(space_a, space_b)) + '\n'
            + domino_b.as_terse_string() + ' '
            + str(Spot(space_d, space_c)) + '\n'
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            save_file_path = temp_dir_path / 'test_solution_save_file.txt'

            solution.save_file(save_file_path)

            self.assertEqual(
                save_file_path.read_text(encoding='ascii'),
                expected_file_contents,
            )

    def test_solution_load_file(self):
        """Test saving a solution file to a temporary directory."""
        domino_a = Domino(MAX_DOTS, MAX_DOTS)
        domino_b = Domino(MAX_DOTS, MIN_DOTS)

        space_a = Space(TOPMOST_ROW, LEFTMOST_COLUMN)
        space_b = space_a.shift_by(delta_c=1)
        space_c = space_b.shift_by(delta_c=1)
        space_d = space_c.shift_by(delta_r=1)

        solution = Solution()
        solution.add_move(domino_a, Spot(space_a, space_b))
        solution.add_move(domino_b, Spot(space_d, space_c))

        contents_for_file = (
            domino_a.as_terse_string() + ' '
            + str(Spot(space_a, space_b)) + '\n'
            + domino_b.as_terse_string() + ' '
            + str(Spot(space_d, space_c)) + '\n'
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            load_file_path = temp_dir_path / 'test_solution_load_file.txt'

            load_file_path.write_text(contents_for_file, encoding='utf-8')
            loaded_solution = Solution.load_file(load_file_path)

            self.assertListEqual(loaded_solution.moves, solution.moves)
