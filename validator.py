from data import CellType
import numpy as np

#graph is gonna be a numpy array

def check_line_vis(line) -> bool:
    seq = [cell for cell in line if cell != CellType.EMPTY]
    print(f"    non-empty sequence = {seq}")
    for a, b in zip(seq, seq[1:]):
        if a == b:
            print(f"    FAIL: two cells of type {a} see each other in {line}")
            return False
    print("    OK")
    return True
        

def check_lolipop(graph) -> bool:
    
    n = len(graph)
    print(f"[lollipop] checking {n}x{n} grid")
    for i in range(n):  
        for j in range(n):
            counter = 0
            if graph[i][j] == CellType.HEAD:
                print(f"  ({i},{j}) HEAD")
                # check grid for horizontal lines in row and addto counter  if head  return false 
                # check grid for vertical lines in column and add counter  if head  return false 
                if i -1 >= 0 and graph[i-1][j] == CellType.STICK_V:
                    counter += 1
                    print(f"    partner STICK_V above ({i-1},{j}) -> counter={counter}")
                if i +1 < n  and graph[i+1][j] == CellType.STICK_V:
                    counter += 1
                    print(f"    partner STICK_V below ({i+1},{j}) -> counter={counter}")
                if j -1 >= 0 and graph[i][j-1] == CellType.STICK_H:
                    counter += 1
                    print(f"    partner STICK_H left ({i},{j-1}) -> counter={counter}")
                if j +1 < n  and graph[i][j+1] == CellType.STICK_H:
                    counter += 1
                    print(f"    partner STICK_H right ({i},{j+1}) -> counter={counter}")
                #check for head:
                if i -1 >= 0 and (graph[i-1][j] == CellType.HEAD or graph[i-1][j] == CellType.STICK_H):
                    print(f"    FAIL: HEAD ({i},{j}) touches {graph[i-1][j]} above ({i-1},{j})")
                    return False
                if i +1 < n  and (graph[i+1][j] == CellType.HEAD or graph[i+1][j] == CellType.STICK_H):
                    print(f"    FAIL: HEAD ({i},{j}) touches {graph[i+1][j]} below ({i+1},{j})")
                    return False
                if j -1 >= 0 and (graph[i][j-1] == CellType.HEAD or graph[i][j-1] == CellType.STICK_V):
                    print(f"    FAIL: HEAD ({i},{j}) touches {graph[i][j-1]} left ({i},{j-1})")
                    return False
                if j +1 < n  and (graph[i][j+1] == CellType.HEAD or graph[i][j+1] == CellType.STICK_V):
                    print(f"    FAIL: HEAD ({i},{j}) touches {graph[i][j+1]} right ({i},{j+1})")
                    return False
                

            elif graph[i][j] == CellType.STICK_H:
                print(f"  ({i},{j}) STICK_H")

                if j -1 >= 0 and graph[i][j-1] == CellType.HEAD:
                    counter += 1
                    print(f"    partner HEAD left ({i},{j-1}) -> counter={counter}")
                if j +1 < n  and graph[i][j+1] == CellType.HEAD:
                    counter += 1
                    print(f"    partner HEAD right ({i},{j+1}) -> counter={counter}")
                #check for stick:
                if i -1 >= 0 and (graph[i-1][j] == CellType.STICK_H or graph[i-1][j] == CellType.STICK_V):
                    print(f"    FAIL: STICK_H ({i},{j}) touches {graph[i-1][j]} above ({i-1},{j})")
                    return False
                if i +1 < n  and (graph[i+1][j] == CellType.STICK_H or graph[i+1][j] == CellType.STICK_V):
                    print(f"    FAIL: STICK_H ({i},{j}) touches {graph[i+1][j]} below ({i+1},{j})")
                    return False
                if j -1 >= 0 and (graph[i][j-1] == CellType.STICK_H or graph[i][j-1] == CellType.STICK_V):
                    print(f"    FAIL: STICK_H ({i},{j}) touches {graph[i][j-1]} left ({i},{j-1})")
                    return False
                if j +1 < n  and (graph[i][j+1] == CellType.STICK_H or graph[i][j+1] == CellType.STICK_V):
                    print(f"    FAIL: STICK_H ({i},{j}) touches {graph[i][j+1]} right ({i},{j+1})")
                    return False
            
            elif graph[i][j] == CellType.STICK_V:
                print(f"  ({i},{j}) STICK_V")
                if i -1 >= 0 and graph[i-1][j] == CellType.HEAD:
                    counter += 1
                    print(f"    partner HEAD above ({i-1},{j}) -> counter={counter}")
                if i +1 < n  and graph[i+1][j] == CellType.HEAD:
                    counter += 1
                    print(f"    partner HEAD below ({i+1},{j}) -> counter={counter}")
                #check for stick:
                if i -1 >= 0 and (graph[i-1][j] == CellType.STICK_H or graph[i-1][j] == CellType.STICK_V):
                    print(f"    FAIL: STICK_V ({i},{j}) touches {graph[i-1][j]} above ({i-1},{j})")
                    return False
                if i +1 < n  and (graph[i+1][j] == CellType.STICK_H or graph[i+1][j] == CellType.STICK_V):
                    print(f"    FAIL: STICK_V ({i},{j}) touches {graph[i+1][j]} below ({i+1},{j})")
                    return False
                if j -1 >= 0 and (graph[i][j-1] == CellType.STICK_H or graph[i][j-1] == CellType.STICK_V):
                    print(f"    FAIL: STICK_V ({i},{j}) touches {graph[i][j-1]} left ({i},{j-1})")
                    return False
                if j +1 < n  and (graph[i][j+1] == CellType.STICK_H or graph[i][j+1] == CellType.STICK_V):
                    print(f"    FAIL: STICK_V ({i},{j}) touches {graph[i][j+1]} right ({i},{j+1})")
                    return False
            else:
                continue
            if counter != 1:
                    print(f"    FAIL: ({i},{j}) {graph[i][j]} has {counter} partners, expected exactly 1")
                    return False
    print("[lollipop] OK: all heads and sticks form valid, non-touching lollipops")
    return True



def validate(graph: np.ndarray[CellType]) -> bool:
    h,w = graph.shape
    print(f"=== validate: grid {h}x{w} ===")

    assert h == w

    #check if only valid lolipops present
    # for every part that is not empty check if it has correct thing
    
        
    if check_lolipop(graph) == False:
        print("=== INVALID: rule 1/2 (lollipop structure or touching) ===")
        return False

    #check if lolipops are next to each other
    # check i all spaces around lolipop are empty


    
    #check columns and rows for the same characters
    print("[visibility] checking rows and columns")
    for c in range(h):
        row = graph[c]
        column = graph[:,c]
        print(f"  row {c} = {row}")
        print(f"  col {c} = {column}")
        if check_line_vis(row) == False or check_line_vis(column) == False:
            print(f"=== INVALID: rule 3 in row {c} or col {c} (see FAIL above) ===")
            return False
        
    print("This graph is VALID")
    return True