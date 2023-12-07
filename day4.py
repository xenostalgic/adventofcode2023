
from tqdm import tqdm

import IPython as ipy

def parse_card(line):
    card_name, nums = line.split(":")
    idx = int(card_name.split()[1])
    w_nums, h_nums = nums.strip().split(" | ")
    matches = [n for n in h_nums.split() if n in w_nums.split()]
    return idx, matches

if __name__=="__main__":
    input = [line for line in open("inputs/day4.txt")]
    print("Part 1:")
    points = 0
    for line in input:
        _, matches = parse_card(line)
        if len(matches) > 0:
            points += 2**(len(matches)-1)
    print("Points:", points)
    card_matches = {}
    for card in input:
        idx, matches = parse_card(card)
        card_matches[idx] = matches
    card_counts = {idx:1 for idx in card_matches}
    for card_idx in tqdm(sorted(card_matches.keys())):
        nm = len(card_matches[card_idx])
        for cci in range(card_idx, card_idx+nm):
            card_counts[cci+1] += card_counts[card_idx]
    print("Total cards:", sum(card_counts.values()))
