from collections import defaultdict
import itertools
import re
import sys
import time
import numpy as np

import IPython as ipy

BFS_STEPS = [
    (-1,-1), (-1,0),(-1,1),
    (0,-1),          (0,1),
    (1,-1),  (1,0),  (1,1),
]

BFS_SQUEEZE_STEPS = {
    (1,0): ["||", "J|", "JL", "|L", "|F", "7|", "7F"],
    (-1,0): ["--", "-F", "-7", "LF", "L-", "J-", "J7"],
    (0,1): ["||", "J|", "JL", "|L", "|F", "7|", "7F"],
    (0,-1): ["--", "-F", "-7", "LF", "L-", "J-", "J7"],
}

STEPS = {
    (0,  1): "-7J",
    (0, -1): "-FL",
    (1, 0): "|LJ",
    (-1,  0): "|F7",
}

REV_STEPS = defaultdict(list)
for ch in "-7JFL|":
    for step,st in STEPS.items():
        if ch in st:
            REV_STEPS[ch].append((-step[0], -step[1]))
REV_STEPS["S"] = [step for step in STEPS]


def print_map(loop, chars):
    y = max(p[0]+2 for p in loop)
    x = max(p[1]+2 for p in loop)
    s = ""
    for i in range(y):
        for j in range(x):
            if (i,j) in loop:
                s += chars[(i,j)]
            else:
                s += "."
        s+="\n"
    print(s)


def find_loop(lines):
    loop = set()
    dists = {}
    chars = {}
    for i,line in enumerate(lines):
        if "S" in line:
            start = (i,line.find("S"))
            loop.add(start)
            dists[start] = 0
            chars[start] = "S"
            break

    # print("".join(lines))

    i = 0
    cur_loop = loop.copy()
    while True:
        dl = len(dists)
        new_loop = set()
        for (ci, cj) in cur_loop:
            ch = chars[(ci,cj)]
            for (si,sj) in REV_STEPS[ch]:
                ti,tj = ci+si,cj+sj
                if lines[ti][tj] in STEPS[(si,sj)]:
                    # pipe connects
                    new_loop.add((ti,tj))
                    dists[(ti,tj)] = min(dists.get((ti,tj),100000), dists[(ci,cj)]+1)
                    chars[(ti,tj)] = lines[ti][tj]
        if len(dists) == dl:
            break
        cur_loop = new_loop.difference(loop)
        loop = loop.union(new_loop)
        i += 1
    #     print(f"\r{i}", end='')

    # print("")

    adj = []
    sch = None
    for step in STEPS:
        si,sj = step
        ti,tj = (start[0]+si,start[1]+sj)
        if (ti,tj) in loop and chars[(ti,tj)] in STEPS[step]:
            adj.append(step)
    for ch in REV_STEPS:
        if ch == "S":
            continue
        if all(a in REV_STEPS[ch] for a in adj):
            sch = ch
    chars[start] = sch

    loop = set(loop)
    # print_map(loop, chars)

    return loop, dists, chars, max(dists.values())

""" 
Alternate approach: redraw map "zoomed in", replacing each tile with a 9x9 region.
      ...        .|.
- --> ---  | --> .|.
      ...        .|.

      .|.        ...
L --> .L-  7 --> -7.
      ...        .|.

then do BFS without squeezes needed. then recount map by "zooming out" again:
for each normal empty tile, check if all 9 targets are in the BFS coverage
"""

ZTILE = [".|.","-.-",".|."]

def zoom_map(loop, chars):
    my = max([p1 for p1,p2 in loop]) + 1
    mx = max([p2 for p1,p2 in loop]) + 1
    zloop = set()
    zchars = {}
    for i in range(my):
        for j in range(mx):
            if (i,j) in loop:
                ch = chars[i,j]
                zi, zj = i*3 + 1, j*3 + 1
                zloop.add((zi,zj))
                zchars[(zi,zj)] = ch
                for ei,ej in REV_STEPS[ch]:
                    ti,tj = (i+ei,j+ej)
                    if (ti,tj) not in loop:
                        continue
                    tzch = ZTILE[ei+1][ej+1]
                    tzi,tzj = zi+ei, zj+ej
                    zloop.add((tzi,tzj))
                    zchars[(tzi,tzj)] = tzch

    return zloop, zchars


def find_enclosed(loop):
    # BFS from (0,0), including "squeezing through pipes"
    # when no new area covered, return covered set
    my = max([p1 for p1,p2 in loop]) + 6
    mx = max([p2 for p1,p2 in loop]) + 6
    cov = set([(0,0),(my-1,mx-1)])
    pbeam = cov.copy()
    cbeam = cov.copy()
    i = 0
    while True:
        nbeam = set()
        for pi,pj in cbeam:
            for si,sj in BFS_STEPS:
                ti,tj = pi+si,pj+sj
                if ti < 0 or tj < 0 or ti >= my or tj >= mx:
                    continue
                if (ti,tj) not in loop and (ti,tj) not in pbeam:
                    nbeam.add((ti,tj))
        pbeam = cbeam
        cbeam = nbeam
        if len(nbeam.difference(cov)) == 0:
            break
        cov = cov.union(nbeam)
        # print(f"\r{i}", end='')
        i += 1

    return cov


def find_enclosed_zoom(loop, chars):
    zloop, zchars = zoom_map(loop, chars)
    zcov = find_enclosed(zloop)
    my = int(max([p1 for p1,p2 in zcov]) / 3)
    mx = int(max([p2 for p1,p2 in zcov]) / 3)
    cov = set()
    for i in range(my):
        for j in range(mx):
            # check if "full" tile is covered
            tile = 0
            for si in [0,1,2]:
                for sj in [0,1,2]:
                    if (i*3+si,j*3+sj) in zcov:
                        tile += 1
            if tile == 9:
                cov.add((i,j))

    combo_chars = {}
    for p in cov:
        combo_chars[p] = "O"
    for p in loop:
        combo_chars[p] = chars[p]
    # print_map(loop.union(cov), combo_chars)

    enc = (my*mx) - len(cov) - len(loop)

    return enc


def find_enclosed_wind(loop, chars):
    my = max([p1 for p1,p2 in loop])+2
    mx = max([p2 for p1,p2 in loop])+2
    enc = set()
    for i,j in itertools.product(range(my),range(mx)):
        if (i,j) in loop:
            continue
        ystr = [chars[(ci,j)] for ci in range(0,i) if (ci,j) in loop and chars[(ci,j)] in "FL-"]
        if len(ystr) % 2 == 0:
            # outside
            pass
        else:
            enc.add((i,j))
    return len(enc)

    
if __name__=="__main__":
    input = open(sys.argv[1]).readlines()
    print("Part 1:")
    loop, dists, chars, max_dist = find_loop(input)
    print("Max dist:", max_dist)
    print("Part 2:")
    s1 = time.monotonic()
    enc = find_enclosed_zoom(loop, chars)
    s2 = time.monotonic()
    print(f"Enclosed (zoomed BFS ran in {s2-s1}):", enc)
    s1 = time.monotonic()
    enc2 = find_enclosed_wind(loop, chars)
    s2 = time.monotonic()
    print(f"Enclosed (parity checking ran in {s2-s1}):", enc2)
