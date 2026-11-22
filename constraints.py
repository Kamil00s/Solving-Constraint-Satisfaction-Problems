from data import CellType

E = CellType.EMPTY
H = CellType.HEAD
SH = CellType.STICK_H
SV = CellType.STICK_V

# Orthogonal directions: (delta_row, delta_col, stick_type_for_that_axis)
DIRS = (
    (-1, 0, SV),  # up    - vertical lollipop stick
    (1, 0, SV),   # down  - vertical lollipop stick
    (0, -1, SH),  # left  - horizontal lollipop stick
    (0, 1, SH),   # right - horizontal lollipop stick
)


def neighbours(i, j, n):
    """Yield in-bounds orthogonal neighbours (r, c, stick_type) for cell (i, j) on an n x n grid."""
    for di, dj, stick in DIRS:
        ni, nj = i + di, j + dj
        if 0 <= ni < n and 0 <= nj < n:
            yield ni, nj, stick


def allowed(a, b, stick) -> bool:
    """Binary compatibility constraint between two orthogonally adjacent cells along `stick` orientation.

    - EMPTY is compatible with any cell type (no direct partner conflict).
    - Two non-empty cells form a valid pair iff one is HEAD and the other matches `stick`.
    """
    if a == E or b == E:
        return True
    if a == H and b == stick:
        return True
    if b == H and a == stick:
        return True
    return False


def line_ok(line) -> bool:
    """Line-of-sight constraint (Rule 3) on a row or column.

    Ignores EMPTY cells (which do not block line of sight) and rejects consecutive
    assigned non-empty cells of the same type. Undecided (`None`) cells remain
    permissive until future assignments determine intermediate cells.
    """
    seq = [cell for cell in line if cell != CellType.EMPTY]
    for a, b in zip(seq, seq[1:]):
        if a is not None and a == b:
            return False
    return True


def cell_ok(i, j, grid, n) -> bool:
    """Local partner & non-touching constraint (Rules 1 & 2) for assigned cell (i, j).

    A non-empty cell must not have more than one non-empty orthogonal neighbour
    (preventing touching lollipops), must pair only with a compatible neighbour,
    and must still have at least one assigned partner or undecided (`None`) neighbour.
    """
    value = grid[i][j]
    if value is None:
        return True

    filled = 0
    unknown = 0
    for ni, nj, stick in neighbours(i, j, n):
        neighbour = grid[ni][nj]
        if neighbour is None:
            unknown += 1
        elif neighbour != E:
            if not allowed(value, neighbour, stick):
                return False
            filled += 1

    if value == E:
        return True
    if filled > 1:
        return False
    if filled == 1:
        return True
    return unknown > 0


def check(i, j, grid, n) -> bool:
    """Scoped consistency check after assigning cell (i, j).

    Verifies cell (i, j), its orthogonal neighbours (whose partner counts change),
    and the full row `i` and column `j` for line-of-sight validity.
    """
    if not cell_ok(i, j, grid, n):
        return False
    for ni, nj, _ in neighbours(i, j, n):
        if not cell_ok(ni, nj, grid, n):
            return False
    return line_ok(grid[i]) and line_ok(grid[:, j])