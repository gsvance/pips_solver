# Pips Solver

A collection of Python code for solving [Pips](https://www.nytimes.com/games/pips) puzzles

## About this project

The `pips_solver` repo is primarily an answer to question of whether Pips puzzles can be solved by rephrasing them as linear programming problems. After reading an [example](https://www.coin-or.org/PuLP/CaseStudies/a_sudoku_problem.html) in the PuLP documentation that solved a Sudoku puzzle by formulating it as an LP, I wondered whether the same approach could be used to find solutions for Pips. As it turns out, the rules of Pips are quite amenable to this sort of formulation, and the game can therefore be solved by any LP solver that permits integer variables.

Any Pips puzzle to be solved is first stored in a specially formatted ASCII input file. The code parses the puzzle file and then uses a series of Python classes to model the Pips game concepts. Next, it transitions to using [PuLP](https://pypi.org/project/PuLP/) for formulating the LP, and then finally calls [HiGHS](https://pypi.org/project/highspy/) to actually solve the problem. The mathematical formulation used to turn Pips into an LP is detailed at the bottom of this readme.

Is this the most efficient way that a computer could be made to solve Pips puzzles? Probably not. Are there more specialized kinds of algorithms that could be tailored to exactly this problem and used to solve it more quickly? Almost certainly. But that's not what this repo is about. As a matter of fact...

## What this repo is not

- A Pips clone. The code here does not implement any sort of playable Pips game.
- An archive of past Pips puzzles. All the included example puzzles are original.
- Officially associated with the New York Times or NYT Games in any way.

## Currently included here

- A series of Python classes for representing Pips concepts including puzzles, dominoes, board spaces and regions, conditions, etc.
- Functions for turning a Pips puzzle object into a PuLP `LpProblem` object and solving it
- Descriptions of the expected ASCII file formats for Pips puzzles and solutions
- Scripts for turning a solved LP into a list of solving instructions or a visual representation of the solved puzzle
- A series of unit tests for validating the various Pips classes

## Mathematical formulation

A Pips board is made up of spaces, which can be modeled as $B \subset \mathbb{N} \times \mathbb{N}$, i.e., each $b \in B$ looks like $(r, c)$, where $r$ is the row index and $c$ is the column index. The board contains zero or more regions $R_i \subseteq B$ for $i \in \\{ 1, \ldots, k \\}$, each of which is associated with some condition $C_i$ that must be satisfied. The set of dominoes is $D \subseteq \\{ 0, \ldots, 6 \\} \times \\{ 0, \ldots, 6 \\}$, where any $d \in D$ might look like $(v_1, v_2)$. Note that in order to have a non-trivial puzzle with any hope of a solution, we must have $0 < |B| = 2 |D| $.

We can now construct the set $S \subseteq B \times B$ of spots where a domino might possibly be placed. Let the set of spots be defined as

$$ S = \\{ (b_1, b_2) : |r_2 - r_1| + |c_2 - c_1| = 1 \\} , $$

where $b_1, b_2 \in B$, $b_1 = (r_1, c_1)$, $b_2 = (r_2, c_2)$, and the taxicab distance formula specifies that each pair of spaces are either horizontally or vertically adjacent. From here, we can create our binary decision variables $x_{ds}$, where

$$ x_{ds} \in \\{ 0, 1 \\} , d \in D , s \in S $$

and $x_{ds}$ indicates the decision to place a domino in a spot. If $x_{ds} = 1$, then domino $d$ has been placed in spot $s$, and if $x_{ds} = 0$, then it has not. Having defined these "placement variables," we can immediately move on to our first set of constraints. For each $d \in D$, we have

$$ \sum_{s \in S} x_{ds} = 1 , $$

corresponding to the fact that every domino must be used and no domino can be placed in more than one spot. Next, we define another set of variables $y_{bv}$, "dot pattern expressions" that are entirely dependent on the placement variables. For each space $b \in B$ and dot value $u \in \\{ 0, \ldots, 6 \\}$, we have

$$ y_{bv} = \sum_{d \in D} \sum_{s \in S} \[ f(v_1, v) f(b_1, b) + f(v_2, v) f(b_2, b) \] x_{ds} $$

with $d = (v_1, v_2)$, $s = (b_1, b_2)$, and function

$$ f(p, q) = \left\\{
\begin{array}{ll}
    1 & \quad \text{if} \  p = q \\
    0 & \quad \text{otherwise} \\
\end{array}
\right. . $$

to indicate when the spot's spaces and domino's dot values match the $y_{bv}$ subscripts. The result is that $y_{bv}$ becomes a binary expression that is dependent on the values of $x_{ds}$. If $y_{bv} = 1$, then space $b$ displays the dot value $v$, and if $y_{bv} = 0$, then it does not. To keep the range of these dot pattern expressions in check, we add constraints for each $b$ like

$$ \sum_{v = 0}^6 y_{bv} = 1 , $$

which enforce that every space on the board must have a domino dot value and no two dominoes can overlap on any given space. Finally, for each space, we also define the "dot value" expressions using variables $z_b$ as

$$ z_b = \sum_{v = 0}^6 v y_{bv} , $$

which contain the integer value of the domino dots in each space $b$. Having defined $x_{ds}$, $y_{bv}$, and $z_b$, we can now tackle the constraints corresponding to the region conditions from the game board. For each $i \in \\{ 1, \ldots, k \\}$,

- If $C_i$ is a "number" condition with value $n$, we add the constraint that

$$ \sum_{b \in R_i} z_b = n . $$

- If $C_i$ is an "equal" condition, then we add equality constraints for each $b_1, b_2 \in R_i$. In practice, the transitivity of equality means that most of these constraints are superfluous and can be omitted from the LP, but each one looks like

$$ z_{b_1} - z_{b_2} = 0 . $$

- If $C_i$ is a "not equal" condition, then for each $v \in \\{ 0, \ldots, 6 \\}$ we add a constraint

$$ \sum_{b \in R_i} y_{bv} \leq 1 . $$

- If $C_i$ is a "less than" condition with value $n$, we add a constraint

$$ \sum_{b \in R_i} z_b \leq n - 1 $$

- If $C_i$ is a "greater than" condition with value $n$, we add a constraint

$$ \sum_{b \in R_i} z_b \geq n + 1 $$

These constraints and variables completely define the Pips LP, since we have no objective function to optimize. Like the Sudoku example, we are interested only in an assignment of ones and zeros to the decision variables $x_{ds}$ that satisfies all constraints.
