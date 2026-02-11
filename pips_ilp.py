"""A formulation of a Pips game as an integer linear program using PuLP."""

from collections.abc import Iterator
import dataclasses
import itertools as it

import pulp as pl

from basics import Domino, Space
from conditions import Equal, GreaterThan, LessThan, NotEqual, Number
from puzzle import Puzzle, Region


@dataclasses.dataclass(order=True, frozen=True, match_args=False, slots=True)
class Spot:
    """An ordered pair of adjacent spaces where a domino could be placed."""
    spaces: tuple[Space, Space]

    def __init__(self, space_1: Space, space_2: Space, /) -> None:
        if abs(space_2.r - space_1.r) + abs(space_2.c - space_1.c) != 1:
            raise ValueError('spot must be made up of two adjacent spaces')
        object.__setattr__(self, 'spaces', (space_1, space_2))

    def __iter__(self) -> Iterator[Space]:
        return iter(self.spaces)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{tuple(self)!r}'

    def __str__(self) -> str:
        return ':'.join(map(str, self))


def get_sorted_spots(puzzle: Puzzle) -> list[Spot]:
    """Return a sorted list of every spot where a domino could be placed."""
    spots: set[Spot] = set()
    for space in puzzle.iter_sorted_spaces():
        neighbors = (
            space.shift_by(delta_r=+1), space.shift_by(delta_r=-1),
            space.shift_by(delta_c=+1), space.shift_by(delta_c=-1),
        )
        for neighbor in neighbors:
            if neighbor in puzzle:
                spots.add(Spot(space, neighbor))
    return sorted(spots)


def create_placement_vars(
    puzzle: Puzzle, spots: list[Spot],
) -> dict[tuple[Domino, Spot], pl.LpVariable]:
    """Return a dict of ILP decision variables for the domino placements.

    The placement variables are binary flags for every (domino, spot) pairing:
    a value of 1 indicates that this domino is placed in this spot, while a
    value of 0 indicates that it is not.
    """
    placement_vars: dict[tuple[Domino, Spot], pl.LpVariable] = {}
    for domino in puzzle.iter_dominoes():
        for spot in spots:
            var_name = f'placement__{domino!s}__{spot!s}'
            ilp_var = pl.LpVariable(var_name, cat=pl.LpBinary)
            placement_vars[domino, spot] = ilp_var
    return placement_vars


def get_sorted_dots(puzzle: Puzzle) -> list[int]:
    """Return a sorted list of all dots values that appear on the dominoes.

    For some puzzles, this will not be the full range of values from 0 to 6.
    For instance, if none of the provided dominoes have a 4 on them, then we
    have no reason to consider the value of 4 as a possibility.
    """
    dots: set[int] = set()
    for domino in puzzle.iter_dominoes():
        dots.update(domino)
    return sorted(dots)


def create_dot_pattern_exprs(
    puzzle: Puzzle,
    spots: list[Spot],
    dots: list[int],
    placement_vars: dict[tuple[Domino, Spot], pl.LpVariable],
) -> dict[tuple[Space, int], pl.LpAffineExpression]:
    """Generate a dict of dot pattern expressions to help outline the ILP.

    These expressions are effectively "dependent variables" whose values are
    entirely determined by the placement variables. They are binary values for
    each (space, dot value) pair: a value of 1 indicates that this space is
    showing this dot value, and a value of 0 indicates that it is not.
    """
    dot_pattern_exprs = {
        (space, dot): pl.LpAffineExpression()  # Initialize as 0 expression
        for space in puzzle.iter_sorted_spaces() for dot in dots
    }
    for domino in puzzle.iter_dominoes():
        for spot in spots:
            for dot, space in zip(domino, spot, strict=True):
                dot_pattern_exprs[space, dot] += (
                    1 * placement_vars[domino, spot]
                )
    return dot_pattern_exprs


def create_dot_number_exprs(
    puzzle: Puzzle,
    dot_pattern_exprs: dict[tuple[Space, int], pl.LpAffineExpression],
) -> dict[Space, pl.LpAffineExpression]:
    """Generate a dict of dot number expressions to help outline the ILP.

    These expressions are effectively "dependent variables" whose values are
    entirely determined by the placement variables. Each of them is an integer
    corresponding to one space on the board, and its value is the number of
    dots showing in that space.
    """
    dot_number_exprs = {
        space: pl.LpAffineExpression()  # Initialize as 0 expression
        for space in puzzle.iter_sorted_spaces()
    }
    for (space, dot), dot_pattern_expr in dot_pattern_exprs.items():
        dot_number_exprs[space] += dot * dot_pattern_expr
    return dot_number_exprs


def abbreviate_region(region: Region) -> str:
    """Return a shorthand string abbreviation to stand for a board region."""
    first_space = next(iter(region))
    return f'Rg{first_space!s}'


@dataclasses.dataclass(eq=False, match_args=False, slots=True)
class PipsILP:
    """A PuLP problem together with dicts of variables and expressions."""
    problem: pl.LpProblem
    placement_vars: dict[tuple[Domino, Spot], pl.LpVariable]
    dot_pattern_exprs: dict[tuple[Space, int], pl.LpAffineExpression]
    dot_number_exprs: dict[Space, pl.LpAffineExpression]


def formulate_ilp(puzzle: Puzzle) -> PipsILP:
    """Construct an integer linear program corresponding to a Pips puzzle."""
    problem = pl.LpProblem("Pips_ILP")

    spots = get_sorted_spots(puzzle)
    placement_vars = create_placement_vars(puzzle, spots)

    dots = get_sorted_dots(puzzle)
    dot_pattern_exprs = create_dot_pattern_exprs(
        puzzle, spots, dots, placement_vars,
    )

    dot_number_exprs = create_dot_number_exprs(puzzle, dot_pattern_exprs)

    # Constraints: enforce that each domino is placed in exactly one spot
    for domino in puzzle.iter_dominoes():
        equation = (
            pl.lpSum(1 * placement_vars[domino, spot] for spot in spots) == 1
        )
        problem += (equation, f'use_domino__{domino}')

    # Constraints: each space must have one half of a domino occupying it
    for space in puzzle.iter_sorted_spaces():
        equation = (
            pl.lpSum(1 * dot_pattern_exprs[space, dot] for dot in dots) == 1
        )
        problem += (equation, f'cant_overlap__{space}')

    # Constraints: the colored region conditions specific to this puzzle
    for region in puzzle.iter_sorted_regions():
        condition = puzzle.get_condition(region)
        region_string = abbreviate_region(region)

        match condition:

            case Number(number):
                equation = (
                    pl.lpSum(dot_number_exprs[space] for space in region)
                    == number
                )
                problem += (equation, f'number_condition__{region_string}')

            case Equal():
                for space_1, space_2 in it.pairwise(region):
                    equation = (
                        dot_number_exprs[space_1] == dot_number_exprs[space_2]
                    )
                    problem += (
                        equation,
                        (
                            'equal_condition'
                            + f'__{region_string}__{space_1!s}__{space_2!s}'
                        ),
                    )

            case NotEqual():
                for dot in dots:
                    inequality = (
                        pl.lpSum(
                            dot_pattern_exprs[space, dot] for space in region
                        )
                        <= 1
                    )
                    problem += (
                        inequality,
                        f'not_equal_condition__{region_string}__{dot}',
                    )

            case GreaterThan(number):
                inequality = (
                    pl.lpSum(dot_number_exprs[space] for space in region)
                    >= number + 1  # Offset by 1 due to greater than or equal
                )
                problem += (
                    inequality, f'greater_than_condition__{region_string}',
                )

            case LessThan(number):
                inequality = (
                    pl.lpSum(dot_number_exprs[space] for space in region)
                    <= number - 1  # Offset by 1 due to less than or equal
                )
                problem += (
                    inequality, f'less_than_condition__{region_string}'
                )

            case _:
                raise TypeError(
                    f'unrecognized condition type: {type(condition)}'
                )

    return PipsILP(
        problem, placement_vars, dot_pattern_exprs, dot_number_exprs,
    )


if __name__ == '__main__':

    import sys
    from pathlib import Path

    _, arg_1 = sys.argv
    puz = Puzzle.parse(Path(arg_1).read_text(encoding='ascii'))
    ilp = formulate_ilp(puz)

    print(ilp.problem)
