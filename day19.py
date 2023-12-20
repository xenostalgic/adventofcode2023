from collections import Counter, defaultdict
from dataclasses import dataclass, field
import itertools
import os
from typing import Collection
import numpy as np
import regex as re
import sys

from tqdm import tqdm
from utils import load_file, prod, toverlap, toverlap_size, tplus

import IPython as ipy

OPS = {
    "<": lambda a,b: a<b,
    ">": lambda a,b: a>b,
}

MAX_PATH_LEN = 0

def parse_rules(rule_text):
    rulesets = defaultdict(list)
    base_cond = "or {x}<0 or {m}<0 or {a}<0 or {s}<0"
    for line in rule_text.splitlines():
        key, *rules = re.split(r"{|,", line[:-1])
        for rule in rules:
            if ":" in rule:
                cond, dest = rule.split(":")
                var, op, thresh, = re.split(r"(<|>)", cond)
            else:
                # conditionless destination
                var, op, thresh, dest = None, None, 0, rule
            rulesets[key].append((var, op, int(thresh), dest))
    return rulesets


def parse_parts(part_text):
    pts = part_text.splitlines()
    parts = []
    for pt in pts:
        part_map = dict((k,int(v)) for k,v in (p.split("=") for p in pt.strip("}{").split(",")))
        parts.append(part_map)
    return parts


def parse_input(text):
    rule_text, part_text = text.split("\n\n")
    rulesets = parse_rules(rule_text)
    parts = parse_parts(part_text)
    return rulesets, parts


def eval_ruleset(ruleset, part):
    for rule in ruleset:
        var, op, thresh, dest = rule
        if var is None or OPS[op](part[var], thresh):
            return dest
    print("no dest??")
    ipy.embed()


def check_accepted(rulesets, part):
    global MAX_PATH_LEN
    cur_key = "in"
    past_keys = [cur_key]
    path_length = 0
    while True:
        next_key = eval_ruleset(rulesets[cur_key], part)
        if next_key == "A":
            return True
        elif next_key == "R":
            return False
        else:
            path_length += 1
            MAX_PATH_LEN = max(MAX_PATH_LEN, path_length)
            past_keys.append(cur_key)
            cur_key = next_key
        if len(past_keys) > len(rulesets) or cur_key in past_keys:
            print("looping rule?")
            ipy.embed()


def sum_ratings(parts):
    tot = 0
    for p in parts:
        tot += sum(p.values())
    return tot


def partition(rulesets: list[tuple], ranges=None, cur_key="in", cur_idx=0, depth: list[tuple] = None):
    if ranges is None:
        ranges = {var:(1,4001) for var in "xmas"}
    if depth is None:
        depth = []
    new_depth = depth + [(cur_key, cur_idx)]

    if cur_key == "A":
        return prod([(v[1]-v[0]) for v in ranges.values()])
    elif cur_key == "R":
        return 0

    var, op, thresh, dest = rulesets[cur_key][cur_idx]
    if var == None:
        return partition(rulesets, ranges, dest, 0, depth=new_depth)

    lo, hi = ranges[var]
    lo_ranges, hi_ranges = ranges.copy(), ranges.copy()
    if lo <= thresh < hi:
        # both sides of the threshold are possible
        if op == ">":
            hi_ranges[var] = (thresh+1, hi)
            lo_ranges[var] = (lo, thresh+1)
            lo_c = partition(rulesets, lo_ranges, cur_key, cur_idx+1, depth=new_depth)
            hi_c = partition(rulesets, hi_ranges, dest, 0, depth=new_depth)
        elif op == "<":
            hi_ranges[var] = (thresh, hi)
            lo_ranges[var] = (lo, thresh)
            lo_c = partition(rulesets, lo_ranges, dest, 0, depth=new_depth)
            hi_c = partition(rulesets, hi_ranges, cur_key, cur_idx+1, depth=new_depth)
        return lo_c + hi_c
    elif (lo > thresh and op == ">") or (hi <= thresh and op == "<"):
        # full range passes this rule
        rec_c = partition(rulesets, ranges, dest, 0, depth=new_depth)
        return rec_c
    elif (lo > thresh and op == "<") or (hi <= thresh and op == ">"):
        itr_c = partition(rulesets, ranges, cur_key, cur_idx+1, depth=new_depth)
        return itr_c
    else:
        print("Unhandled case?")
        ipy.embed()


if __name__=="__main__":
    filename = sys.argv[1]
    if os.path.exists(filename):
        text = open(filename).read()
    else:
        text = load_file(filename, year=2023, day=19)

    rulesets, parts = parse_input(text)

    print("Part 1:")
    accepted_parts = [part for part in parts if check_accepted(rulesets, part)]
    sr = sum_ratings(accepted_parts)
    print("\nAccepted sum of ratings:", sr)
    print("Max path length:", MAX_PATH_LEN)

    print("\nPart 2:")
    ptcount = partition(rulesets)
    if "practice" in filename and ptcount == 167409079868000:
        print("Matches expected value")
    pct = ptcount*100 / (4000**4) 
    print(f"Total possible rating combinations: {ptcount} ({pct}% of possible)")