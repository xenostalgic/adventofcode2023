import sys

def predict_seq_recursive(seq: list[int]) -> int:
    if len(set(seq)) == 1:
        # all the same, so next will be too
        return seq[0]
    diffs  = [seq[i+1]-seq[i] for i in range(len(seq)-1)]
    dnext = predict_seq_recursive(diffs)
    return seq[-1] + dnext


def predict_seq_recursive_rev(seq: list[int]) -> int:
    if len(set(seq)) == 1:
        # all the same, so prev will be too
        return seq[0]
    diffs  = [seq[i+1]-seq[i] for i in range(len(seq)-1)]
    dprev = predict_seq_recursive_rev(diffs)
    return seq[0] - dprev


if __name__=="__main__":
    input = open(sys.argv[1]).read()
    seqs = [list(map(int,line.strip().split())) for line in input.splitlines()]
    print("Part 1:")
    conts = [predict_seq_recursive(seq) for seq in seqs]
    print("Continuations:", conts)
    print("Sum of continuations:", sum(conts))
    print("\nPart 2:")
    prevs = [predict_seq_recursive_rev(seq) for seq in seqs]
    print("Previous:", prevs)
    print("Sum of previous:", sum(prevs))
