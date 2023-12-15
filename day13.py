from collections import defaultdict
import itertools
import regex as re
import sys

from tqdm import tqdm
from utils import load_file, read_grid

import IPython as ipy

def edit_distance(s1, s2):
    return sum([1 if (s1[i]!=s2[i]) else 0 for i in range(len(s1))])


def check_row_reflection(pattern):
    ridx = None
    for i in range(0,len(pattern)-1):
        i2 = i + 1
        reflects = True
        rcount = 0
        dist_to_edge = min(i+1, len(pattern)-i2)
        for d in range(dist_to_edge):
            r1, r2 = pattern[i-d], pattern[i2+d]
            if r1 != r2:
                reflects = False
                break
            else:
                print("row match:", r1,r2)
                rcount += 1
        if rcount >= dist_to_edge and reflects:
            print(f"Row reflection between rows {i} and {i2}!")
            ridx = i
    return ridx


def check_col_reflection(pattern):
    cidx = None
    for i in range(0,len(pattern[0])-1):
        i2 = i + 1
        reflects = True
        ccount = 0
        dist_to_edge = min(i+1, len(pattern[0])-i2)
        for d in range(dist_to_edge):
            c1 = "".join([row[i-d] for row in pattern])
            c2 = "".join([row[i2+d] for row in pattern])
            if c1 != c2:
                reflects = False
                break
            else:
                print("col match:", c1,c2)
                ccount += 1
        if ccount >= dist_to_edge and reflects:
            print(f"Col reflection between cols {i} and {i2}!")
            cidx = i
    return cidx


def check_smudged_row_reflection(pattern):
    ridx = None
    for i in range(0,len(pattern)-1):
        i2 = i + 1
        total_error = 0
        dist_to_edge = min(i+1, len(pattern)-i2)
        for d in range(dist_to_edge):
            r1, r2 = pattern[i-d], pattern[i2+d]
            total_error += edit_distance(r1,r2)
        if total_error == 1:
            print(f"Row reflection between rows {i} and {i2}!")
            ridx = i
    return ridx


def check_smudged_col_reflection(pattern):
    cidx = None
    for i in range(0,len(pattern[0])-1):
        i2 = i + 1
        total_error = 0
        dist_to_edge = min(i+1, len(pattern[0])-i2)
        for d in range(dist_to_edge):
            c1 = "".join([row[i-d] for row in pattern])
            c2 = "".join([row[i2+d] for row in pattern])
            total_error += edit_distance(c1,c2)
        if total_error == 1:
            print(f"Col reflection between cols {i} and {i2}!")
            cidx = i
    return cidx

if __name__=="__main__":
    filename = sys.argv[1]
    if "practice" in filename:
        text = open(filename).read()
    else:
        text = load_file(filename, year=2023, day=12)

    patterns = [read_grid(chunk) for chunk in text.split("\n\n")]
    print("Part 1:")
    cidxs = [] #check_col_reflection(pattern) for pattern in patterns]
    ridxs = [] #check_row_reflection(pattern) for pattern in patterns]
    for pattern in patterns:
        cidx = check_col_reflection(pattern)
        ridx = check_row_reflection(pattern)
        if cidx is not None:
            cidxs.append(cidx)
        elif ridx is not None:
            ridxs.append(ridx)
        else:
            print("Both none??")
            ipy.embed()
    csum = sum([c+1 for c in cidxs])
    rsum = sum([r+1 for r in ridxs])
    print(f"{csum} + ({rsum}*100) = {csum+100*rsum}")

    print("\nPart 2:")
    cidxs = [check_smudged_col_reflection(pattern) for pattern in patterns]
    ridxs = [check_smudged_row_reflection(pattern) for pattern in patterns]
    csum = sum([c+1 for c in cidxs if c is not None])
    rsum = sum([r+1 for r in ridxs if r is not None])
    print(f"{csum} + ({rsum}*100) = {csum+100*rsum}")
