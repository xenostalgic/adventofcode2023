from typing import Any
import numpy as np
from functools import reduce
from itertools import product

import IPython as ipy

W2N = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]

def num_spelled(s):
    if s in W2N:
        return W2N.index(s)
    return False

def isdigit(s):
    return s in "0123456789"

def isnum(s):
    try:
        float(s)
        return True
    except:
        return False
    
def prod(nums):
    base = 1
    for n in nums:
        base = base*n
    return base

def extract_nums(s):
    nums = []
    binary_s = "".join(["0" if isdigit(ch) else "." for ch in s])
    op = binary_s.find("0")
    iter = 0
    while op != -1:
        j = binary_s[op:].find(".")
        if j == -1:
            nums.append((s[op:], (op,len(s))))
            return nums
        cl = op + j
        nums.append((s[op:cl], (op,cl)))
        i = binary_s[cl:].find("0")
        if i == -1:
            break
        op = cl + i
        iter += 1
        if iter > len(binary_s):
            print("Error extracting numbers")
            ipy.embed()
    return nums

NUM_MAP = {str(i): i for i in range(10)}
NUM_MAP["."] = -1
NUM_MAP["default"] = -2

def to_array(lines: list[str], ch_map: dict[str, Any] = NUM_MAP) -> np.ndarray:
    """Convert an input map to a numpy array.

    Args:
        lines (list[str]): A list of strings
        ch_map (dict[str, Any], optional): An optional mapping of string values to ints. Defaults to NUM_MAP.

    Returns:
        np.ndarray: A numpy array representing the input numerically.
    """
    h = len(lines)
    w = len(lines[0])
    arr = np.zeros((h,w))
    for i, line in enumerate(lines):
        for j, ch in enumerate(line):
            if ch in ch_map:
                val = ch_map[ch]
            else:
                val = ch_map["default"]
            arr[i,j] = val
    return val




