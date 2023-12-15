from collections import defaultdict
import itertools
import regex as re
import sys

from tqdm import tqdm
from utils import load_file

import IPython as ipy

def parse_input(text):
    entries = []
    for row in text.splitlines():
        springs, counts = row.split()
        counts = list(map(int,re.findall(r"\d+", counts)))
        entries.append((springs,counts))
    return entries

FIR_MEMO = {}

def fits_in_row(orig_counts, orig_span, clo, chi, slo, shi, depth=0):
    debug = False
    # if "??.????????????.?????" in orig_span:
    #     debug = True
        # ipy.embed()
    global FIR_MEMO
    if (clo, chi, slo, shi) in FIR_MEMO:
        return FIR_MEMO[(clo, chi, slo, shi)]
    span = orig_span[slo:shi]
    counts = orig_counts[clo:chi]

    # trim recursion
    if len(span) == 0:
        FIR_MEMO[(clo, chi, slo, shi)] = 0 #[]
        return 0 #[]
    if len(counts) == 0:
        ipy.embed()
    if span.count("#")+span.count("?") < sum(counts):
        return 0 #[]
    if span.count("#") > sum(counts):
        return 0 #[]
    # if len(span) < sum(counts)+len(counts)-1:
    #     return 0 #[]
    if span.startswith("."):
        return fits_in_row(orig_counts, orig_span, clo, chi, slo+1, shi, depth=depth)
    if span.endswith("."):
        return fits_in_row(orig_counts, orig_span, clo, chi, slo, shi-1, depth=depth)

    if depth > 100:
        ipy.embed()

    if shi < len(orig_span) and orig_span[shi]=="#":
        print("span ends right before a #")
        ipy.embed()

    # contiguous span of # and ?. treat as single-count case times ways for remainder
    # assignments = []
    n = 0
    c = counts[0]
    if debug: print("\t"*depth + f"Got span {span} ({slo,shi} from orig span {orig_span}) with counts {counts}", flush=True)
    # if span == "?.#?" and orig_span == "??????#????.#?" and counts == [1]:
    #     ipy.embed()
    for start_offset in range(len(span)):
        end_offset = start_offset+c
        if end_offset > len(span):
            # not enough room for the first chunk
            break
        if "#" in span[:start_offset]:
            # required damaged chars before the first chunk
            break
        if "." in span[start_offset:end_offset]:
            # chunk can't be continuous
            continue
        if slo+end_offset < len(orig_span) and orig_span[slo+end_offset] == "#":
            # next char is damaged, so first chunk can't end here
            continue
        if len(counts) == 1:
            if span[end_offset+1:].count("#") > 0:
                continue
            if debug: print("\t"*depth + f"Assign {c} to {slo+start_offset,slo+end_offset}; no remaining counts --> 1 way", flush=True)
            # assignments.append([(c,slo+start_offset,slo+end_offset)])
            n += 1
        else:
            if debug: print("\t"*depth + f"Assign {c} to {slo+start_offset,slo+end_offset}; recurse on span {orig_span[slo+end_offset+1:shi]} with counts {orig_counts[clo+1:chi]}", flush=True)
            r = fits_in_row(orig_counts, orig_span, clo+1, chi, slo+end_offset+1, shi, depth=depth+1)
            # if debug: print("\t"*depth + f"Got {len(r)} ways", flush=True)
            if debug: print("\t"*depth + f"Got {r} ways", flush=True)
            # assignments.extend([[(c,slo+start_offset,slo+end_offset)]+ra for ra in r])
            n += r

    # n = len(assignments)
    if debug: print("\t"*depth + f"Span {orig_span[slo:shi]} fits counts {orig_counts[clo:chi]} {n} ways", flush=True)
    if chi-clo == len(orig_counts) and shi-slo == len(orig_span):
        FIR_MEMO = {}
    else:
        FIR_MEMO[(clo, chi, slo, shi)] = n # assignments

    return n #assignments


def check_assignments(agns: list[tuple], springs: str, counts: list[int]):
    lens = [len(agn) for agn in agns]
    if len(set(lens)) > 1:
        print("Varying assignment lengths")
        ipy.embed()
    for agn in agns:
        if [a[0] for a in agn] != counts:
            print("Mismatched counts")
            ipy.embed()
        astr = ""
        for i,ch in enumerate(springs):
            if ch == "?":
                if any([alo<=i<ahi for c,alo,ahi in agn]):
                    astr += "#"
                else:
                    astr += "."
            else:
                astr += ch
        spans = list(re.findall(r"#+", astr))
        slens = [len(span) for span in spans]
        if slens != counts:
            print(f"assignment doesn't work: got {astr} with lens {slens} for counts {counts}")
            ipy.embed()
    return True

def rec_fir(entry):
    springs, counts = entry
    springs = re.sub("\.+", ".", springs)
    springs = springs.strip(".")
    n = fits_in_row(counts, springs, 0, len(counts), 0, len(springs))
    return n


def unfold(entries):
    unfolded_entries = []
    for entry in entries:
        springs, counts = entry
        ucounts = []
        for i in range(5):
            ucounts += counts
        unfolded_entries.append(("?".join([springs]*5), ucounts))
    return unfolded_entries


if __name__=="__main__":
    filename = sys.argv[1]
    if "practice" in filename:
        text = open(filename).read()
    else:
        text = load_file(filename, year=2023, day=12)

    entries = parse_input(text)

    print("Part 1:")
    varcs = [rec_fir(entry) for entry in entries]
    print(sum(varcs))
    
    print("\nPart 2:")
    unfolded = unfold(entries)
    varcs = [rec_fir(entry) for entry in tqdm(unfolded)]
    print(sum(varcs))

