import argparse
import os
import numpy as np
from statistics import quantiles
from parse_ptoc_lat import parse_file

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    args = parser.parse_args()
    all_time = []
    for i in range(args.num):
        dirpath = os.path.join(args.dir, str(i))
        for root, dirs, files in os.walk(args.dir):
            for fname in files:
                if "consume" in fname and "stdout" in fname:
                    path = os.path.join(root, fname)
                    times = parse_file(path)
                    if len(times) > 0:
                        all_time.append(times)
    all_time = np.concatenate(all_time)
    p50 = np.quantile(all_time, 0.5)
    p99 = np.quantile(all_time, 0.99)
    p50_ms = p50 / 1000000.0
    p99_ms = p99 / 1000000.0
    print(f"p50: {p50} ns {p50_ms} ms, p99: {p99} ns {p99_ms} ms")


if __name__ == '__main__':
    main()
