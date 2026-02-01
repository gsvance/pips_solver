# Pips Puzzle File Format

The Pips puzzle files are made up of three sections, separated by blank lines, i.e., the string `'\n\n'`. Note that section 1 may include blank lines as part of its content, so sections 2 and 3 are identified by reading the file from the bottom up.

## 1. ASCII Board Layout

This section consists of ASCII art showing the layout of the Pips game board. Space characters indicate areas where there is nothing, and any non-whitespace characters indicate game spaces where domino halves can be placed. Spaces that exist as part of the same one colored region should always use the same character.

I like to use successive letters of the alphabet for colored regions (e.g., `A`, `B`, `C`, etc.) and `.` characters for spaces without conditions, but the format allows you to use any ASCII characters that are not whitespace.

## 2. Colored Region Conditions

This section specifies the actual game conditions on each region from the board layout section. There is one condition per line, starting with the region's character followed by a space and then a string for the condition, such as:

- `10`
- `=`
- `=/=`
- `>6`
- `<12`

Any non-whitespace characters appearing in section 1 that do not appear in this section are assumed to be game board spaces without conditions. It is an error to specify more than one condition for the same region, or to specify a condition for a region that does not exist in section 1.

## 3. List of Dominoes

In this section, list all the available dominoes as two-digit string separated by whitespace. They can appear across multiple lines, but do not include blank lines.

## File Format Limitations

This file format expects all three sections to be non-empty, so it is impossible to represent an empty puzzle, i.e., a puzzle with zero game board spaces and zero dominoes. This isn't much of a limitation, since a Pips puzzle without dominoes would be either be impossible or an instant win.

A slightly more important consequence is that this file format is also unable to represent Pips puzzles that have zero regions. Solving such a puzzle would only involve placing the dominoes onto the board spaces without any other requirements, but it would still be a valid puzzle. An equivalent puzzle could be represented by adding one region with an always-satisfied condition, e.g., an `=` region made up of only one space.
