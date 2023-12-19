from collections import Counter, defaultdict
from dataclasses import dataclass, field
import itertools
import os
from typing import Collection
import numpy as np
import regex as re
import sys

from tqdm import tqdm
from utils import load_file, toverlap, toverlap_size, tplus

import IPython as ipy

STEPS = {
    "R": (0,  1),
    "L": (0, -1),
    "D": (1, 0),
    "U": (-1,  0),
}
STEP_ORD = "RDLU"


def print_grid(dug: Collection, dug2: Collection = None, edge: int = 0):
    if dug2 is None: dug2 = set()
    y = max([y for y,_ in dug])
    x = max([x for _,x in dug])
    s = ""
    for i in range(y+1 + edge):
        for j in range(x+1 + edge):
            s += "#" if (i,j) in dug else "@" if (i,j) in dug2 else "."
        s += "\n"
    return s


def parse_instructions(text: str):
    entries, colors = [], []
    for line in text.splitlines():
        d, n, color = line.strip().split()
        n = int(n)
        color = color.strip("()")
        entries.append((d,n))
        colors.append(color)
    return entries, colors


def parse_colors(colors: list[str]):
    entries = []
    for hex in colors:
        n = int(hex[1:-1], 16)
        d = STEP_ORD[int(hex[-1])]
        entries.append((d,n))
    return entries


def rezero(dug: Collection):
    ys = [y for y,_ in dug]
    xs = [x for _,x in dug]
    miny = min(ys)
    minx = min(xs)
    return [(p[0]-miny,p[1]-minx) for p in dug]


def dig_outline(entries):
    cur = (0,0)
    outline = [cur]
    for (d,n) in tqdm(entries, desc="Digging outline"):
        step = STEPS[d]
        for i in range(n):
            cur = tplus(step,cur)
            outline.append(cur)
    return rezero(outline)


def get_fill(outline: list[tuple[int,int]]):
    outline = set(outline)
    y = max([y for y,_ in outline])+1
    x = max([x for _,x in outline])+1
    fill = set()
    for i in tqdm(range(y), desc="Filling outline"):
        for j in range(x):
            if (i,j) in outline:
                continue
            g = 0
            ray = range(i) if i > y/2 else range(i+1,y) # pick min dist to edge
            for s in ray:
                if (s,j) in outline and (s,j+1) in outline:
                    g += 1

            if g % 2 == 0:
                continue
            fill.add((i,j))

    total = outline.union(fill)
    with open("day18_output.txt", 'w') as outf:
        print(print_grid(outline), file=outf, flush=True)
        print(print_grid(total), file=outf, flush=True)

    return total


def dig_big_outline(entries):
    curp = (0,0)
    corners_by_x = defaultdict(list)
    vedges_by_x = defaultdict(list)
    hedges, vedges = [], []
    hprint = []
    for eidx, (d,n) in tqdm(enumerate(entries), desc="Digging outline"):
        step = STEPS[d]
        if d in "RL":
            esum = 0
            jedge = range(curp[1], curp[1]+(step[1]*(n+1)), step[1])
            for idx,j in enumerate(jedge):
                if (d == "R" and idx < n) or (d == "L" and idx > 0):
                    # add only if edge continues to the right
                    corners_by_x[j].append(curp[0])
                esum += 1
            hedges.append(n)
            hprint.extend([(curp[0],j) for j in jedge])
        else:
            # store edges not covered by horizontal edges
            prevd = entries[(eidx-1)%len(entries)][0]
            nextd = entries[(eidx+1)%len(entries)][0]
            i1, i2 = (curp[0], curp[0]+(step[0]*n))
            vedges_by_x[curp[1]].append((min(i1,i2), max(i1,i2)))
            vedges.append(n+1)
        curp = tplus(curp, (step[0]*n, step[1]*n))

    return corners_by_x, vedges_by_x, hprint


def get_big_fill(outline_by_x: dict, vedges_by_x: dict, reference: set = None):
    fill_size = 0
    rems_size = 0
    fill = set()
    remf = set()
    for j in outline_by_x:
        spans = sorted(outline_by_x[j])
        for p in range(0, len(spans), 2):
            i1, i2 = spans[p], spans[p+1]
            overlaps = [sp for sp in vedges_by_x[j] if toverlap(tplus(sp,(0,1)),(i1,i2))]
            overlap_sizes = [toverlap_size(sp, (i1,i2)) for sp in overlaps]
            add_size = (i2 - i1)+1
            rem_size = sum([o+1 for o in overlap_sizes])
            if (add_size - rem_size) < 0:
                print("Removing more than all of a column??")
                ipy.embed()
            if rem_size < 0:
                print("Removing negative amount")
                ipy.embed()
            if add_size < 0:
                print("Adding negative amount")
                ipy.embed()

            if p>0 and (spans[p-1], spans[p]) in vedges_by_x[j]:
                rem_size += 1

            fill_size += add_size - rem_size
            rems_size += rem_size

            # set-based solution, remove for full input
            tf, rf = set(), set()
            for i in range(i1, i2+1):
                tf.add((i,j))
                fill.add((i,j))
            for sp in overlaps:
                for i in range(sp[0], sp[1]+1):
                    if (i,j) in tf:
                        rf.add((i,j))
                        fill.remove((i,j))
                        remf.add((i,j))
                    elif (i,j) in fill:
                        print("Removing point not in added")
                        rf.add((i,j))
                        fill.remove((i,j))
                        remf.add((i,j))
            if len(tf) != add_size or len(rf) != rem_size:
                print("Removal mismatch")
                ipy.embed()
            

    if len(fill) != fill_size or len(remf) != rems_size:
        print("Set/index mismatch")
        ipy.embed()

    vtot = 0
    vset = set()
    for j in vedges_by_x:
        jsum = sum(p[1]+1-p[0] for p in vedges_by_x[j])
        vtot += jsum
        for sp in vedges_by_x[j]:
            for i in range(sp[0], sp[1]):
                vset.add((i,j))

    if reference is not None:
        ref_outline, ref_fill = reference
        if len(ref_fill) != len(fill.union(vset)):
            print("Off-by-one compared to reference")
            ipy.embed()

    return fill_size, rems_size, vtot


def print_big_fill(outline_by_x: dict, vedges_by_x: dict):
    fill = set()
    remf = set()
    for j in outline_by_x:
        spans = sorted(outline_by_x[j])
        for p in range(0, len(spans), 2):
            i1, i2 = spans[p], spans[p+1]
            overlaps = [sp for sp in vedges_by_x[j] if toverlap(tplus(sp,(0,1)), (i1,i2))]
            for i in range(i1, i2+1):
                fill.add((i,j))
            for sp in overlaps:
                for i in range(sp[0], sp[1]+1):
                    if (i,j) in fill:
                        fill.remove((i,j))
                        remf.add((i,j))
    fill2 = set()
    for j in vedges_by_x:
        for (i1,i2) in vedges_by_x[j]:
            for i in range(i1,i2+1):
                fill2.add((i,j))

    if len(fill.intersection(fill2)):
        print("fills overlap")
        ipy.embed()

    print(f"fill size {len(fill)} with {len(remf)} removed edges plus {len(fill2)} from vertical edges:")
    s = print_grid(fill, fill2, edge=1)
    print(s.count("#") + s.count("@"), "total fill")
    return len(fill), len(remf), len(fill2)


if __name__=="__main__":
    filename = sys.argv[1]
    if os.path.exists(filename):
        text = open(filename).read()
    else:
        text = load_file(filename, year=2023, day=18)

    entries, colors = parse_instructions(text)

    print("Part 1:")
    outline = dig_outline(entries)
    fill = get_fill(outline)
    print("\nArea fill:", len(fill))

    print("\nPart 2:")
    bentries = parse_colors(colors)

    # with open("inputs/day18_practice4.txt", 'w') as f:
    #     print("\n".join([f"{d} {n} #0000" for (d,n) in bentries]), file=f)

    corners_by_x, vedges_by_x, hprint = dig_big_outline(entries)
    nfill, nrem, nvert = get_big_fill(corners_by_x, vedges_by_x, reference=(outline,fill))
    snfill, snrem, snvert = print_big_fill(corners_by_x, vedges_by_x)
    print(f"V1: Area fill: {nfill} (not including {nrem} removed vertical edges) + {nvert} total vertical edges = {nfill+nvert}")
    print(f"V2: Area fill: {snfill} (not including {snrem} removed vertical edges) + {snvert} total vertical edges = {snfill+nvert}")

    ipy.embed()