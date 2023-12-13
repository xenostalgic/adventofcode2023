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
        entries.append((springs,counts))
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

fis_memo = {}
def fits_in_stretch(orig_counts, orig_stretch, cidx, nidx):
    if (cidx, nidx) in fis_memo:
        return fis_memo[(cidx, nidx)]
    stretch = orig_stretch[nidx:]
    counts = orig_counts[cidx:]
    if len(stretch)==0:
        fis_memo[(cidx, nidx)] = 0
        return 0
    ls = len(stretch)
    room = sum(counts)+len(counts)-1
    n = 0
    for i in range(ls):
        if ls-i < room:
            continue
        noff = i+counts[0]+1
        if noff == len(stretch) or stretch[noff]=="?": # doesn't have to be damaged
            if len(counts) == 1:
                n += 1
            else:
                n += fits_in_stretch(orig_counts, orig_stretch, cidx+1, nidx+noff)
    fis_memo[(cidx, nidx)] = n
    return n


fir_memo = {}
def fits_in_row(orig_counts, orig_span, clo, chi, slo, shi, depth=0):
    # if (clo, chi, slo, shi) in fir_memo:
    #     return fir_memo[(clo, chi, slo, shi)]
    span = orig_span[slo:shi]
    counts = orig_counts[clo:chi]

    # trim recursion
    if len(span) == 0:
        fir_memo[(clo, chi, slo, shi)] = 0
        return 0
    if len(counts) == 0:
        return 1
    if len([ch for ch in span if ch in "?#"]) < sum(counts):
        return 0
    if len(span) < sum(counts)+len(counts)-1:
        return 0

    if depth > 100:
        ipy.embed()

    if shi < len(orig_span) and orig_span[shi]=="#":
        print("span ends right before a #")
        ipy.embed()
    if span.startswith(".") or span.endswith("."):
        print("leading/trailing .")
        ipy.embed()

    if "." in span:
        sidx = slo+span.index(".")
        n = 0
        for csplit in range(clo, chi+1):
            # TODO: check off-by-ones
            print("\t"*depth + f"Splitting span {span} on sidx {sidx}", flush=True)
            print("\t"*depth + f"Calling lo split (span {slo}:{sidx}={orig_span[slo:sidx]}, counts {orig_counts[clo:csplit]}), depth {depth}", flush=True)
            count_lo = fits_in_row(orig_counts, orig_span, clo, csplit, slo, sidx, depth=depth+1)
            print("\t"*depth + f"Calling hi split (span {sidx}:{shi+1}={orig_span[sidx:shi+1]}), counts {orig_counts[csplit:chi]}), depth {depth}", flush=True)
            count_hi = fits_in_row(orig_counts, orig_span, csplit, chi, sidx+1, shi, depth=depth+1)
            print("\t"*depth + f"Got {count_lo}, {count_hi} ways --> total {count_lo*count_hi}", flush=True)
            n += count_lo*count_hi
    else:
        # contiguous span of # and ?. treat as single-count case times ways for remainder
        n = 0
        c = counts[0]
        print("\t"*depth + f"Got span {span} ({slo,shi} from orig span {orig_span}) with counts {counts}", flush=True)
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
                print("\t"*depth + f"Assign {c} to {slo+start_offset,slo+end_offset}; no remaining counts --> 1 way", flush=True)
                n += 1
            else:
                print("\t"*depth + f"Assign {c} to {slo+start_offset,slo+end_offset}; recurse on span {orig_span[slo+end_offset+1:shi]} with counts {orig_counts[clo+1:chi]}", flush=True)
                r = fits_in_row(orig_counts, orig_span, clo+1, chi, slo+end_offset+1, shi, depth=depth+1)
                print("\t"*depth + f"Got {r} ways", flush=True)
                n += r

    print("\t"*depth + f"Span {orig_span[slo:shi]} fits counts {orig_counts[clo:chi]} {n} ways", flush=True)
    fir_memo[(clo, chi, slo, shi)] = n
    return n


def rec_fir(entry):
    springs, counts = entry
    springs = re.sub("\.+", ".", springs)
    springs = springs.strip(".")
    n = fits_in_row(counts, springs, 0, len(counts), 0, len(springs))
    print(f"Row {springs} fits counts {counts} {n} ways\n")
    # ipy.embed()
    return n


if __name__=="__main__":
    filename = sys.argv[1]
    if "practice" in filename:
        text = open(filename).read()
    else:
        text = load_file(filename, year=2023, day=12)
    
    print("Part 1:")
    entries = parse_input(text)
    varcs = [rec_fir(entry) for entry in entries]
    print(sum(varcs))
