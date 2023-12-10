from dataclasses import dataclass
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


def gcd(a: int, b: int):
    while b > 0:
        a, b = b, a % b
    return a


def lcm(a: int, b: int):
    return abs(a)*(abs(b)/gcd(a,b))


def lcm_n(nums: list[int]):
    return reduce(lcm, nums)


### SEARCH

def manhattan_distance(pos1, pos2):
    return sum((d1-d2)**2 for d1,d2 in zip(pos1,pos2))

def euclidian_distance(pos1, pos2):
    return np.sqrt(sum((d1-d2)**2 for d1,d2 in zip(pos1,pos2)))

@dataclass
class Node:
    pos: tuple[int,int]
    cost: int
    hist: list

    def next(self):
        for x in [1,0,-1]:
            for y in [1,0,-1]:
                npos = (self.pos[0]+y, self.pos[1]+x)
                yield Node(npos, self.cost+1, self.hist + [self.pos])

    def heuristic(self, tgt_nodes: list):
        dists = [euclidian_distance(self.pos, tgt.pos) for tgt in tgt_nodes]
        return min(dists)


def bfs(start_node: Node, tgt_nodes: list[Node]):
    pos_to_cost = {start_node.pos: start_node}
    beam_history = []

    for step_idx in range(10000):
        t += 1
        new_nodes = {} # map from position to full node
        for node_pos, node in nodes.items():
            for next in node.next():
                new_nodes[next.pos] = next
        beam_history.append(nodes)
        nodes = new_nodes
        if any([tgt.pos in nodes for tgt in tgt_nodes]):
            break

    return step_idx


