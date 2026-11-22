from constraints import allowed, check, neighbours


def prune(i, j, value, grid, domains, n):
    
    trail = []
    for i1, j1, stick in neighbours(i, j, n):

        if grid[i1][j1] is not None:
            continue                                   

        domain = domains[(i1, j1)]
        removed = {v for v in domain if not allowed(value, v, stick)}

        domain -= removed

        trail.append(((i1, j1), removed))

        if not domain:
            return trail, False                        

    return trail, True


def restore(domains, trail):
    
    for cell, rem in trail:
        domains[cell].update(rem)