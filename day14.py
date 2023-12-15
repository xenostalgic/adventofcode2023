from collections import defaultdict
import itertools
import numpy as np
import regex as re
import sys

from tqdm import tqdm
from utils import load_file, read_grid

import IPython as ipy

def to_array(grid: list[str]):
    h = len(grid)
    w = len(grid[0])
    arr = np.zeros((h,w))
    for i in range(h):
        for j in range(w):
            if grid[i][j] == "#":
                arr[i,j] = 1
            elif grid[i][j] == "O":
                arr[i,j] = 2
    return arr

def print_array(array: np.ndarray):
    s = ""
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            s += ".#O"[int(array[i,j])]
        s += "\n"
    return s


def tilt(array: np.ndarray, dir: str="N"):
    rolls = np.argwhere(array==2)
    h, w = array.shape
    new_array = array.copy()
    for (i,j) in rolls:
        new_array[i,j] = 0
    if dir == "N":
        for (i,j) in rolls:
            blocks = np.argwhere(new_array[:i,j]==1)
            if len(blocks) == 0:
                block_pos = -1
            else:
                block_pos = blocks.max()
            stack_count = len(np.argwhere(array[block_pos+1:i,j]==2))
            new_array[block_pos+stack_count+1, j] = 2
    elif dir == "S":
        for (i,j) in rolls:
            blocks = np.argwhere(new_array[i:,j]==1)
            if len(blocks) == 0:
                block_pos = h
            else:
                block_pos = i + blocks.min()
            stack_count = len(np.argwhere(array[i+1:block_pos,j]==2))
            new_array[block_pos-stack_count-1, j] = 2
    elif dir == "W":
        for (i,j) in rolls:
            blocks = np.argwhere(new_array[i,:j]==1)
            if len(blocks) == 0:
                block_pos = -1
            else:
                block_pos = blocks.max()
            stack_count = len(np.argwhere(array[i,block_pos+1:j]==2))
            new_array[i, block_pos+stack_count+1] = 2
    elif dir == "E":
        for (i,j) in rolls:
            blocks = np.argwhere(new_array[i,j:]==1)
            if len(blocks) == 0:
                block_pos = w
            else:
                block_pos = j + blocks.min()
            stack_count = len(np.argwhere(array[i,j+1:block_pos]==2))
            new_array[i, block_pos-stack_count-1] = 2
    else:
        raise ValueError("Tilting in other directions not implemented")
    return new_array


def get_load(array: np.ndarray):
    rolls = np.argwhere(array==2)
    h = array.shape[0]
    total_load = 0
    for (i,j) in rolls:
        total_load += h-i
    return total_load

if __name__=="__main__":
    filename = sys.argv[1]
    if "practice" in filename:
        text = open(filename).read()
    else:
        text = load_file(filename, year=2023, day=12)

    grid = read_grid(text)
    print("Part 1:")
    array = to_array(grid)
    tilted = tilt(array)
    print(print_array(tilted))
    load = get_load(tilted)
    print("Load:", load)

    print("\nPart 2:")
    board = array.copy()
    print("Initial state:")
    print(print_array(board))
    state_seqs = {}
    board_states = []
    board_loads = []
    for itr in tqdm(range(1000000000)):
        for dir in "NWSE":
            board = tilt(board, dir=dir)

        # cycle detection
        board_states += [print_array(board)]
        board_loads += [get_load(board)]
        state_seq = tuple(board_states[-50:])
        if state_seq in state_seqs:
            print("Converged??")
            prev_itr, load = state_seqs[state_seq]
            cycle_len = itr - prev_itr
            cycle_loads = board_loads[-cycle_len:]
            remaining_cycles_mod = (1000000000 - itr) % cycle_len
            print("Cycle loads:", cycle_loads)
            res = cycle_loads[remaining_cycles_mod-2]
            break
        else:
            state_seqs[state_seq] = (itr, get_load(board))

    print("Load:", res)


