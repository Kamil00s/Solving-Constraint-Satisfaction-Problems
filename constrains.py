from data import CellType

E  = CellType.EMPTY
H  = CellType.HEAD
SH = CellType.STICK_H
SV = CellType.STICK_V

# (zmiana wiersza, zmiana kolumny, patyk należący do tej osi)
DIRS = (
    (-1,  0, SV),   # w górę   - lizak stoi pionowo
    ( 1,  0, SV),   # w dół
    ( 0, -1, SH),   # w lewo   - lizak leży poziomo
    ( 0,  1, SH),   # w prawo
)

def neighbours(i,j,n):
    for i1,j1, stick in DIRS:
        res1, res2 = i + i1 , j + j1
        if n> res1 >= 0 and  n > res2 >= 0:
            #yield is more efficient than allocation memory
            yield res1, res2, stick


def allowed(a,b,stick) -> bool:
    if a == E or b == E:
        return True
    if a == H and b == stick:
        return True
    if b == H and a == stick:
        return True
    return False



def line_ok(line) -> bool:
    #check if the line is safe 
    seq = [cell for cell in line if cell != CellType.EMPTY]   
    for a, b in zip(seq, seq[1:]):
        if a is not None and a == b:
            return False
    return True
    
    

def cell_ok(i, j, grid, n) -> bool:
    value = grid[i][j]
    if value is None:
        return True

    filled = 0
    unknown = 0
    for i1, j1, stick in neighbours(i, j, n):
        neighbour = grid[i1][j1]
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
    if not cell_ok(i, j, grid, n):
        return False
    for i1, j1, _ in neighbours(i, j, n):
        if not cell_ok(i1, j1, grid, n):
            return False
    return line_ok(grid[i]) and line_ok(grid[:, j])


