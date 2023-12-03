import IPython as ipy

W2N = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]

def isint(ch):
    return ch in "0123456789"

def isnum(ss):
    return ss in W2N

def get_cn_digits(line):
    d1, d2 = None, None
    for ch in line:
        if isint(ch):
            d1 = ch
            break
    for ch in line[::-1]:
        if isint(ch):
            d2 = ch
            break
    cn = int(d1+d2)
    return cn

def get_d1_spelled(line):
    for i in range(len(line)):
        if isint(line[i]):
            return line[i]
        else:
            for j in [3,4,5]:
                if isnum(line[i:i+j]):
                    return str(W2N.index(line[i:i+j])+1)
    return None

def get_d2_spelled(line):
    for i in range(len(line)-1, -1, -1):
        if isint(line[i]):
            return line[i]
        else:
            for j in [3,4,5]:
                if isnum(line[i-j:i]):
                    return str(W2N.index(line[i-j:i])+1)
    return None


def get_cn_spelled(line):
    d1 = get_d1_spelled(line)
    d2 = get_d2_spelled(line)
    try:
        return int(d1+d2)
    except:
        ipy.embed()
    

if __name__=="__main__":
    print("Part 1:")
    sum1 = sum([get_cn_digits(line) for line in open("inputs/1.txt")])
    print(sum1)
    print("Part 2:")
    sum2 = sum([get_cn_spelled(line) for line in open("inputs/1.txt")])
    print(sum2)
    print("Done.")