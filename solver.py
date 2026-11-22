from collections import deque
import time
import numpy as np

from constraints import E, allowed, check, neighbours
from data import CellType
from forward_solver import prune, restore

# Fixed candidate value order for deterministic baseline search.
VALUES = (CellType.EMPTY, CellType.HEAD, CellType.STICK_H, CellType.STICK_V)


def _has_support(vx, dom_y, stick) -> bool:
    """Return True if value `vx` has at least one arc-consistent support `vy` in `dom_y`."""
    return any(allowed(vx, vy, stick) for vy in dom_y)


def ac3(domains, grid, n, queue=None):
    """Enforce arc consistency (AC-3) over unassigned variables and record domain changes.

    Used both for initial consistency before search and during search to propagate
    binary partner/axis constraints across neighbouring domains.
    """
    trail = []
    if queue is None:
        work_queue = deque()
        for i in range(n):
            for j in range(n):
                if grid[i][j] is not None:
                    continue
                for ni, nj, stick in neighbours(i, j, n):
                    if grid[ni][nj] is None:
                        work_queue.append(((i, j), (ni, nj), stick))
    else:
        work_queue = deque(queue)

    in_queue = set(work_queue)

    while work_queue:
        (xi, xj), (yi, yj), stick = work_queue.popleft()
        in_queue.discard(((xi, xj), (yi, yj), stick))

        if grid[xi][xj] is not None or grid[yi][yj] is not None:
            continue

        dom_x = domains[(xi, xj)]
        dom_y = domains[(yi, yj)]
        unsupported = {vx for vx in dom_x if not _has_support(vx, dom_y, stick)}

        if unsupported:
            dom_x -= unsupported
            trail.append(((xi, xj), unsupported))
            if not dom_x:
                # Wipeout detected: current partial assignment cannot succeed.
                return trail, False

            # Re-enqueue arcs pointing into (xi, xj) from other unassigned neighbours.
            for pi, pj, pstick in neighbours(xi, xj, n):
                if (pi, pj) != (yi, yj) and grid[pi][pj] is None:
                    arc = ((pi, pj), (xi, xj), pstick)
                    if arc not in in_queue:
                        work_queue.append(arc)
                        in_queue.add(arc)

    return trail, True


def solve(domains, n, fc=False):
    """Baseline backtracking or forward-checking solver using fixed row-major cell order."""
    grid = np.full((n, n), None, dtype=object)
    cells = [(i, j) for i in range(n) for j in range(n)]

    def search(k):
        if k == len(cells):
            return True

        i, j = cells[k]
        for value in VALUES:
            if value not in domains[(i, j)]:
                continue

            grid[i][j] = value
            if not fc:
                if check(i, j, grid, n) and search(k + 1):
                    return True
            else:
                if check(i, j, grid, n):
                    trail, pas = prune(i, j, value, grid, domains, n)
                    if pas and search(k + 1):
                        return True
                    restore(domains, trail)
            # Reset undecided cells to None (not EMPTY) on backtrack.
            grid[i][j] = None
        return False

    return grid if search(0) else None


def solve_with_stats(
    domains,
    n,
    fc=False,
    heuristic=False,
    ac3_enabled=False,
    timeout_sec=60.0,
):
    """Evaluate CSP search with configurable FC, MRV/partner heuristic, AC-3, and timeout[cite: 1].

    Tracks search duration (after CSP construction), variable assignments,
    backtracking steps, timeout status, and the resulting solution grid[cite: 1].
    """
    grid = np.full((n, n), None, dtype=object)
    cells = [(i, j) for i in range(n) for j in range(n)]
    # Copy domains so each evaluation run starts cleanly without mutating input domains.
    working_domains = {cell: set(dom) for cell, dom in domains.items()}

    stats = {
        "solution": None,
        "timed_out": False,
        "elapsed_sec": 0.0,
        "assignments": 0,
        "backtracks": 0,
    }

    start_time = time.perf_counter()

    def time_exceeded() -> bool:
        """Enforce the 1-minute (60s) search timeout measured after CSP construction[cite: 1]."""
        if time.perf_counter() - start_time >= timeout_sec:
            stats["timed_out"] = True
            return True
        return False

    def _unpaired_neighbour_values(i, j):
        """Domain-specific value helper: prioritize values that complete an adjacent unpaired part."""
        needed = []
        for ni, nj, stick in neighbours(i, j, n):
            nb = grid[ni][nj]
            if nb is None or nb == E:
                continue

            has_partner = False
            for n2i, n2j, stick2 in neighbours(ni, nj, n):
                nb2 = grid[n2i][n2j]
                if nb2 is not None and nb2 != E and allowed(nb, nb2, stick2):
                    has_partner = True
                    break

            if not has_partner:
                for v in VALUES:
                    if v != E and allowed(nb, v, stick) and v not in needed:
                        needed.append(v)
        return needed

    def _urgency_score(i, j):
        """Tie-breaker score: prefer cells adjacent to non-empty cells or sharing rows/cols with them."""
        score = 0
        for ni, nj, _ in neighbours(i, j, n):
            nb = grid[ni][nj]
            if nb is not None and nb != E:
                score += 3
        for col in range(n):
            if col != j and grid[i][col] is not None and grid[i][col] != E:
                score += 1
        for row in range(n):
            if row != i and grid[row][j] is not None and grid[row][j] != E:
                score += 1
        return score

    def next_cell():
        """Select next unassigned cell: fixed row-major order or MRV + urgency heuristic."""
        if not heuristic:
            for cell in cells:
                if grid[cell[0]][cell[1]] is None:
                    return cell
            return None

        best_cell = None
        best_key = None
        for cell in cells:
            i, j = cell
            if grid[i][j] is not None:
                continue
            dom_size = len(working_domains[cell])
            # MRV (smallest domain first), then highest urgency, then row-major tie-break.
            key = (dom_size, -_urgency_score(i, j), i, j)
            if best_key is None or key < best_key:
                best_key = key
                best_cell = cell
        return best_cell

    def ordered_values(cell):
        """Order legal domain values for `cell` (partner-completing values first when heuristic=True)."""
        avail = [v for v in VALUES if v in working_domains[cell]]
        if not heuristic:
            return avail
        i, j = cell
        urgent_partners = [v for v in _unpaired_neighbour_values(i, j) if v in avail]
        rest = [v for v in avail if v not in urgent_partners]
        return urgent_partners + rest

    initial_ok = True
    if ac3_enabled:
        # Establish initial arc consistency before starting tree search[cite: 1].
        _, initial_ok = ac3(working_domains, grid, n)

    def search(assigned_count) -> bool:
        if time_exceeded():
            return False
        if not initial_ok:
            return False
        if assigned_count == len(cells):
            return True

        cell = next_cell()
        if cell is None:
            return True

        i, j = cell
        for value in ordered_values(cell):
            if time_exceeded():
                return False

            grid[i][j] = value
            stats["assignments"] += 1

            ok = check(i, j, grid, n)
            trail = []

            if ok and fc:
                trail, ok = prune(i, j, value, grid, working_domains, n)

            if ok and ac3_enabled:
                if not fc:
                    # Apply immediate neighbour filtering when AC-3 runs without FC.
                    for ni, nj, stick in neighbours(i, j, n):
                        if grid[ni][nj] is None:
                            rem = {
                                v
                                for v in working_domains[(ni, nj)]
                                if not allowed(value, v, stick)
                            }
                            if rem:
                                working_domains[(ni, nj)] -= rem
                                trail.append(((ni, nj), rem))
                                if not working_domains[(ni, nj)]:
                                    ok = False
                                    break
                if ok:
                    ac3_queue = [
                        ((pi, pj), (ni, nj), pstick)
                        for ni, nj, _ in neighbours(i, j, n)
                        if grid[ni][nj] is None
                        for pi, pj, pstick in neighbours(ni, nj, n)
                        if grid[pi][pj] is None
                    ]
                    ac3_trail, ok = ac3(working_domains, grid, n, queue=ac3_queue)
                    trail.extend(ac3_trail)

            if ok and search(assigned_count + 1):
                return True

            if trail:
                restore(working_domains, trail)
            grid[i][j] = None
            stats["backtracks"] += 1

        return False

    found = initial_ok and search(0)
    stats["elapsed_sec"] = time.perf_counter() - start_time
    if found and not stats["timed_out"]:
        stats["solution"] = grid
    return stats