from pathlib import Path
import numpy as np
from data import CellType

CHARS = {'.': CellType.EMPTY, 'O': CellType.HEAD,
         '-': CellType.STICK_H, '|': CellType.STICK_V}
INV = {cell: char for char, cell in CHARS.items()}
FULL = {CellType.EMPTY, CellType.HEAD, CellType.STICK_H, CellType.STICK_V}


def load_grid(path):
    rows = Path(path).read_text().split()
    return np.array([[CHARS[ch] for ch in row] for row in rows], dtype=object)


def load_domains(path):
    grid = load_grid(path)
    return {(i, j): {cell} if cell != CellType.EMPTY else FULL.copy()
            for i, row in enumerate(grid) for j, cell in enumerate(row)}


def to_string(grid):
    return "\n".join("".join(INV[cell] for cell in row) for row in grid)


