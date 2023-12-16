from collections import defaultdict
import itertools
import numpy as np
import regex as re
import sys

from tqdm import tqdm
from utils import load_file, read_grid

import IPython as ipy

def hash(s: str):
    sasc = s #.decode("ascii")
    hval = 0
    for ch in sasc:
        aval = ord(ch)
        hval = ((hval+aval)*17) % 256
    return hval


def print_box_state(hm):
    for k,ll in hm.items():
        if len(ll) == 0:
            continue
        print(f"Box {k}:", ll)
    print("")


def run_hashmap(seq: list[str]):
    hm = defaultdict(list)

    # run initialization sequence
    for entry in seq:
        if entry.endswith("-"):
            sval = entry[:-1]
            hval = hash(sval)
            labels = [lens[0] for lens in hm[hval]]
            if sval in labels:
                idx = labels.index(sval)
                hm[hval] = hm[hval][:idx] + hm[hval][idx+1:]
        elif "=" in entry:
            sval, fl = entry.split("=")
            hval = hash(sval)
            labels = [lens[0] for lens in hm[hval]]
            if sval in labels:
                idx = labels.index(sval)
                hm[hval][idx] = (sval, int(fl))
            else:
                hm[hval].append((sval, int(fl)))

    # get total focusing power
    fp = 0
    for box_idx in range(256):
        for lens_idx, lens in enumerate(hm[box_idx], start=1):
            power = (box_idx+1) * lens_idx * lens[1]
            print(f"For box {box_idx} slot {lens_idx} lens {lens}: {power}")
            fp += power
    
    return fp


if __name__=="__main__":
    filename = sys.argv[1]
    if "practice" in filename or len(filename) == 0:
        text = "rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7"
    else:
        text = load_file(filename, year=2023, day=15)

    seq = text.replace("\n", "").split(",")

    print("Part 1:")
    print("Hash of HASH:", hash("HASH"))
    print("Hash of initialization sequence:", sum([hash(val) for val in seq]))

    print("\nPart 2:")
    fp = run_hashmap(seq)
    print("Focusing power:", fp)
