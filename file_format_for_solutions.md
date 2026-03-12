# Pips Solution File Format

A Pips solution file consits of a single section made up of one or more move instructions separated by newlines. Each move instruction contains two parts separated by whitespace, the first indicating a domino and the second describing the location where that domino should be placed.

For example, the instruction `53 1,3:1,2` says that a domino with dot patterns 5 and 3 should be placed with its 5 in row 1, column 3 and its 3 in row 1, column 2. Note that the ordering of the two domino dots values and the two coordinate pairs are significant---the instruction `53 1,2:1,3` would flip the domino around by 180 degrees.
