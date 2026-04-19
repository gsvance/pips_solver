# Pips Solver

A collection of Python code for solving [Pips](https://www.nytimes.com/games/pips) puzzles

## About this project

The `pips_solver` repo is primarily an answer to question of whether Pips puzzles can be solved by rephrasing them as linear programming problems. After reading an [example](https://www.coin-or.org/PuLP/CaseStudies/a_sudoku_problem.html) in the PuLP documentation that solved a Sudoku puzzle by formulating it as an LP, I wondered whether the same approach could be used to find solutions for Pips. As it turns out, the rules of Pips are quite amenable to this sort of formulation, and the game can therefore be solved by any LP solver that allows integer variables.

A Pips puzzle to be solved is first be stored in a specially formatted ASCII file. When the puzzle file is parsed, Pips game concepts are modeled using a series of Python classes. Next, the code transitions to using [PuLP](https://pypi.org/project/PuLP/) for formulating the LP, and finally calls [HiGHS](https://pypi.org/project/highspy/) to actually solve it.

## What this repo is not

- A Pips clone. This repo does not include any sort of playable Pips game.
- An archive of Pips puzzles. All the included example puzzles are original.
- Officially associated with the New York Times or NYT Games in any way.

## Mathematical formulation

A Pips board is made up of spaces, which can be modeled as $B \subset \mathbb{N} \times \mathbb{N}$, i.e., each $b \in B$ looks like $(r, c)$, where $r$ is the row index and $c$ is the column index. The board contains zero or more regions $R_i \subseteq B$ for $i \in \{1, \ldots, k\}$, each of which is associated with some condition $C_i$ that must be satisfied. The set of dominoes is $D \subseteq \{0, 1, \ldots, 6\} \times {0, 1, \ldots, 6}$, where any $d \in D$ might look like $(u, v)$.

## Currently included here

- A series of Python classes for representing Pips concepts including puzzles, dominoes, board spaces and regions, conditions, etc.
- Functions for turning a puzzle object into a PuLP `LpProblem` object and solving it
- Descriptions of the expected ASCII file formats for Pips puzzles and solutions
- Scripts for turning a solved LP into a list of solving instructions or a visual representation of the solved puzzle
- A series of unit tests for the various Pips classes
