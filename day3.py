from collections import defaultdict
from utils import isdigit, extract_nums
import numpy as np


def get_syms(lines: list[str]) -> set[str]:
    """Get the set of non-digit, non-period symbols in the text.

    Args:
        lines (list[str]): A list of lines

    Returns:
        set: A set of symbols.
    """
    chars = set("".join([l.strip() for l in lines]))
    return set([ch for ch in chars if not isdigit(ch) and ch != "."])


def get_symdices(lines: list[str], syms: set[str]) -> list[tuple[int, int]]:
    symdices = []
    for i in range(len(lines)):
        symdices.extend([(i,j) for j,ch in enumerate(lines[i]) if ch in syms])
    return symdices


def get_nums(lines: list[str]) -> defaultdict[list[tuple[str, tuple[int,int]]]]:
    part_nums = defaultdict(list)
    for i in range(len(lines)):
        line_nums = extract_nums(lines[i])
        for n, idxs in line_nums:
            part_nums[i].append((n, idxs))
    return part_nums


def get_adjacent_nums(
    lines: list[str],
    symdices: list[tuple[int, int]],
    part_nums: defaultdict[list[tuple[str, tuple[int,int]]]]
) -> list[tuple]:
    adj_nums = set()
    for symdx in symdices:
        si, sj = symdx
        for ni in [si-1, si, si+1]: # look at adjacent rows
            for part_num in part_nums[ni]:
                num, (n_open, n_close) = part_num
                if sj in range(n_open-1, n_close+1):
                    adj_nums.add((num, (ni,n_open), (ni, n_close)))
                    sym = lines[si][sj]
    return adj_nums


def get_gear_ratios(
    lines: list[str],
    symdices: list[tuple[int, int]],
    part_nums: defaultdict[list[tuple[str, tuple[int,int]]]]
) -> list[tuple]:
    ratios = []
    for symdx in symdices:
        si, sj = symdx
        sym = lines[si][sj]
        if sym != "*":
            continue
        gear_nums = []
        for ni in [si-1, si, si+1]: # look at adjacent rows
            for part_num in part_nums[ni]:
                num, (n_open, n_close) = part_num
                if sj in range(n_open-1, n_close+1):
                    gear_nums.append((num, (ni,n_open), (ni, n_close)))
        if len(gear_nums) == 2:
            g1 = int(gear_nums[0][0])
            g2 = int(gear_nums[1][0])
            ratios.append(g1*g2)
                    
    return ratios


if __name__=="__main__":
    print("Part 1:")
    lines = [line.strip() for line in open("inputs/3.txt")]
    syms = get_syms(lines)
    symdices = get_symdices(lines, syms)
    part_nums = get_nums(lines)
    adj_nums = get_adjacent_nums(lines, symdices, part_nums)
    print(sum([int(num[0]) for num in adj_nums]))
    print("Part 2:")
    ratios = get_gear_ratios(lines, symdices, part_nums)
    print(sum(ratios))


