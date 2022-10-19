import argparse
import os
import json
from statistics import quantiles
import re


def parse_file(fpath: str):
    with open(fpath, "r") as f:
        for line in f:
            if "[" in line:
                l = line.strip()
                s = l.split(": ")
                arr = s[1].split(", ")
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
            if "consume" in fname and "stdout" in fname:
                path = os.path.join(root, fname)
                times = parse_file(path)
                p50 = quantiles(times, n=100)[49]
                p99 = quantiles(times, n=100)[98]
                p50_ms = p50 / 1000000.0
                p99_ms = p99 / 1000000.0
                print(f"{path} p50: {p50} ns {p50_ms}ms, p99: {p99} ns {p99_ms} ms")


if __name__ == '__main__':
    main()
