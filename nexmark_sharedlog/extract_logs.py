import argparse
import os
from statistics import mean, median
from dataclasses import dataclass
from typing import List
# from matplotlib import pyplot as plt


@dataclass
class Stat:
    p50: List[int]
    p90: List[int]
    p99: List[int]
    duration: List[str]


def parse_logs(logs_dir: str, target: str):
    dpaths = []
    for root, dirs, files in os.walk(logs_dir):
        for dname in dirs:
            dpath = os.path.join(root, dname)
            dpaths.append(dpath)
    stats = {}
    for dpath in dpaths:
        for root, dirs, files in os.walk(dpath):
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
            cnt += 1
    p50_arr = []
    p90_arr = []
    p99_arr = []
    for name in names:
        p50arr = stats[name].p50
        p90arr = stats[name].p90
        p99arr = stats[name].p99
        if p50arr:
            if len(p50arr) > 1:
                p50_arr += p50arr[1:] 
                p90_arr += p90arr[1:] 
                p99_arr += p99arr[1:] 
            else:
                p50_arr += p50arr 
                p90_arr += p90arr 
                p99_arr += p99arr 
    return p50_arr, p90_arr, p99_arr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True)
    parser.add_argument('--target', required=True)
    args = parser.parse_args()
    p50_arr, p90_arr, p99_arr = parse_logs(args.dir, args.target)
    # print(f"overall avg,p50\tp90\tp99")
    print(f"{round(mean(p50_arr), 1)}, {round(mean(p90_arr), 1)}, {round(mean(p99_arr), 1)}")


            
if __name__ == '__main__':
    main()
