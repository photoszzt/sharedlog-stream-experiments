import argparse
import os
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
                if "consume" in fname and "stderr" in fname:
                    path = os.path.join(root, fname)
                    times = parse_file(path)
                    if len(times) > 0:
                        all_time.extend(times)
    p50 = quantiles(all_time, n=100)[49]
    p99 = quantiles(all_time, n=100)[98]
    print(f"p50: {p50} us, p99: {p99} us")


if __name__ == '__main__':
    main()
