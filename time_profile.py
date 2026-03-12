#!/usr/bin/env python3
"""The script measures and reports the distribution of puzzle solving times.

When called on the command line, pass in the path to a directory containing
Pips puzzle files as the first argument.
"""

from collections.abc import Iterable
from pathlib import Path
import sys
import time

from pips_ilp import formulate_ilp
from puzzle import Puzzle


def find_puzzle_files(puzzles_dir: Path) -> list[Path]:
    """Accept a directory path and return a list of Pips puzzle files."""
    assert puzzles_dir.is_dir()
    return list(puzzles_dir.glob('*.txt'))


def measure_puzzle_solving_times(puzzle_path: Path) -> dict[str, float]:
    """Measure the time needed to solve a Pips puzzle from start to finish."""
    time_0 = time.perf_counter()
    puzzle_text = puzzle_path.read_text(encoding='ascii')
    time_1 = time.perf_counter()
    puzzle = Puzzle.parse(puzzle_text)
    time_2 = time.perf_counter()
    puzzle_ilp = formulate_ilp(puzzle)
    time_3 = time.perf_counter()
    solution = puzzle_ilp.solve()
    time_4 = time.perf_counter()
    assert solution is not None

    return {
        'file reading time': time_1 - time_0,
        'puzzle parsing time': time_2 - time_1,
        'ILP formulation time': time_3 - time_2,
        'solver + cleanup time': time_4 - time_3,
        'solver time only': float(puzzle_ilp.problem.solutionTime),
        'cleanup time only': (time_4 - time_3) - puzzle_ilp.problem.solutionTime,
        'complete file-to-solution time': time_4 - time_0,
    }


def average(nums: Iterable[float]) -> float:
    """Compute the arithmetic mean of a sequence of floats."""
    nums_list = list(nums)
    return sum(nums_list) / len(nums_list)


def median(nums: Iterable[float]) -> float:
    """Compute the median of a sequence of floats by sorting."""
    nums_list = sorted(nums)
    if len(nums_list) % 2 == 1:
        middle = len(nums_list) // 2
        return nums_list[middle]
    middle_right = len(nums_list) // 2
    middle_left = middle_right - 1
    return (nums_list[middle_left] + nums_list[middle_right]) / 2.0


def ms(x: float) -> str:
    """Format a floating number of seconds as a string in milliseconds."""
    return f'{x*1000:,.1f} ms'


def print_report(times: list[dict[str, float]]) -> None:
    """Print a statistical report for the user with puzzle solve times."""
    assert len(times) > 0
    print()
    print('Total Puzzles Solved:', len(times))
    print()
    report_keys = list(times[0].keys())
    for report in times:
        assert list(report.keys()) == report_keys
    for key in report_keys:
        print('Measured Quantity:', key)
        print('   Best Case:', ms(min(report[key] for report in times)))
        print('     Average:', ms(average(report[key] for report in times)))
        print('      Median:', ms(average(report[key] for report in times)))
        print('  Worst Case:', ms(max(report[key] for report in times)))
        print()


def main(puzzles_dir: Path) -> None:
    """Find puzzles in the directory, solve them, and then report runtimes."""
    puzzle_paths = find_puzzle_files(puzzles_dir)
    times: list[dict[str, float]] = []
    for puzzle_path in puzzle_paths:
        times.append(measure_puzzle_solving_times(puzzle_path))
    print_report(times)


if __name__ == '__main__':
    _, arg_1 = sys.argv
    main(Path(arg_1))
