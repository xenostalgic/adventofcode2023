from collections import defaultdict
import itertools
import regex as re
import sys
from utils import load_file

import IPython as ipy

def pc_regex(entry):
    springs, stretches, counts, sunks = entry
    ipy.embed()
    pattern = "[\.\?]+".join(f"[#|\?]{{{ci}}}" for ci in counts)
    re.findall(pattern, springs, overlapped=True)


def parse_input(text):
    entries = []
    for row in text.splitlines():
        springs, counts = row.split()
        counts = list(map(int,re.findall(r"\d+", counts)))
        unks = [(i,ch) for i,ch in enumerate(springs) if ch=="?"]
        entries.append((list(springs),counts,unks))
    return entries

def parse_stretches(text):
    entries = []
    for row in text.splitlines():
        springs, counts = row.split()
        counts = list(map(int,re.findall(r"\d+", counts)))
        stretches = re.findall(r"[\?|#]+", springs)
        sunks = {}
        for si,s in enumerate(stretches):
            unks = [(i,ch) for i,ch in enumerate(springs) if ch=="?"]
            sunks[(si,s)] = unks
        entries.append((springs, stretches,counts,sunks))
    return entries

def possible_combs(entries):
    var_counts = []
    for eidx, entry in enumerate(entries):
        schs, counts, unks = entry
        entry_vars = []
        for perm in itertools.permutations(unks):
            for i in range(0,len(unks)+1):
                svar = schs.copy()
                for unk in perm[:i]:
                    svar[unk[0]] = "#"
                for unk in perm[i:]:
                    svar[unk[0]] = "."
                entry_vars.append("".join(svar))
        en = 0
        compats = []
        for sstr in set(entry_vars):
            # if sstr == "#.#.###":
            #     print("Found tgt")
            #     ipy.embed()
            dmg_spans = re.findall(r"#+", sstr)
            if len(dmg_spans) != len(counts):
                continue
            compat = True
            for i,sp in enumerate(dmg_spans):
                if i >= len(counts) or counts[i] != len(sp):
                    compat = False
                    break
            if compat:
                en += 1
                compats.append(sstr)
        var_counts.append(en)
        print(f"Row {eidx} compatible variants:", en)

        if en == 17:
            ipy.embed()
    return var_counts


def compat_counts(vstr, counts):
    dmg_spans = re.findall(r"#+", vstr)
    if len(dmg_spans) != len(counts):
        return False
    for i,sp in enumerate(dmg_spans):
        if i >= len(counts) or counts[i] != len(sp):
            return False
    return True


def get_variants(stretch, unks):
    svars = []
    sl = list(stretch)
    for perm in itertools.permutations(unks):
        for i in range(len(unks)+1):
            ssv = sl.copy()
            for unk in perm[:i]:
                ssv[unk[0]] = "#"
            for unk in perm[i:]:
                ssv[unk[0]] = "."
            svars.append("".join(ssv))
    return svars


def fit_in_stretch(stretch, counts):
    if len(stretch)==0:
        return 0
    ls = len(stretch)
    room = sum(counts)+len(counts)-1
    n = 0
    for i in range(ls):
        if ls-i < room:
            continue
        nidx = i+counts[0]+1
        if nidx == len(stretch) or stretch[nidx]=="?": # doesn't have to be damaged
            if len(counts) == 1:
                n += 1
            else:
                n += fit_in_stretch(stretch[nidx:], counts[1:])
    return n


def possible_combs_stretches(entry):
    stretches, counts, sunks = entry
    while len(stretches[0]) < counts[0]:
        stretches = stretches[1:]
    while len(stretches[-1]) < counts[-1]:
        stretches = stretches[:-1]

    sidx_to_cidxs = defaultdict(dict)
    for sidx, s in enumerate(stretches):
        for cidx, c in enumerate(counts):
            if c > len(s) or "#"*(c+1) in s:
                # current count can't fit, so can't continue with current or any more
                break
            n = fit_in_stretch(s,counts[:cidx+1])
            sidx_to_cidxs[sidx][(0,cidx+1)] = n
        if sidx == 0:
            continue
        for sidx2 in range(sidx):
            pcidxs = set(pcidx2 for (pcidx1,pcidx2) in sidx_to_cidxs[sidx2])
            for pcidx in pcidxs:
                for cidx in range(pcidx,len(counts)):
                    c = counts[cidx]
                    if c > len(s) or "#"*(c+1) in s:
                        # current count can't fit
                        break
                    next = fit_in_stretch(s,counts[pcidx:cidx+1])
                    if (pcidx,cidx+1) not in sidx_to_cidxs[sidx]:
                        sidx_to_cidxs[sidx][(pcidx,cidx+1)] = 0
                    sidx_to_cidxs[sidx][(pcidx,cidx+1)] += next

    # DP the sidx/cidx flow
    tot = 0
    cp_n = {}
    for cidx1 in range(len(counts)):
        for cidx2 in range(len(counts)):
            # total ways to cover counts[cidx1:cdix2] in a single stretch
            n = 0
            for sidx in sidx_to_cidxs:
                for (pc1,pc2),ways in sidx_to_cidxs[sidx].items():
                    if pc2 != cidx:
                        continue
                    n += ways
            cp_n[(cidx1,cidx2)] = n
    # recurse???? idk
            


        





if __name__=="__main__":
    filename = sys.argv[1]
    if "practice" in filename:
        text = open(filename).read()
    else:
        text = load_file(filename, year=2023, day=12)
    
    print("Part 1:")
    entries = parse_stretches(text)
    # varcs = possible_combs(entries)
    varcs = [possible_combs_stretches(entry) for entry in entries]
    print(sum(varcs))

    # print("\nPart 2:")

    # print(res)
