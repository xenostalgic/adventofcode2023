import sys
from utils import prod
import numpy as np

def read_input(lines):
    times = list(map(int,lines[0].strip().split()[1:]))
    dists = list(map(int,lines[1].strip().split()[1:]))
    return list(zip(times, dists))


def read_input_kerning(lines):
    time = int(lines[0].split(":")[1].replace(" ", ""))
    dist = int(lines[1].split(":")[1].replace(" ", ""))
    return (time, dist)


def get_ways(time, record):
    n = 0

    for i in range(time):
        d = (time-i)*i
        if d > record:
            n += 1

    return n


if __name__=="__main__":
    input = open(sys.argv[1]).readlines()
    print("Day 1:")
    td_pairs = read_input(input)
    ways = [get_ways(t,d) for (t,d) in td_pairs]
    print("Product of ways to win races:", prod(ways))
    print("Day 2:")
    t, d = read_input_kerning(input)
    res = get_ways(t,d)
    print("Ways to win the single race:", res)