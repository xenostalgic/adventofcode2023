import IPython as ipy

COLORS = ["red", "green", "blue"]

def prod(nums):
    def mult(n1, n2):
        return n1*n2
    return map(mult, nums, 1)

def parse_game(line):
    gameid, record = line.split(": ", 1)
    gameidx = int(gameid[5:])
    records = [r.strip() for r in record.split(";")]
    record_maps = [{c.split()[1]: int(c.split()[0]) for c in r.split(", ")} for r in records]
    return gameidx, record_maps

def max_counts(record_maps):
    max_color_counts = {color: 0 for color in COLORS}
    for map in record_maps:
        for color in map:
            max_color_counts[color] = max(map[color], max_color_counts[color])
    return max_color_counts


def set_power(ccs):
    base = 1
    for color in COLORS:
        base = base*ccs[color]
    return base


def possible_index(limits, game):
    gameidx, record_maps = parse_game(game)
    game_max_counts = max_counts(record_maps)
    for color in limits:
        if game_max_counts[color] > limits[color]:
            return 0
    return gameidx


if __name__=="__main__":
    games = [line for line in open("inputs/2.txt")]
    limits = {"red": 12, "green": 13, "blue": 14}
    print("Part 1:")
    possible_indices = [possible_index(limits, game) for game in games]
    print(sum(possible_indices))
    print("Part 2:")
    powers = [set_power(max_counts(parse_game(game)[1])) for game in games]
    print(sum(powers))

