# solver.py
import numpy as np

from constrains import check
from data import CellType

VALUES = (CellType.EMPTY, CellType.HEAD, CellType.STICK_H, CellType.STICK_V)



def solve(domains, n):
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
            if check(i, j, grid, n) and search(k + 1):
                return True
            grid[i][j] = None            

        return False                     

    return grid if search(0) else None