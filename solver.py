import numpy as np

from constraints import check
from data import CellType
from forward_solver import prune, restore

VALUES = (CellType.EMPTY, CellType.HEAD, CellType.STICK_H, CellType.STICK_V)

def solve(domains, n, fc=False):
    #pure backtracking
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
            if fc == False:
                if check(i, j, grid, n) and search(k + 1):
                    return True
            else:
                if check(i, j, grid, n):
                    trail, pas = prune(i,j,value, grid, domains,n)
                    if pas and search(k+1):
                        return True
                    restore(domains,trail)
            grid[i][j] = None            
        return False                     

    return grid if search(0) else None