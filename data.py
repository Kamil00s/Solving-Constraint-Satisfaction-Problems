from enum import Enum

class CellType(Enum):
    EMPTY = 0
    HEAD = 1
    STICK_H = 2
    STICK_V = 3


def is_head(cell: CellType) -> bool:
    return cell == CellType.HEAD

    