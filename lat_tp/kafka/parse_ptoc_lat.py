import argparse
import os
import json
from statistics import quantiles


def parse_file(fpath: str):
    with open(fpath, "r") as f:
        for line in f:
            if "[" in line:
                arr = line.strip().split(" ")
                arr[0] = arr[0][1:]
                arr[-1] = arr[-1][:-1]
                times = [ int(i) for i in arr]
                return times


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, required=True)
    args = parser.parse_args()
    for root, dirs, files in os.walk(args.dir):
        for fname in files:
            if "consume" in fname and "stderr" in fname:
                path = os.path.join(root, fname)
                times = parse_file(path)
                p50 = quantiles(times, n=100)[49]
                p99 = quantiles(times, n=100)[98]
                print(f"{fpath} p50: {p50} us, p99: {p99} us")


if __name__ == '__main__':
    main()
