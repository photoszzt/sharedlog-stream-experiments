import argparse
import os
from statistics import mean


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True)
    parser.add_argument('--metric', required=True)
    args = parser.parse_args()
    stats = {}
    for root, dirs, files in os.walk(args.dir):
        for fname in files:
            if "kstreams-test_nexmark" in fname and "stdout" in fname and fname not in stats:
                fpath = os.path.join(root, fname)
                stats[fname] = []
                with open(fpath, "r") as f:
                    for line in f:
                        if args.metric in line:
                            l = line.strip().split(";")
                            latStr = l[2].split(":")[1]
                            if "NaN" not in latStr:
                                stats[fname].append(float(latStr))
    all_commit_lat = []
    for f, n in stats.items():
        all_commit_lat.extend(n)
    print(f"mean: {mean(all_commit_lat)}")



if __name__ == '__main__':
    main()
