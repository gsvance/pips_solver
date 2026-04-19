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

A Pips board is made up of spaces, which can be modeled as $B \subset \mathbb{N} \times \mathbb{N}$, i.e., each $b \in B$ looks like $(r, c)$, where $r$ is the row index and $c$ is the column index. The board contains zero or more regions $R_i \subseteq B$ for $i \in \\{ 1, \ldots, k \\}$, each of which is associated with some condition $C_i$ that must be satisfied. The set of dominoes is $D \subseteq \\{ 0, 1, \ldots, 6 \\} \times \\{ 0, 1, \ldots, 6 \\}$, where any $d \in D$ might look like $(u, v)$. Note that in order to have a non-trivial puzzle with any hope of a solution, we must have $ 0 < | B | = 2 | D | $.

We can now construct the set $S \subseteq B \times B$ of spots where a domino might be placed. Let the set of spots be

$$ S = \\{ (b_1, b_2) : |r_2 - r_1| + |c_2 - c_1| = 1 \\} , $$

where $b_1, b_2 \in B$, $b_1 = (r_1, c_1)$, $b_2 = (r_2, c_2)$, and the equality enforces that each pair of spaces are horizontally or vertically adjacent. From here, we can create our binary decision variables $x_{ds}$, where

$$ x_{ds} \in \\{ 0, 1 \\} , d \in D , s \in S $$

and $x_{ds}$ indicates the decision to place a domino in a spot. If $x_{ds} = 1$, then domino $d$ has been placed in spot $s$, and if $x_{ds} = 0$, then it has not. Having defined these placement variables, we can immediately move into our first set of constraints. For each $d \in D$, we have

$$ \sum_{s \in S} x_{ds} = 1 , $$

corresponding to the fact that every domino must be used and no domino can be placed in more than one spot. Next, we define another set of variables $y_{bw}$, dot pattern expressions dependent on the placement variables. For each space $b \in B$ and dot value $w \in \\{ 0, 1, \ldots, 6 \\}$, we have

$$ y_{bw} = \sum_{d \in D} \sum_{s \in S} \[ f(u, w) g(b_1, b) + f(v, w) g(b_2, b) \] x_{ds} $$

with $d = (u, v)$, $s = (b_1, b_2)$, and functions

$$ f(u, v) = \left\\{
\begin{array}{ll}
    1 & \quad \text{if} \  u = v \\
    0 & \quad \text{otherwise} \\
\end{array} 
\right. $$

and

$$ g(b_1, b_2) = \left\\{
\begin{array}{ll}
    1 & \quad \text{if} \  b_1 = b_2 \\
    0 & \quad \text{otherwise} \\
\end{array} 
\right. $$

to indicate when the spot's spaces and domino's dots match the $y_{bw}$ subscripts. The ultimate result is that $y_{bw}$ becomes a binary expression entirely dependent on the values of $x_{ds}$. If $y_{bw} = 1$, then space $b$ displays dot value $w$, and if $y_{bw} = 0$, then it does not. To keep the range of these dot pattern expressions in check, we add constraints for each $b$ like

$$ \sum_{w = 0}^6 y_{bw} = 1 , $$

which enforce that every space on the board must have a domino dot value and no two dominoes can overlap on any given space. Finally, for each space, we also define the dot value variables $z_b$ as

$$ z_b = \sum_{w = 0}^6 y_{bw} w , $$

which contains the integer value of the domino dots in space $b$. Having defined $x_{ds}$, $y_{bw}$, and $z_b$, we can now tackle the constraints corresponding to the region conditions from the game board. For each $i \in \\{ 1, \ldots, k \\}$,

- If $C_i$ is a number condition with total $n$, we add the constraint that

$$ \sum_{b \in R_i} z_b = n . $$

- If $C_i$ is an equal condition, then we add equality constraints for each $b_1, b_2 \in R_i$. In practice, the transitivity of equality means that most of these constraints are superfluous and can be omitted, but each one looks like

$$ z_{b_1} - z_{b_2} = 0 . $$

- If $C_i$ is a not equal condition, then for each $w \in \\{ 0, 1, \ldots, 6 \\}$ we add a constraint

$$ \sum_{b \in R_i} y_{bw} \leq 1 . $$

- If $C_i$ is a less than condition with value $n$, we add a constraint

$$ \sum_{b \in R_i} z_b \leq n - 1 $$

- If $C_i$ is a greater than condition with value $n$, we add a constraint

$$ \sum_{b \in R_i} z_b \geq n + 1 $$

These constraints and variables define the Pips problem, since we have no objective function being optimized for.

## Currently included here

- A series of Python classes for representing Pips concepts including puzzles, dominoes, board spaces and regions, conditions, etc.
- Functions for turning a puzzle object into a PuLP `LpProblem` object and solving it
- Descriptions of the expected ASCII file formats for Pips puzzles and solutions
- Scripts for turning a solved LP into a list of solving instructions or a visual representation of the solved puzzle
- A series of unit tests for the various Pips classes
