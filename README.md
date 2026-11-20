# Lollipop CSP Solver

Aufgabenblatt 2 — Constraint Satisfaction Problems
Künstliche Intelligenz: Grundlagen und Anwendungen, TU Berlin, WS 2026
Gruppe `<GRUPPENNUMMER>`

A CSP solver for **Lollipop** puzzles (<https://de.puzzle-lollipops.com>), evaluated with four
different search techniques across six puzzle instances of varying size and difficulty.

---

## The puzzle

A lollipop occupies exactly two orthogonally adjacent cells: a **head** (circle) and a **stick**
(line) that runs into the head. Some heads and sticks are given; they must be completed into
lollipops, and further lollipops may have to be added. There is no target number of lollipops.

Three rules:

1. **Every head and every stick belongs to a lollipop.** A head needs exactly one stick pointing
   into it; a stick needs exactly one head on the side its orientation points to.
2. **Lollipops must not touch orthogonally.** Diagonal contact is allowed. Because a lollipop is
   only two cells, rules 1 and 2 together reduce to: *every non-empty cell has exactly one
   non-empty orthogonal neighbour, and that neighbour is its partner.*
3. **Parts of the same type must not see each other** along a row or column. Empty cells do not
   block line of sight — only non-empty cells do. Equivalently: in the sequence of non-empty cells
   of a line, no two consecutive entries may have the same type.

---

## Requirements

- Python 3.10+
- `numpy`

```bash
python -m venv .venv
source .venv/bin/activate
pip install numpy
```

## Running

From the project root:

```bash
python scripts/run1.py
```

This loads every instance in `instances/`, builds the CSP, runs the solver and verifies each
solution with the independent validator.

---

## CSP representation

| | |
|---|---|
| **Variables** | one per grid cell, `(i, j)` |
| **Domain** | `{EMPTY, HEAD, STICK_H, STICK_V}` |
| **Given cells** | singleton domain — this is node consistency (1-consistency), applied at load time |
| **Binary constraints** | between orthogonally adjacent cells: the only legal non-empty pair is a head plus the stick belonging to that axis |
| **Higher-arity constraints** | "exactly one non-empty neighbour" (cell + its ≤4 neighbours), and the line-of-sight rule (whole row / column) |

An instance file is converted into a CSP by `parser.load_domains()`: every given cell gets a
one-element domain, every other cell the full domain.

---

## Instance format

Plain text, one line per row, no header. Dimensions are derived from the file.

| char | meaning |
|---|---|
| `.` | not given (in a solution file: empty) |
| `O` | head |
| `-` | horizontal stick |
| `\|` | vertical stick |

```
.....-
O.-...
......
.-....
....-.
O.....
```

The dots are placeholders so that the position of a character equals its column index, and so the
file can be compared against a screenshot of the original puzzle by eye.

---

## Project structure

```
data.py          CellType enum: EMPTY, HEAD, STICK_H, STICK_V
parser.py        load_grid() / load_domains() / to_string()
constrains.py    constraint layer for PARTIAL boards, used during search
validator.py     validate() - checks a COMPLETE board, independent implementation
solver.py        the search techniques
scripts/         runnable entry points
instances/       puzzle instances
tests/           test boards and unit tests
```

### Why two implementations of the rules

`validator.py` was written separately from `constrains.py` and checks a finished board from
scratch. Every solution returned by the solver is passed through it. Because the two
implementations do not share code, agreement between them is meaningful evidence that a returned
board really is a solution — the solver does not grade its own work.

---

## Search technique

**Plain backtracking** — fixed assignment order, no constraint propagation, no heuristic.

Cells are assigned row-major, from the top-left to the bottom-right corner. For each cell the
values are tried in the order `EMPTY`, `HEAD`, `STICK_H`, `STICK_V`, skipping any value that is
not in the cell's domain; a given cell therefore has exactly one candidate. After every
assignment the constraints are checked, and a cell is reset to `None` as soon as a value leads
nowhere.

## Console output

For every instance the program prints the problem instance, the solution it found, and the result
of validating that solution independently.

---

## Implementation notes

Three decisions that the rest of the code depends on:

**`None` is not `EMPTY`.** In the working grid, `None` means *not decided yet* and
`CellType.EMPTY` means *decided to be blank*. The two behave oppositely in both rules: an `EMPTY`
neighbour can never become a partner and never blocks line of sight, while a `None` one may still
become either. Merging them makes the solver reject every head at the moment it is placed. On
backtrack a cell is reset to `None`, never to `EMPTY`.

**Constraints reject only certain violations.** `check()` reports a conflict only when no future
assignment could repair it — a head without a stick passes as long as one of its neighbours is
still undecided. Being too permissive costs search time; being too strict loses valid solutions.

**Constraint checks are scoped.** `check()` runs after every assignment, so it inspects only what
the new value could have broken: the written cell, its four neighbours (their partner counts
change too), its row and its column. The rest of the board was already consistent at the previous
check.