
import sys

import IPython as ipy

def parse_map(lines):
    # input format: dest range start, source range start, range size
    # output format: source range start & end : offset
    sdmap: dict[tuple[int,int],int] = {}
    src_type, tgt_type = None, None
    for line in lines:
        if "map" in line:
            map_type = line.split()[0]
            src_type, _, tgt_type = map_type.split("-")
        else:
            drs, srs, size = map(int, line.split())
            sdmap[(srs, srs+size)] = (drs - srs)
    return src_type, tgt_type, sdmap

def parse_almanac(text):
    almanac: dict[str, dict] = {}
    chunks = text.strip().split("\n\n")
    seeds = list(map(int, chunks[0].split()[1:]))
    mtypes = set(["seed"])
    for chunk in chunks[1:]:
        src, tgt, cmap = parse_map(chunk.split("\n"))
        almanac[(src,tgt)] = cmap
        mtypes.add(src)
        mtypes.add(tgt)
    return seeds, almanac, mtypes


def get_materials_sets(seeds: list[int], almanac: dict[str, dict], mtypes: set[str]):
    material_sets = []
    for seed in seeds:
        curtype = "seed"
        curval = seed
        mats = {curtype: curval}
        while len(mats) < len(mtypes):
            for (srctype,tgttype),tmap in almanac.items():
                if srctype != curtype:
                    continue
                tgtval = curval
                for (lo,hi),offset in tmap.items():
                    if lo <= curval < hi:
                        tgtval = curval + offset
                        break
                mats[tgttype] = tgtval
                curtype = tgttype
                curval = tgtval
        material_sets.append(mats)
    return material_sets


def get_spans(vals: list[int]):
    spans = []
    i = 0
    while i < len(vals):
        spans.append((vals[i], vals[i]+vals[i+1]))
        i += 2
    return spans


def span_intersection(span1: tuple[int, int], span2: tuple[int, int]):
    # returns intersecting span or None

    # no overlap cases
    if (span1[1] <= span2[0]) or (span2[1] <= span1[0]):
        return None

    # containment cases
    if (span1[0] <= span2[0]) and (span1[1] >= span2[1]):
        return span2
    elif (span2[0] <= span1[0]) and (span2[1] >= span1[1]):
        return span1

    # partial overlap cases
    if (span1[0] < span2[0]) and (span1[1] < span2[1]):
        return (span2[0], span1[1])
    elif (span2[0] < span1[0]) and (span2[1] < span1[1]):
        return (span1[0], span2[1])
    

def merge_spans(spans: list[tuple[int,int]]):
    new_spans = []
    i = 0
    while i < len(spans):
        si = spans[i]
        new_span = si
        if i+1 == len(spans):
            # nothing to merge with this span
            new_spans.append(si)
            break
        for j in range(i+1, len(spans)):
            sj = spans[j]
            if span_intersection(si,sj) is None:
                # not adjacent; add new_span and move on
                new_spans.append(new_span)
                break
            else:
                # merge sj and keep looking for merges
                new_span = (si[0], max(si[1], sj[1]))
        i = j
    return new_spans
    

def spanlist_sum(spans: list[tuple[int,int]]):
    tot = 0
    for span in spans:
        tot += span[1]-span[0]
    return tot


def get_materials_sets_spans(seed_spans: list[tuple[int,int]], almanac: dict[str, dict], mtypes: set[str]):
    material_spans = {"seed": seed_spans}

    curtype = "seed"
    cur_spans = seed_spans
    while curtype != "location":
        s = spanlist_sum(cur_spans)
        # print(f"{len(cur_spans)} spans for type '{curtype}' with a total of {s} elements")
        # find next type mapping
        for (srctype,tgttype),tmap in almanac.items():
            if srctype == curtype:
                break

        tgt_spans = []
        for src_span in cur_spans:
            # map each src span into tgt span(s)
            mapped_segs = []
            for tgt_span,offset in tmap.items():
                sp_int = span_intersection(src_span, tgt_span)
                if sp_int is None:
                    continue
                mapped_segs.append(sp_int)
                tgt_int = (sp_int[0]+offset, sp_int[1]+offset)
                tgt_spans.append(tgt_int)

            # add the identity mapping for any gaps in mapped_segs
            mapped_segs = sorted(mapped_segs, key=lambda seg: seg[0])
            if len(mapped_segs) == 0:
                # all identity
                tgt_spans.append(src_span)
                continue
            if src_span[0] < mapped_segs[0][0]:
                tgt_spans.append((src_span[0], mapped_segs[0][0]))
            if src_span[1] > mapped_segs[-1][1]:
                tgt_spans.append((mapped_segs[-1][1], src_span[1]))
            for i in range(len(mapped_segs)-1):
                cseg = mapped_segs[i]
                nseg = mapped_segs[i+1]
                if cseg[1] < nseg[0]:
                    tgt_spans.append((cseg[1],nseg[0]))

        # merge tgt spans as much as possible (if needed)
        if len(tgt_spans) > len(cur_spans):
            tgt_spans = sorted(tgt_spans, key=lambda seg: seg[0])
            tgt_spans = merge_spans(tgt_spans)

        material_spans[tgttype] = tgt_spans
        curtype = tgttype
        cur_spans = tgt_spans

    return material_spans["location"]


if __name__=="__main__":
    input = open(sys.argv[1]).read()
    print("Part 1:")
    print("Get almanac:")
    seeds, almanac, mtypes = parse_almanac(input)
    print("Get material sets:")
    msets = get_materials_sets(seeds, almanac, mtypes)
    min_loc = min([mset["location"] for mset in msets])
    print("Minimum location value:", min_loc)
    print("Part 2:")
    seed_spans = get_spans(seeds)
    loc_spans = get_materials_sets_spans(seed_spans, almanac, mtypes)
    min_loc2 = min([min(loc_span) for loc_span in loc_spans])
    print("Minimum location value:", min_loc2)
