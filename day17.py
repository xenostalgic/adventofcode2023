from collections import Counter, defaultdict
from dataclasses import dataclass, field
import itertools
import os
import numpy as np
import regex as re
import sys

from tqdm import tqdm
from utils import load_file, manhattan_distance, read_grid

import IPython as ipy

TURNS = {"v": "><", "^": "><", ">": "v^", "<": "v^"}
STEPS = {
    (0,  1): ">",
    (0, -1): "<",
    (1, 0): "v",
    (-1,  0): "^",
}
REV_STEPS = {v:k for k,v in STEPS.items()}

def get_heuristics(grid):
    y,x = grid.shape
    fp_heur = np.zeros_like(grid)
    print("Getting heuristics...")
    for i in tqdm(range(y-1,-1,-1)):
        for j in range(x-1,-1,-1):
            n = (y-1-i)+(x-1-j)
            if n == 0:
                fp_heur[i,j] = 0
                continue
            sg = grid[i:,j:]
            costs = sorted(sg.flatten())
            est_cost = sum(costs[:n])
            ai = min(i+1,y-1)
            aj = min(j+1,x-1)
            min_cost = min([
                fp_heur[ai,aj]+min(grid[ai,j], grid[i,aj]),
                fp_heur[i,aj],
                fp_heur[ai,j]
            ])
            fp_heur[i,j] = max(est_cost, min_cost)

    # ipy.embed()
    return fp_heur

@dataclass
class Step:
    pos: tuple[int,int]
    cost: int
    dir: str
    hist: list = field(default_factory=list)
    heuristic: int = -1

    def next(self, grid, hgrid):
        adj = []
        ci,cj = self.pos
        for sdir in TURNS[self.dir]:
            si,sj = REV_STEPS[sdir]
            tc = 0
            for n in range(1,4):
                ai,aj = ci+(si*n), cj+(sj*n)
                if not ((0 <= ai < grid.shape[0]) and (0 <= aj < grid.shape[1])):
                    break
                tc += grid[ai,aj]
                th = self.hist + [(ci+(si*k), cj+(sj*k)) for k in range(1,n)] + [(ai,aj)]
                new_step = Step(
                    pos=(ai,aj),
                    cost=self.cost+tc,
                    dir=sdir,
                    hist=th,
                    heuristic=(self.cost+tc)+hgrid[ai,aj],
                )
                adj.append(new_step)
        return adj

    def gh(self):
        if self.heuristic < 0:
            raise ValueError
        return self.heuristic
    

@dataclass
class UltraStep:
    pos: tuple[int,int]
    cost: int
    dir: str
    hist: list = field(default_factory=list)
    heuristic: int = -1

    def next(self, grid, hgrid):
        adj = []
        ci,cj = self.pos
        for sdir in TURNS[self.dir]:
            si,sj = REV_STEPS[sdir]
            tc = 0
            th = self.hist.copy()
            for n in range(1,11):
                ai,aj = ci+(si*n), cj+(sj*n)
                if not ((0 <= ai < grid.shape[0]) and (0 <= aj < grid.shape[1])):
                    break
                tc += grid[ai,aj]
                th += [(ai,aj)]
                if n < 4:
                    continue
                new_step = UltraStep(
                    pos=(ai,aj),
                    cost=self.cost+tc,
                    dir=sdir,
                    hist=th.copy(),
                    heuristic=(self.cost+tc)+hgrid[ai,aj],
                )
                adj.append(new_step)
        return adj

    def gh(self):
        if self.heuristic < 0:
            raise ValueError
        return self.heuristic


def to_array(list_grid):
    y = len(list_grid)
    x = len(list_grid[0])
    grid = np.zeros((y,x))
    for i in range(y):
        for j in range(x):
            grid[i,j] = int(list_grid[i][j])
    return grid


def print_grid(path, grid):
    y, x = len(grid), len(grid[0])
    pos_dir = {step[0]:step[1] for step in path}
    s = ""
    for i in range(y):
        for j in range(x):
            if (i,j) in pos_dir:
                s += pos_dir[(i,j)]
            else:
                s +=str(int(grid[i,j]))
        s += "\n"
    return s


def a_star(grid, ultra=False):

    hgrid = get_heuristics(grid)

    queue = []
    for d in "^v<>":
        if ultra:
            s = UltraStep( pos=(0,0), cost=0, dir=d, hist=[(0,0)], heuristic=hgrid[0,0])
        else:
            s = Step( pos=(0,0), cost=0, dir=d, hist=[(0,0)], heuristic=hgrid[0,0])
        queue.append(s)

    best_paths = {(s.pos, s.dir):s for s in queue}
    expanded = defaultdict(list)
    full_paths = []

    dest = grid.shape[0]-1, grid.shape[1]-1

    max_cost = grid.sum()

    itr = 0
    while len(queue) > 0:
        print(f"\r{itr}", end="")
        itr += 1
        cur = queue.pop()

        min_heuristic = min([s.gh() for s in queue] + [max_cost])

        # check for completion
        if cur.pos == dest:
            full_paths.append(cur)
            if cur.cost < min_heuristic:
                break
            continue

        # expand
        expanded[cur.pos].append(cur)
        next_steps = cur.next(grid, hgrid)
        for nstep in next_steps:
            pd_idx = (nstep.pos, nstep.dir)
            if pd_idx not in best_paths:
                # add node as best path
                best_paths[pd_idx] = nstep
                queue.append(nstep)
            elif best_paths[pd_idx].gh() > nstep.gh():
                # replace current best path to node
                best_paths[pd_idx] = nstep
                queue.append(nstep)
            else:
                continue

        if len(queue) == 0:
            break
        queue = sorted(queue, key=lambda x: x.gh(), reverse=True)


    res = min(full_paths, key=lambda s: s.cost)
    print("\n" + print_grid([(p,".") for p in res.hist], grid))
    return res


if __name__=="__main__":
    filename = sys.argv[1]
    if os.path.exists(filename):
        text = open(filename).read()
    else:
        text = load_file(filename, year=2023, day=17)

    grid = to_array(read_grid(text))

    print("Part 1:")
    res = a_star(grid)
    print("\nMin heat loss:", res.cost)

    print("\nPart 2:")
    res = a_star(grid, ultra=True)
    print("\nMin heat loss with ultra crucibles:", res.cost)
    ipy.embed()