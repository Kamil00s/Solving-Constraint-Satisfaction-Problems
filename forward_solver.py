from constraints import E, allowed, neighbours


def _has_assigned_partner(i, j, grid, n) -> bool:
    """Return True if non-empty cell (i, j) already has an assigned orthogonal partner."""
    val = grid[i][j]
    if val is None or val == E:
        return False
    for ni, nj, stick in neighbours(i, j, n):
        nb = grid[ni][nj]
        if nb is not None and nb != E and allowed(val, nb, stick):
            return True
    return False


def prune(i, j, value, grid, domains, n):
    """Forward-checking domain pruning on unassigned orthogonal neighbours of (i, j).

    Removes values `v` that violate direct partner compatibility with `value` or
    would give an already-paired non-empty cell a second orthogonal partner.
    Returns `(trail, is_consistent)` so removed values can be undone on backtrack.
    """
    trail = []
    already_paired = _has_assigned_partner(i, j, grid, n)

    for ni, nj, stick in neighbours(i, j, n):
        if grid[ni][nj] is not None:
            continue

        domain = domains[(ni, nj)]
        removed = set()
        for v in domain:
            if not allowed(value, v, stick):
                removed.add(v)
            elif already_paired and value != E and v != E and allowed(value, v, stick):
                # Prevent a second orthogonal partner once (i, j) is already paired.
                removed.add(v)

        if removed:
            domain -= removed
            trail.append(((ni, nj), removed))
            if not domain:
                # Domain wipeout: immediate dead end for forward checking.
                return trail, False

    return trail, True


def restore(domains, trail):
    """Restore pruned domain values recorded in `trail` when backtracking."""
    for cell, rem in trail:
        domains[cell].update(rem)