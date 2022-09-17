import argparse
import os
from string import ascii_lowercase


class Data:
    auc_numEntry = 0
    auc_numElement = 0
    auc_elapsed = 0
    per_numEntry = 0
    per_numElement = 0
    per_elapsed = 0
    elapsed = 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True)
    parser.add_argument('--target', required=True)
    parser.add_argument('--num', required=True, type=int)
    parser.add_argument('--tps', required=True, type=int)
    args = parser.parse_args()

    for i in range(args.num):
        print(i)
        dpath = os.path.join(args.dir, str(i), f"{args.tps}tps_epoch", 'logs')
        stats = {}
        for root, dirs, files in os.walk(dpath):
            for fname in files:
                if args.target in fname and "stderr" in fname:
                    if fname not in stats:
                        stats[fname] = Data()
                        fpath = os.path.join(root, fname)
                        with open(fpath, "r") as f:
                            for line in f:
                                if "restore, count" in line:
                                    l = line.strip().split(",")
                                    print(l)
                                    if "person" in l[0] or "auction" in l[0]:
                                        numElement = l[1].strip().split(": ")[1]
                                        numEntry = l[2].strip().split(": ")[1]
                                        elapsedStr = l[3].strip().split(": ")[1]
                                        elapsed = float(elapsedStr.rstrip(ascii_lowercase))
                                        if "ms" not in elapsedStr:
                                            elapsed = elapsed * 1000 
                                        print(numElement, numEntry, elapsed)
                                        if "person" in l[0]:
                                            stats[fname].per_numElement = numElement
                                            stats[fname].per_numEntry = numEntry 
                                            stats[fname].per_elapsed = elapsed
                                        elif "auction" in l[0]:
                                            stats[fname].auc_numElement = numElement
                                            stats[fname].auc_numEntry = numEntry 
                                            stats[fname].auc_elapsed = elapsed
                                elif "restore, elapsed" in line:
                                    l = line.strip().split(",")
                                    elapsedStr = l[1].strip().split(": ")[1]
                                    elapsed = float(elapsedStr.rstrip(ascii_lowercase))
                                    if "ms" not in elapsedStr:
                                        elapsed = elapsed * 1000 
                                    print(l, elapsed)
                                    stats[fname].elapsed = elapsed
        for f, d in stats.items():
            print(f"{d.auc_numElement},{d.auc_numEntry},{d.auc_elapsed},{d.per_numElement},{d.per_numEntry},{d.per_elapsed},{d.elapsed}")


if __name__ == '__main__':
    main()
