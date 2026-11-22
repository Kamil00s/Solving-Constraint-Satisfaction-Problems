import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from parser import load_grid, load_domains, to_string
from solver import solve
from data import CellType
from validator import validate

path = ROOT / "instances" / "01_6x6_normal.txt"

grid = load_grid(path)
print("The text file:")
print(to_string(grid))
print("Numpy array:")
print("shape:", grid.shape)

print(grid)

print("Domains:")
for cell, domain in load_domains(path).items():
    print(cell, domain)

solved = solve(load_domains(path), 6)

if solved is not None:
    print(solved)
else: 
    print("No solution")

print("Starting validation")
validate(solved)

print(to_string(solved))

print("Strating run with forward checking")

res = solve(load_domains(path),6,fc=True)

if res is not None:
    print(solved)
else: 
    print("No solution")

print("Starting validation")
validate(res)

print(to_string(res))
