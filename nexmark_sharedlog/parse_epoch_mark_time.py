import argparse
import os
import json
from statistics import quantiles, mean

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True)
    args = parser.parse_args()
    stats = {}
    for root, dirs, files in os.walk(args.dir):
        for fname in files:
            if "stderr" in fname:
                fpath = os.path.join(root, fname)
                if fname not in stats:
                    with open(fpath, "r") as f:
                        for line in f:
                            if "epoch mark time" in line:
                                l = line.strip().split(": ")[1]
                                nums = l.strip("[]{}").split(" ")
                                nums = [int(i) for i in nums]
                                q = quantiles(nums, n=100)
                                print(f"{fname}: p50: {q[49]}, p99: {q[98]}")
                                stats[fname] = nums
    all_epoch_mark = []
    for f, nums in stats.items():
        all_epoch_mark.extend(nums)
    print(f"mean: {mean(all_epoch_mark)}, max: {max(all_epoch_mark)}")


if __name__ == '__main__':
    main()
