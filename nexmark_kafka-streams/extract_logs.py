import argparse
import os
from statistics import mean
from dataclasses import dataclass
from typing import List

@dataclass
class Stat:
    p50: List[int]
    p90: List[int]
    p99: List[int]
    duration: List[str]


def parse_logs(log_dir: str, target: str):
    stats = {}
    for root, dirs, files in os.walk(log_dir):
        for fname in files:
            fpath = os.path.join(root, fname)
            stats[fname] = Stat(p50 = [], p90 = [], p99=[], duration=[])
            with open(fpath, 'r') as f:
                for line in f:
                    if target in line and 'p50' in line:
                        sp = line.strip().split(",")
                        dur_str = sp[0].strip().split(":")[1].strip()
                        time = dur_str.split("=")[1]
                        p50 = sp[1].strip().split("=")[1]
                        p90 = sp[2].strip().split("=")[1]
                        p99 = sp[3].strip().split("=")[1]
                        stats[fname].p50.append(int(p50))
                        stats[fname].p90.append(int(p90))
                        stats[fname].p99.append(int(p99))
                        stats[fname].duration.append(time)
    names = stats.keys()
    cnt = 1
    for name in names:
        p50arr = stats[name].p50
        p90arr = stats[name].p90
        p99arr = stats[name].p99
        if p50arr:
            # print(f"{args.exppref}_{cnt}_p50={p50arr}; {args.exppref}_{cnt}_p90={p90arr}; {args.exppref}_{cnt}_p99={p99arr}")
            cnt += 1
    # p50_str = f"{args.exppref}_p50 = "
    # p90_str = f"{args.exppref}_p90 = "
    # p99_str = f"{args.exppref}_p99 = "
    # cnt = cnt - 1
    # for i in range(cnt):
    #     if i != cnt - 1:
    #         p50_str += f"{args.exppref}_{i+1}_p50[1:] + "
    #         p90_str += f"{args.exppref}_{i+1}_p90[1:] + "
    #         p99_str += f"{args.exppref}_{i+1}_p99[1:] + "
    #     else:
    #         p50_str += f"{args.exppref}_{i+1}_p50[1:]"
    #         p90_str += f"{args.exppref}_{i+1}_p90[1:]"
    #         p99_str += f"{args.exppref}_{i+1}_p99[1:]"
    # print(p50_str)
    # print(p90_str)
    # print(p99_str)
    # print(f"{args.exppref}_p50_avg = round(mean({args.exppref}_p50), 1)")
    # print(f"{args.exppref}_p90_avg = round(mean({args.exppref}_p90), 1)")
    # print(f"{args.exppref}_p99_avg = round(mean({args.exppref}_p99), 1)")
    p50_arr = []
    p90_arr = []
    p99_arr = []
    for name in names:
        p50arr = stats[name].p50
        p90arr = stats[name].p90
        p99arr = stats[name].p99
        if p50arr:
            if len(p50_arr) > 1:
                p50_arr += p50arr[1:] 
                p90_arr += p90arr[1:] 
                p99_arr += p99arr[1:] 
            else:
                p50_arr += p50arr 
                p90_arr += p90arr 
                p99_arr += p99arr 
            # print(f"p50 avg: {round(mean(p50arr), 1)}, p90 avg: {round(mean(p90arr), 1)}, p99avg: {round(mean(p99arr), 1)}")
    # print(f"overall avg,p50\tp90\tp99")
    return p50_arr, p90_arr, p99_arr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True)
    parser.add_argument('--target', required=True)
    # parser.add_argument('--exppref', required=True)
    args = parser.parse_args()
    p50_arr, p90_arr, p99_arr = parse_logs(args.dir, args.target)
    print(f"{round(mean(p50_arr), 1)}, {round(mean(p90_arr), 1)}, {round(mean(p99_arr), 1)}")


if __name__ == '__main__':
    main()
