import argparse
import os
import json
from pathlib import Path
from statistics import quantiles, mean, stdev
import numpy as np

def printStats(tp, statk, stats, all_stats):
    print("tps/work, stage, mean, std, min, p25, p50, p90, p99, max")
    for stage in statk:
        for tps_per_work in tp:
            if stage not in stats[tps_per_work]: 
                continue
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

    summary_stats = []
    print()
    for tps in tp:
        if tps in all_stats:
            data = all_stats[tps]
            data_arr = np.concatenate(data)
            p50 = np.quantile(data_arr, 0.5)
            p99 = np.quantile(data_arr, 0.99)
            print(f"{tps},{p50},{p99}")
            summary_stats.append((tps, p50, p99))
    sorted(summary_stats, key=lambda kv: kv[0])
    return summary_stats

def get_nums(line):
    l = line.strip().split(": ")[1]
    if '=' in l:
        l = l.split('=')[1]
    nums = l.strip("[]{}").split(" ")
    nums = [int(i) for i in nums]
    return nums


def update_dict(dic, tps_per_work, stage, item):
    if stage not in dic[tps_per_work]:
        dic[tps_per_work][stage] = []
    dic[tps_per_work][stage].append(item)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True)
    parser.add_argument('--mode', required=True, help='2pc, epoch, align_chkpt')
    args = parser.parse_args()
    dirs_dict = {}
    for root, dirs, _ in os.walk(args.dir):
        for d in dirs:
            if args.mode in d or "Kb" in d:
                try:
                    if args.mode in d:
                        tps_per_work = int(d.split("_")[0][:-3])
                    else:
                        tps_per_work = d
                    if tps_per_work not in dirs_dict:
                        dirs_dict[tps_per_work] = []
                    dirs_dict[tps_per_work].append(os.path.join(root, d, "logs"))
                except Exception:
                    pass
    print(dirs_dict)
    stats = {}
    flush_all = {}
    flush_at_least_one = {}
    epochMarkTimes = {}
    for tps_per_work, dirpaths in dirs_dict.items():
        if tps_per_work not in stats:
            stats[tps_per_work] = {}
        if tps_per_work not in flush_all:
            flush_all[tps_per_work] = {}
        if tps_per_work not in epochMarkTimes:
            epochMarkTimes[tps_per_work] = {}
        if tps_per_work not in flush_at_least_one:
            flush_at_least_one[tps_per_work] = {}
        visited_files = set()
        for dirpath in dirpaths:
            for fname in Path(dirpath).glob("**/*.stderr"):
                basename = os.path.basename(fname)
                if basename in visited_files:
                    continue
                visited_files.add(basename)
                stage = basename.split("_")[0]
                with open(fname, "r") as f:
                    for line in f:
                        if "epoch mark time" in line or (("flushStage" in line or "flushAtLeastOne" in line) and "[" in line):
                            nums = get_nums(line)
                            if "epoch mark time" in line:
                                update_dict(stats, tps_per_work, stage, nums)
                            elif "flushStage" in line and "[" in line:
                                update_dict(flush_all, tps_per_work, stage, nums)
                            elif "flushAtLeastOne" in line and "[" in line:
                                update_dict(flush_at_least_one, tps_per_work, stage, nums)
                        elif "epoch_mark_times" in line:
                            l = int(line.strip().split(": ")[1])
                            update_dict(epochMarkTimes, tps_per_work, stage, l)
    tp = sorted(stats.keys())
    statk = sorted(stats[tp[0]].keys())
    all_mark_stats = {}
    print("progress marking(us)")
    summary = printStats(tp, statk, stats, all_mark_stats)
    # os.makedirs(args.out_dir, exist_ok=True)
    # p = os.path.join(args.out_dir, "mark_time.json")
    # with open(p, "w") as f:
    #     json.dump(summary, f)
                         
    print("flush all(us)")
    tp = sorted(flush_all.keys())
    fa_keys = None
    i = 0
    while i < len(tp):
        fa_keys = flush_all[tp[i]].keys()
        if len(fa_keys) != 0:
            break
        i = i + 1
    fak = sorted(fa_keys)
    print(tp, fak)
    all_flush_stats = {}
    printStats(tp, fak, flush_all, all_flush_stats)

    # print("flush at least one(us)")
    # all_flush_at_least_one_stats = {}
    # printStats(tp, statk, flush_at_least_one, all_flush_at_least_one_stats)

    # print("progress marking times")
    # tp = sorted(epochMarkTimes.keys())
    # for tps_per_work in tp:
    #     stat = epochMarkTimes[tps_per_work]
    #     for stage, data in stat.items():
    #         print(f"{tps_per_work},{stage},{mean(data)},{stdev(data)}")


if __name__ == '__main__':
    main()
