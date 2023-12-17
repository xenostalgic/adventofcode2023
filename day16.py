from collections import Counter, defaultdict
from dataclasses import dataclass
import itertools
import numpy as np
import regex as re
import sys

from tqdm import tqdm
from utils import load_file, read_grid

import IPython as ipy

R1_DIRS = {"R": "D", "L": "U", "U": "L", "D": "R"} # for \
R2_DIRS = {"R": "U", "L": "D", "U": "R", "D": "L"} # for /
DIRPS = {"R": ">", "L": "<", "U": "^", "D": "v"}

ENTR_DIR_POS = {"D": (-1,0), "U": (1,0), "R": (0,-1), "L": (0,1)}
EXIT_DIR_POS = {"D": (1,0), "U": (-1,0), "R": (0,1), "L": (0,-1)}

@dataclass(frozen=True)
class Beam:
    pos: tuple[int, int]
    dir: str


def print_grid(energized, grid, energized_only=False):
    y, x = len(grid), len(grid[0])
    en_pos = defaultdict(str)
    for beam in energized:
        en_pos[beam.pos] += DIRPS[beam.dir]
    s = ""
    for i in range(y):
        for j in range(x):
            if energized_only:
                if (i,j) in en_pos:
                    s += "#"
                else:
                    s += "."
            else:
                if grid[i][j] == "." and (i,j) in en_pos:
                    val = en_pos[(i,j)]
                    s += str(len(val)) if len(val) > 1 else val
                else:
                    s += grid[i][j]
        s += "\n"
    return s


def next(beam: Beam, grid: list[list[str]]) -> tuple[list[Beam], list[Beam]]:
    """Take the start of a beam and project it forward until it hits a wall,
    mirror, or splitter. Return a list of beams to continue from and a list of
    covered tiles to mark as energized.

    Args:
        beam (Beam): A beam to start from
        grid (list[list[str]]): The map

    Returns:
        tuple[list[Beam], list[Beam]]: A list of beam starts and a list of energized tiles.
    """
    y, x = len(grid), len(grid[0])
    ci, cj = beam.pos
    energized = []
    if beam.dir == "R":
        ray = list(range(cj+1,x))
    elif beam.dir == "L":
        ray = list(range(cj-1,-1,-1))
    elif beam.dir == "U":
        ray = list(range(ci-1,-1,-1))
    elif beam.dir == "D":
        ray = list(range(ci+1,y))
    else:
        raise ValueError(f"Unrecognized dir: {dir}. Must be one of RLUD")
    
    end_pos, end_val = None, None
    if beam.dir in "RL":
        for j in ray:
            energized.append(Beam((ci,j),beam.dir))
            if grid[ci][j] not in ".-":
                end_pos = (ci,j)
                end_val = grid[ci][j]
                break
    elif beam.dir in "UD":
        for i in ray:
            energized.append(Beam((i,cj),beam.dir))
            if grid[i][cj] not in ".|":
                end_pos = (i,cj)
                end_val = grid[i][cj]
                break
    
    # get new beam starts
    if end_val is None:
        # hit a wall, beam dies
        return [], energized
    elif end_val == "|" and beam.dir in "RL":
        # split left/right into up/down
        return [Beam(end_pos,"U"), Beam(end_pos,"D")], energized
    elif end_val == "-" and beam.dir in "UD":
        # split up/down into left/right
        return [Beam(end_pos,"R"), Beam(end_pos,"L")], energized
    elif end_val == "\\":
        # reflect 1
        new_dir = R1_DIRS[beam.dir]
        return [Beam(end_pos,new_dir)], energized
    elif end_val == "/":
        # reflect 2
        new_dir = R2_DIRS[beam.dir]
        return [Beam(end_pos,new_dir)], energized
    else:
        raise ValueError("Incompatible direction and val:", end_pos, end_val, beam.dir)
        
def pivot_init(beam: Beam, grid):
    bi,bj = beam.pos
    gv = grid[bi][bj]
    if gv == ".":
        return [beam]
    elif gv == "\\":
        new_dir = R1_DIRS[beam.dir]
        return [Beam(beam.pos, new_dir)]
    elif gv == "/":
        new_dir = R2_DIRS[beam.dir]
        return [Beam(beam.pos, new_dir)]
    elif gv == "|" and beam.dir in "RL":
        return [Beam(beam.pos, "U"), Beam(beam.pos, "D")]
    elif gv == "-" and beam.dir in "DU":
        return [Beam(beam.pos, "R"), Beam(beam.pos, "L")]
    else:
        return [beam]


def sim_beam(grid, init_beam: Beam = Beam((0,0),"R"), loop_cutoff: int = 0):

    checked_beams: Counter[Beam] = Counter()
    beams: list[Beam] = pivot_init(init_beam, grid)
    energized: Counter[Beam] = Counter()
    rays = defaultdict(list)
    step = 0

    while len(beams) > 0:
        cur_beam = beams.pop()
        if cur_beam in checked_beams and checked_beams[cur_beam] > loop_cutoff:
            # in a loop; cut it short
            continue

        next_beams, ray_en = next(cur_beam, grid)

        beams.extend(next_beams)
        rays[cur_beam].append(ray_en)

        for b in ray_en:
            energized[b] += 1
        energized[cur_beam] += 1
        checked_beams[cur_beam] += 1
        step += len(energized)-1

    return energized
        

if __name__=="__main__":
    if len(sys.argv) == 1 or "practice" in sys.argv[1]:
        text = open("inputs/day16_practice.txt").read()
    else:
        filename = sys.argv[1]
        text = load_file(filename, year=2023, day=16)

    grid = read_grid(text)

    print("Part 1:")
    energized = sim_beam(grid)
    tiles = set([b.pos for b in energized])
    print(print_grid(energized, grid, energized_only=True))
    print("Total energized tiles:", len(tiles))

    print("\nPart 2:")
    en_counts = {}
    y,x = len(grid), len(grid[0])
    for i in tqdm(range(y)):
        energr = sim_beam(grid, Beam((i,0),"R"))
        en_counts[(i,0)] = len(set([b.pos for b in energr]))
        energl = sim_beam(grid, Beam((i,x-1),"L"))
        en_counts[(i,x-1)] = len(set([b.pos for b in energr]))
    for j in tqdm(range(x)):
        energd = sim_beam(grid, Beam((0,j),"D"))
        en_counts[(0,j)] = len(set([b.pos for b in energd]))
        energu = sim_beam(grid, Beam((y-1,j),"U"))
        en_counts[(y-1,j)] = len(set([b.pos for b in energd]))
    print("Max energized:", max(en_counts.values()))
