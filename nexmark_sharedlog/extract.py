import os
from statistics import mean
from extract_logs import parse_logs
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True)
    parser.add_argument('--target', required=True)
    parser.add_argument('--tps', required=True, default="125,250,500")
    args = parser.parse_args()
    tps = args.tps.strip().split(",")
    modes = ["alo", "epoch"]
    top_dir = args.dir
    data_arr = {}
    for tp in tps:
        for mode in modes:
            log_dir = os.path.join(top_dir, f"{tp}tps_{mode}", "logs")
            print(log_dir)
            p50_arr, p90_arr, p99_arr = parse_logs(log_dir, args.target)
            p50 = round(mean(p50_arr), 1)
            p99 = round(mean(p99_arr), 1)
            p50_k = f"p50_{mode}"
            p99_k = f"p99_{mode}"
            if p50_k not in data_arr:
                data_arr[p50_k] = []
            if p99_k not in data_arr:
                data_arr[p99_k] = []
            data_arr[p50_k].append(p50)
            data_arr[p99_k].append(p99)
    for k, v in data_arr.items():
        print(f"{k} = {v}")


if __name__ == '__main__':
    main()
