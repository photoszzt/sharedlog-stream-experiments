import argparse
import os
from string import ascii_lowercase
from pathlib import Path


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
    args = parser.parse_args()

    dirs_dict = {}
    for root, dirs, _ in os.walk(args.dir):
        for d in dirs:
            if "epoch" in d:
                tps_per_work = int(d.split("_")[0][:-3])
                if tps_per_work not in dirs_dict:
                    dirs_dict[tps_per_work] = []
                dirs_dict[tps_per_work].append(os.path.join(root, d, "logs"))
    print(dirs_dict)
    all_tps = dirs_dict.keys()
    all_tps = sorted(all_tps)

    for tps_per_work in all_tps:
        dirpaths = dirs_dict[tps_per_work]
        for dpath in dirpaths:
            stats = {}
            for fpath in Path(dpath).glob("**/*.stderr"):
                fname = os.path.basename(fpath)
                if args.target in str(fname):
                    if fname not in stats:
                        stats[fname] = Data()
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
                print(f"{d.auc_numElement},{d.auc_numEntry},{d.auc_elapsed},"
                      f"{d.per_numElement},{d.per_numEntry},{d.per_elapsed},{d.elapsed}")


if __name__ == '__main__':
    main()
