import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from parser import load_grid, load_domains, to_string

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
