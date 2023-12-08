import sys
from collections import Counter

import IPython as ipy

RRANKS = "AKQJT98765432"
RANKS = RRANKS[::-1]

JRANKS = "J23456789TQKA"

""" 
comparator implementation, cruelly deprecated :(((((
"""

def compare_cards(c1: str, c2: str):
    return -(RRANKS.find(c1) - RRANKS.find(c2))

def compare_val_ranks(hand1, hand2):
    for c1, c2 in zip(hand1, hand2):
        cc = compare_cards(c1,c2)
        if cc == 0:
            continue
        return cc
    print("Equal hands? probably shouldn't happen")
    return 0

def compare_hands(hand1: str, hand2: str):
    """Comparison function for hand ranks for sorting.

    Args:
        hand1 (str): The first hand
        hand2 (str): The second hand

    Returns:
        int: A number for sorting:
        - a positive number if if hand1 is greater in rank to hand2
        - 0 if they are equal
        - a negative number if hand2 is of greater rank
    """
    lbs1, lbs2 = Counter(hand1), Counter(hand2)
    mv1, mv2 = max(lbs1.values()), max(lbs2.values())
    if len(lbs1) != len(lbs2):
        return len(lbs2) - len(lbs1)
    elif len(lbs1) in [2,3]:
        # four of a kind or full house
        if mv1 != mv2:
            return mv1 > mv2
        # same type, so compare by card ranks
    return compare_val_ranks(hand1, hand2)

def compare_hbs(hb1, hb2):
    return compare_hands(hb1[0], hb2[0])


"""
key-based implementation
"""

TYPES = [(1,5), (2,4), (2,3), (3,3), (3,2), (4,2), (5,1)]

def get_best_joker_card(ccs: dict):
    # get non-joker max count
    njmc = max([c for card,c in ccs.items() if card != "J"])
    # get highest card of that count
    max_count_cards = [card for card in ccs if ccs[card] == njmc and card != "J"]
    best_card = max(max_count_cards, key=JRANKS.index)
    return best_card


def get_type(hand: str, joker=False):
    ccs = Counter(hand)
    if joker and "J" in hand:
        if len(ccs) == 1:
            # all jokers
            hand == "AAAAA"
        else:
            best_nj_card = get_best_joker_card(ccs)
            hand = hand.replace("J", best_nj_card)
    ccs = Counter(hand)
    mc = max(ccs.values())
    return TYPES.index((mc,len(ccs)))


def get_val_rank(hand: str, joker=False):
    if joker:
        ranks = JRANKS
    else:
        ranks = RANKS
    r = 0
    for idx,card in enumerate(hand[::-1]):
        r += (14**idx)*(ranks.find(card))
    return r


def get_rank(hand: str, joker=False):
    t = get_type(hand, joker)
    return t*496452 + get_val_rank(hand, joker)


if __name__=="__main__":
    input = open(sys.argv[1]).readlines()
    hbs = [tuple(l.split()) for l in input]
    print("Part 1:")
    hbs_sorted = sorted(hbs, key=lambda hb: get_rank(hb[0]))
    tot = 0
    for idx, hb in enumerate(hbs_sorted, start=1):
        tot += idx*int(hb[1])
    print("Total winnings:", tot)
    print("Part 2:")
    hbs_sorted = sorted(hbs, key=lambda hb: get_rank(hb[0], joker=True))
    tot = 0
    for idx, hb in enumerate(hbs_sorted, start=1):
        tot += idx*int(hb[1])
    print("Total winnings:", tot)
        