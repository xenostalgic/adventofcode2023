import sys
import IPython as ipy
from tqdm import tqdm

from utils import lcm, prod, lcm_n

def read_input(text):
    lines = text.splitlines()
    rlis = lines[0].strip()
    nodes = {}
    for line in lines[2:]:
        src, _, r, l = line.strip().split()
        opts = r.strip("(,"), l.strip(")")
        nodes[src] = opts
    return rlis, nodes


def follow(rlis, nodes, start="AAA", end="ZZZ"):
    cur = start
    i = 0
    while not cur.endswith(end):
        d = rlis[i%len(rlis)]
        next = nodes[cur][1] if d == "R" else nodes[cur][0]
        cur = next
        i += 1
    return i


def follow_parallel(rlis, nodes, end="Z"):
    cur_set = [n for n in nodes if n.endswith("A")]
    i = 0
    while True:
        d = rlis[i%len(rlis)]
        next_set = []
        for n in cur_set:
            opts = nodes[n]
            next = opts[1] if d == "R" else opts[0]
            next_set.append(next)
        cur_set = next_set
        i += 1
        if all([n.endswith(end) for n in cur_set]):
            break
    return i


def get_arriv_cycle_remainder(rlis, nodes, start="AAA", end="Z", all_remainders=False):
    path = [(start,0)]
    seen = set(path)
    arriv_len, cycle_len, stop_idxs = None, None, []
    i = 0
    cur = start
    while True:
        opts = nodes[cur]
        mi = i % len(rlis)
        next = opts[1] if rlis[mi] == "R" else opts[0]
        mi1 = (i+1) % len(rlis)
        if (next, mi1) in seen:
            arriv_len = path.index((next,mi1))
            cycle_len = len(path) - arriv_len
            if all_remainders:
                remainders = [(si - arriv_len) for si in stop_idxs]
                return cycle_len, arriv_len, remainders
            else:
                remainder = stop_idxs[-1] - arriv_len
                return cycle_len, arriv_len, remainder
        if next.endswith(end):
            stop_idxs.append(i+1)
        path.append((next, mi1))
        seen.add((next, mi1))
        cur = next
        i += 1


def follow_cyclemod(rlis, nodes):
    start_set = [n for n in nodes if n.endswith("A")]
    cycle_lens = [get_arriv_cycle_remainder(rlis, nodes, start=n, end="Z")[0] for n in start_set]
    lcm = lcm_n(cycle_lens)
    return int(lcm)


def follow_cyclemod_lollipop(rlis, nodes):
    start_set = [n for n in nodes if n.endswith("A")]
    acr_lens = [get_arriv_cycle_remainder(rlis, nodes, start=n, end="Z") for n in start_set]
    print(acr_lens)
    cycle_lens, arriv_lens, remainders = zip(*acr_lens)
    max_arriv_len = max(arriv_lens)
    rems = [(r+max_arriv_len-al)%cl for r,cl,al in zip(remainders, cycle_lens, arriv_lens)]

    # now we have a system of equations ("congruences"):
    # x % cl = m for m, cl in zip(rems,cycle_lens)
    # where x is the steps from the last pointer to arrive into a cycle
    # chinese remainder theorem can find a solution
    # but we can also do it sort of iteratively...
    x, cur_m = rems[0], cycle_lens[0]
    for ci in tqdm(range(1, len(start_set))):
        # combine each congruence with the combination-so-far
        r2 = rems[ci]
        m2 = cycle_lens[ci]
        # by construction, x % c_{0...i-1} = r_{0...i-1} always
        while x % m2 != r2:
            x = x + cur_m
            if x > 10371555451871:
                ipy.embed()
        cur_m = lcm(cur_m, m2)


    return x + max_arriv_len


def follow_cyclemod_figure8(rlis, nodes):
    start_set = [n for n in nodes if n.endswith("A")]
    acr_lens = [get_arriv_cycle_remainder(rlis, nodes, start=n, end="Z", all_remainders=True) for n in start_set]
    print(acr_lens)
    cycle_lens, arriv_lens, remainder_sets = zip(*acr_lens)
    max_arriv_len = max(arriv_lens)
    rem_sets = [[(r+max_arriv_len-al)%cl for r in rset] for rset,cl,al in zip(remainder_sets, cycle_lens, arriv_lens)]

    # now we have a system of equations ("congruences"):
    # x % cl = m for m, cl in zip(rems,cycle_lens)
    # where x is the steps from the last pointer to arrive into a cycle
    # chinese remainder theorem can find a solution
    # but we can also do it sort of iteratively...
    xset, mset = rem_sets[0], [cycle_lens[0] for r in rem_sets[0]]
    for ci in range(1, len(start_set)):
        # combine each congruence with each possible combination-so-far
        # this does get exponential but hopefully the numbers are small?
        r2_set = rem_sets[ci]
        m2 = cycle_lens[ci]
        next_xset, next_mset = [], []
        for r2 in r2_set:
            for x,m in zip(xset,mset):
                # by construction, x % m_{0...i-1} = r_{0...i-1} for each corresponding x and cur_m
                # so we just need to check if it satisfies x % m2 == r2 also
                cvs = set()
                fail = False
                while x % m2 != r2:
                    x = x + m
                    if x % m2 in cvs:
                        fail = True
                        break
                    else:
                        cvs.add(x%m2)
                if not fail:
                    next_xset.append(x)
                    next_mset.append(lcm(m, m2))
        xset = next_xset
        mset = next_mset

    x = min(xset)

    print("lcm:", mset[xset.index(x)])
    print("rem:", x)
    print("max arrival time", max_arriv_len)
    ipy.embed()

    return int(x + max_arriv_len)


if __name__=="__main__":
    rlis, nodes = read_input(open(sys.argv[1]).read())
    print("Part 1:")
    n_steps = follow(rlis, nodes, start="AAA", end="ZZZ")
    print("# steps:", n_steps)

    # print("Part 2 (reference):")
    # n_steps2 = follow_parallel(rlis, nodes)
    # print(n_steps2, "\n")

    print("\nPart 2 (basic):")
    n_steps2 = follow_cyclemod(rlis, nodes)
    print(n_steps2, "\n")

    print("\nPart 2 (handles 'lollipops'):")
    n_steps2 = follow_cyclemod_lollipop(rlis, nodes)
    print(n_steps2, "\n")

    # print("\nPart 2 (handles 'lollipops' and multiple end-nodes per cycle):")
    # n_steps2 = follow_cyclemod_figure8(rlis, nodes)
    # print(n_steps2, "\n")

