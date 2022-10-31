import argparse
import os
import json
from pathlib import Path
from statistics import quantiles, mean, stdev
import numpy as np

def printStats(tp, statk, stats, all_stats):
    for stage in statk:
        for tps_per_work in tp:
            data = stats[tps_per_work][stage]
            data_arr = np.concatenate(data)
            if tps_per_work not in all_stats:
                all_stats[tps_per_work] = []
            all_stats[tps_per_work].append(data_arr)
            mean = np.mean(data_arr)
            std = np.std(data_arr)
            min_data = np.min(data_arr)
            p25 = np.quantile(data_arr, 0.25)
            p50 = np.quantile(data_arr, 0.5)
            p90 = np.quantile(data_arr, 0.9)
            p99 = np.quantile(data_arr, 0.99)
            max_data = np.max(data_arr)
            print(f"{tps_per_work},{stage},{mean},{std},{min_data},{p25},{p50},{p90},{p99},{max_data}")

    print()
    for tps in tp:
        data = all_stats[tps]
        data_arr = np.concatenate(data)
        p50 = np.quantile(data_arr, 0.5)
        p99 = np.quantile(data_arr, 0.99)
        print(f"{tps},{p50},{p99}")

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
    flush_at_least_one = {}
    epochMarkTimes = {}
    for tps_per_work, dirpath in dirs_dict.items():
        stats[tps_per_work] = {}
        flush_all[tps_per_work] = {}
        epochMarkTimes[tps_per_work] = {}
        flush_at_least_one[tps_per_work] = {}
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
                    elif "flushStage" in line and "[" in line:
                        l = line.strip().split(": ")[1]
                        nums = l.strip("[]{}").split(" ")
                        nums = [int(i) for i in nums]
                        if stage not in flush_all[tps_per_work]:
                            flush_all[tps_per_work][stage] = []
                        flush_all[tps_per_work][stage].append(nums)
                    elif "flushAtLeastOne" in line and "[" in line:
                        l = line.strip().split(": ")[1]
                        nums = l.strip("[]{}").split(" ")
                        nums = [int(i) for i in nums]
                        if stage not in flush_at_least_one[tps_per_work]:
                            flush_at_least_one[tps_per_work][stage] = []
                        flush_at_least_one[tps_per_work][stage].append(nums)
                    elif "epoch_mark_times" in line:
                        l = int(line.strip().split(": ")[1])
                        if stage not in epochMarkTimes[tps_per_work]:
                            epochMarkTimes[tps_per_work][stage] = []
                        epochMarkTimes[tps_per_work][stage].append(l)

    tp = sorted(stats.keys())
    stat = stats[tps_per_work]
    statk = sorted(stat.keys())
    all_mark_stats = {}
    print("progress marking(us)")
    printStats(tp, statk, stats, all_mark_stats)
                         
    print("flush all(us)")
    all_flush_stats = {}
    printStats(tp, statk, flush_all, all_flush_stats)

    print("flush at least one(us)")
    all_flush_at_least_one_stats = {}
    printStats(tp, statk, flush_at_least_one, all_flush_at_least_one_stats)

    print("progress marking times")
    tp = sorted(epochMarkTimes.keys())
    for tps_per_work in tp:
        stat = epochMarkTimes[tps_per_work]
        for stage, data in stat.items():
            print(f"{tps_per_work},{stage},{mean(data)},{stdev(data)}")


if __name__ == '__main__':
    main()
