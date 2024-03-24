import argparse
import os
import json
import pickle
import numpy as np
from pathlib import Path
from statistics import quantiles, mean, stdev
from parse_epoch_mark_time import get_nums, update_dict, get_dirs_dict, get_sorted_keys


def get_stats(stats):
    tp, statk = get_sorted_keys(stats)
    staged_stats = {}
    all_data = {}
    for stage in statk:
        for k in tp:
            if k not in staged_stats:
                staged_stats[k] = {}
            if k not in all_data:
                all_data[k] = []
            if stage not in staged_stats[k]:
                staged_stats[k][stage] = {}
            if "all" not in staged_stats[k]:
                staged_stats[k]["all"] = {}
            if stage not in stats[k]:
                continue
            data = stats[k][stage]
            data_arr = np.concatenate(data)
            p50 = np.quantile(data_arr, 0.5)
            p99 = np.quantile(data_arr, 0.99)
            staged_stats[k][stage] = {"p50": p50, "p99": p99}
            print(f"{k},{stage},{p50},{p99}")
            all_data[k].append(data_arr)
    for k in tp:
        if k in all_data:
            d = np.concatenate(all_data[k])
            p50 = np.quantile(d, 0.5)
            p99 = np.quantile(d, 0.99)
            staged_stats[k]["all"] = {"p50": p50, "p99": p99}
            print(f"{k},{p50},{p99}")
    return staged_stats


def init_dict(d, k):
    if k not in d:
        d[k] = {}


def parse_stats_single_exp(directory, mode, app, out_dir):
    dirs_dict = get_dirs_dict(directory, mode, app)
    for k, dirpaths in dirs_dict.items():
        visited_files = set()
        for dirpath in dirpaths:
            progress_mark = {}
            flush_all = {}
            flush_at_least_one = {}
            txnCommitTime = {}
            waitPrevTxnInCmt = {}
            waitPrevTxnInPush = {}
            waitPrevTxn2pc = {}
            txnSndPhase = {}
            init_dict(progress_mark, k)
            init_dict(flush_all, k)
            init_dict(flush_at_least_one, k)
            init_dict(txnCommitTime, k)
            init_dict(waitPrevTxnInCmt, k)
            init_dict(waitPrevTxnInPush, k)
            init_dict(waitPrevTxn2pc, k)
            init_dict(txnSndPhase, k)
                
            for fname in Path(dirpath).glob("**/*.stderr"):
                basename = os.path.basename(fname)
                if basename in visited_files:
                    continue
                visited_files.add(basename)
                stage = basename.split("_")[0]
                with open(fname, "r") as f:
                    for line in f:
                        if mode == "epoch" and "epochMarkTime" in line:
                            nums = get_nums(line)
                            update_dict(progress_mark, k, stage, nums)
                        elif "flushStage" in line and "[" in line:
                            nums = get_nums(line)
                            update_dict(flush_all, k, stage, nums)
                        elif "flushAtLeastOne" in line and "[" in line:
                            nums = get_nums(line)
                            update_dict(flush_at_least_one, k, stage, nums)
                        elif mode == "2pc" and "txnCommitTime" in line and "[" in line:
                            nums = get_nums(line)
                            update_dict(txnCommitTime, k, stage, nums)
                        elif mode == "2pc" and "waitPrevTxnInCmt" in line:
                            nums = get_nums(line)
                            update_dict(waitPrevTxnInCmt, k, stage, nums)
                        elif mode == "2pc" and "waitPrevTxnInPush" in line:
                            nums = get_nums(line)
                            update_dict(waitPrevTxnInPush, k, stage, nums)
                        elif mode == "2pc" and "waitPrevTxn2pc " in line and "[" in line:
                            nums = get_nums(line)
                            update_dict(waitPrevTxn2pc, k, stage, nums)
                        elif mode == "2pc" and "txnSndPhase" in line:
                            nums = get_nums(line)
                            update_dict(txnSndPhase, k, stage, nums)
            workload = os.path.dirname(dirpath)
            workload_name = os.path.basename(workload)
            exp = os.path.basename(os.path.dirname(workload))
            out_dir_path = os.path.join(out_dir, exp)
            os.makedirs(out_dir_path, exist_ok=True)
            st_path = os.path.join(out_dir_path, f"{workload_name}_stats.pickle")
            all_stats = {}
            print(f"{workload}, p50, p99")
            if mode == "epoch":
                print("progress mark(us)")
                st = get_stats(progress_mark)
                all_stats["progress_mark"] = st
            if mode == "2pc":
                print("txnCommitTime(us)")
                st = get_stats(txnCommitTime)
                all_stats["txnCommitTime"] = st

                print("waitPrevTxnInCmt(us)")
                st = get_stats(waitPrevTxnInCmt)
                all_stats["waitPrevTxnInCmt"] = st

                print("waitPrevTxnInPush(us)")
                st = get_stats(waitPrevTxnInPush)
                all_stats["waitPrevTxnInPush"] = st

                print("txnSndPhase(us)")
                st = get_stats(txnSndPhase)
                all_stats["txnSndPhase"] = st

            print(f"{mode} flushStage(us)")
            st = get_stats(flush_all)
            all_stats["flushStage"] = st

            print(f"{mode} flushAtLeastOne(us)")
            st = get_stats(flush_at_least_one)
            all_stats["flush_at_least_one"] = st
            with open(st_path, "wb") as f:
                pickle.dump(all_stats, f)
            

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True)
    parser.add_argument('--mode', required=True, help='2pc, epoch, align_chkpt')
    parser.add_argument('--app', required=True, help='app name')
    parser.add_argument("--out_stats", required=True, help="out stats dir")
    args = parser.parse_args()
    parse_stats_single_exp(args.dir, args.mode, args.app, args.out_stats)


if __name__ == '__main__':
    main()
