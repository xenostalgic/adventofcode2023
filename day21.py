from collections import Counter, defaultdict
from dataclasses import dataclass, field
import itertools
import os
from typing import Collection
import numpy as np
import regex as re
import sys

from tqdm import tqdm
from utils import load_file, read_grid, tplus

import IPython as ipy

STEPS = [
    (0,  1),
    (0, -1),
    (1, 0),
    (-1,  0),
]


def to_array(grid: list[str]) -> tuple[np.ndarray, tuple[int, int]]:
    y = len(grid)
    x = len(grid[0])
    arr = np.zeros((y,x))
    start = None
    for i in range(y):
        for j in range(x):
            if grid[i][j] == "#":
                arr[i,j] = 1
            if grid[i][j] == "S":
                start = i,j
    return arr, start


def get_adj(pos: tuple[int, int], grid: np.ndarray):
    h, w = grid.shape
    adj = set()
    for step in STEPS:
        ni, nj = tplus(pos, step)
        npos = (ni % h, nj % w)
        if grid[npos]:
            continue
        adj.add(npos)
    return adj


def get_n_step_set(grid: np.ndarray, start: tuple[int,int], n: int) -> set[tuple[int, int]]:
    # old_frontier = None
    frontier = set([start])
    for step_idx in range(n):
        new_frontier = set()
        for pos in frontier:
            adj = get_adj(pos, grid)
            for p in adj:
                new_frontier.add(p)
        frontier = new_frontier
        print(f"\r{len(frontier)}", end='', flush=True)
    print("")
    return frontier


@dataclass(frozen=True)
class BoardPos:
    pos: tuple[int,int] # index within the board
    bidx: tuple[int, int] # index OF the board

    def plus(self, step: tuple[int,int]):
        npos = tplus(self.pos, step)
        return npos
    
    def get_board_index(idx: int, limit: int):
        return -1 if idx < 0 else 1 if idx >= limit else 0
    
    def adj(self, grid: np.ndarray) -> set:
        h, w = grid.shape
        adj = set()
        for step in STEPS:
            ni, nj = tplus(self.pos, step)
            npos = (ni % h, nj % w)
            if grid[npos]:
                continue                
            bi, bj = BoardPos.get_board_index(ni,h), BoardPos.get_board_index(nj,w)
            if self.pos[1] == w-1 and step[1] == 1 and bj != 1:
                print("hmmm")
                ipy.embed()
            nbidx = tplus(self.bidx, (bi,bj))
            adj.add(BoardPos(npos,nbidx))
        return adj
    

def print_wrapped_grid(grid: np.ndarray, tiles: set[BoardPos]):
    bis = [bp.bidx[0] for bp in tiles]
    bjs = [bp.bidx[1] for bp in tiles]
    min_bi, max_bi = min(bis), max(bis)
    min_bj, max_bj = min(bjs), max(bjs)
    h,w = grid.shape
    s = ""
    for i in range(h*(max_bi+1-min_bi)):
        cbi = i // h + min_bi
        cpi = i % h
        for j in range(w*(max_bj+1-min_bj)):
            cbj = j // w + min_bj
            cpj = j % w
            if grid[cpi,cpj]:
                s += "#"
            else:
                cbp = BoardPos((cpi,cpj), (cbi,cbj))
                if cbp in tiles:
                    s += "O"
                else:
                    s += "."
        s += "\n"
    return s


def get_n_step_set_twrap(grid: np.ndarray, start: BoardPos, n: int, filter=False) -> set[tuple[int, int]]:
    board_completions = {}
    full_boards = set()
    max_board_sizes = []
    max_board_size = None
    frontier = set([start])
    for step_idx in range(0,n):
        # add adjacent points
        new_frontier = set()
        for pos in frontier:
            for p in pos.adj(grid):
                new_frontier.add(p)

        if filter:
            if max_board_size is None:
                max_board_sizes.append(len(set([bp for bp in new_frontier if bp.bidx == start.bidx])))
                if len(set(max_board_sizes[:-5])) == 1:
                    max_board_size = max_board_sizes[-1]
            else:
                bidxs = [bp.bidx for bp in new_frontier]
                bcs = {bidx:len([b for b in bidxs if b==bidx]) for bidx in set(bidxs)}
                for bidx, count in bcs.items():
                    if bidx in full_boards:
                        continue
                    if count > max_board_size:
                        board_completions[bidx] = step_idx
                    if bidx in board_completions and step_idx > 40+board_completions[bidx]:
                        full_boards.add(bidx)
                frontier = [bp for bp in new_frontier if bp.bidx not in full_boards]
        else:
            frontier = new_frontier

    print("")

    return len(frontier)

if __name__=="__main__":
    filename = sys.argv[1]
    if os.path.exists(filename):
        text = open(filename).read()
    else:
        text = load_file(filename, year=2023, day=21)

    grid, start = to_array(read_grid(text))

    print("Part 1:")
    fset = get_n_step_set(grid, start, 64)
    print("Number of reachable tiles:", len(fset))

    print("\nPart 2:")
    start_bpos = BoardPos(start, (0,0))

    if "practice" in filename:
        print("Practice values for infinite grid:")
        for n,t in zip(
            [6,  10, 50,   100,  500,    1000,   5000],
            [16, 50, 1594, 6536, 167004, 668697, 16733044]
        ):
            ntiles = get_n_step_set_twrap(grid, start_bpos, n)
            print(f"Number of reachable tiles: got {ntiles} vs {t} expected", flush=True)
    ipy.embed()

    ntiles = get_n_step_set_twrap(grid, start_bpos, 26501365)
    print(f"Number of reachable tiles: {ntiles}")
