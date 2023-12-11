from math import prod
import re
import sys
import os
import numpy as np
from utils import load_file, manhattan_distance, read_grid

def print_arr(grid):
    s = ""
    idx = 1
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            s += "#" if grid[i,j] else "."
        s += "\n"
    print(s)


def to_array(grid):
    y = len(grid)
    x = len(grid[0])
    arr = np.zeros((y,x))
    for i in range(y):
        for j in range(x):
            if grid[i][j] == "#":
                arr[i,j] = 1
    return arr


def between(p1, p2, q):
    if p1 < q < p2:
        return True
    if p2 < q < p1:
        return True
    if p2 == q == p1:
        return True
    return False


def get_gals(grid):
    gals = []
    for i in range(grid.shape[0]):
        for j in range(grid.shape[0]):
            if grid[i,j] == 1:
                gals.append((i,j))
    return gals


def expand_and_get_paths(grid, gals, ratio=2):
    expand_is = []
    expand_js = []
    for i in range(grid.shape[0]):
        if grid[i,:].sum() == 0:
            expand_is.append(i)
    for j in range(grid.shape[0]):
        if grid[:,j].sum() == 0:
            expand_js.append(j)
    gps = set()
    dists = []
    for g1 in gals:
        for g2 in gals:
            if g1 == g2 or (g2,g1) in gps:
                continue
            d = manhattan_distance(g1,g2)
            eid = len([ei for ei in expand_is if between(g1[0], g2[0], ei)])
            ejd = len([ej for ej in expand_js if between(g1[1], g2[1], ej)])
            d += (ratio-1)*eid 
            d += (ratio-1)*ejd
            dists.append(d)
            gps.add((g1,g2))
    return dists

if __name__=="__main__":
    filename = sys.argv[1]
    if "practice" not in filename:
        text = load_file(filename, year=2023, day=11)
    else:
        text = open(filename).read()

    print("\nPart 1:")
    grid = read_grid(text)
    arr = to_array(grid)
    print_arr(arr)
    gals = get_gals(arr)
    dists = expand_and_get_paths(arr,gals,ratio=2)
    res = sum(dists)
    print(res)

    print("\nPart 2:")
    gals = get_gals(arr)
    dists = expand_and_get_paths(arr,gals,ratio=1000000)
    res2 = sum(dists)
    print(res2)
