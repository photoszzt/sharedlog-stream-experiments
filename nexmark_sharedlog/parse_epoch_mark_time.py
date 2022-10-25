import argparse
import os
import json
from pathlib import Path
from statistics import quantiles, mean, stdev
import numpy as np

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True)
    args = parser.parse_args()
    dirs_dict = {}
    for root, dirs, _ in os.walk(args.dir):
        for d in dirs:
            if "epoch" in d:
                tps_per_work = int(d.split("_")[0][:-3])
                dirs_dict[tps_per_work] = os.path.join(root, d, "logs")
    stats = {}
    flush_all = {}
    epochMarkTimes = {}
    for tps_per_work, dirpath in dirs_dict.items():
        stats[tps_per_work] = {}
        flush_all[tps_per_work] = {}
        epochMarkTimes[tps_per_work] = {}
        visited_files = set()
        for fname in Path(dirpath).glob("**/*.stderr"):
            basename = os.path.basename(fname)
            if basename in visited_files:
                continue
            visited_files.add(basename)
            stage = basename.split("_")[0]
            with open(fname, "r") as f:
                for line in f:
                    if "epoch mark time" in line:
                        l = line.strip().split(": ")[1]
                        nums = l.strip("[]{}").split(" ")
                        nums = [int(i) for i in nums]
                        if stage not in stats[tps_per_work]:
                            stats[tps_per_work][stage] = []
                        stats[tps_per_work][stage].append(nums)
                    elif "flushAllStream" in line and "[" in line:
                        l = line.strip().split(": ")[1]
                        nums = l.strip("[]{}").split(" ")
                        nums = [int(i) for i in nums]
                        if stage not in flush_all[tps_per_work]:
                            flush_all[tps_per_work][stage] = []
                        flush_all[tps_per_work][stage].append(nums)
                    elif "epoch_mark_times" in line:
                        l = int(line.strip().split(": ")[1])
                        if stage not in epochMarkTimes[tps_per_work]:
                            epochMarkTimes[tps_per_work][stage] = []
                        epochMarkTimes[tps_per_work][stage].append(l)
    print("progress marking")
    for tps_per_work, stat in stats.items():
        for stage, data in stat.items():
            data_arr = np.concatenate(data)
            print(f"{tps_per_work},{stage},{np.mean(data_arr)},{np.std(data_arr)},{np.min(data_arr)},{np.quantile(data_arr, 0.25)},{np.quantile(data_arr, 0.5)},{np.quantile(data_arr, 0.9)},{np.quantile(data_arr, 0.99)},{np.max(data_arr)}")
                         
    print("flush all")
    for tps_per_work, stat in flush_all.items():
        for stage, data in stat.items():
            data_arr = np.concatenate(data)
            print(f"{tps_per_work},{stage},{np.mean(data_arr)},{np.std(data_arr)},{np.min(data_arr)},{np.quantile(data_arr, 0.25)},{np.quantile(data_arr, 0.5)},{np.quantile(data_arr, 0.9)},{np.quantile(data_arr, 0.99)},{np.max(data_arr)}")

    print("progress marking times")
    for tps_per_work, stat in epochMarkTimes.items():
        for stage, data in stat.items():
            print(f"{tps_per_work},{stage},{mean(data)},{stdev(data)}")


if __name__ == '__main__':
    main()
