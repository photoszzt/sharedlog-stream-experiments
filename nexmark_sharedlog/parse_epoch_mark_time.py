import argparse
import os
import json
from pathlib import Path
from statistics import quantiles, mean, stdev
import numpy as np

def printStats(tp, statk, stats, all_stats):
    print("tps/work, stage, mean, std, min, p25, p50, p90, p99, max")
    per_stage_stats = {}
    for stage in statk:
        if stage not in per_stage_stats:
            per_stage_stats[stage] = {}
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
            per_stage_stats[stage][tps_per_work] = {
                'mean': mean,
                'std': std,
                'min': min_data,
                'p25': p25,
                'p50': p50,
                'p90': p90,
                'p99': p99,
                'max': max_data,
            }
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
    return summary_stats, per_stage_stats

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


def get_sorted_keys(dic):
    tp = sorted(dic.keys())
    fa_keys = None
    i = 0
    while i < len(tp):
        fa_keys = dic[tp[i]].keys()
        if len(fa_keys) != 0:
            break
        i = i + 1
    fak = sorted(fa_keys)
    return tp, fak


def parse_single_topdir(directory, mode):
    dirs_dict = {}
    for root, dirs, _ in os.walk(directory):
        for d in dirs:
            if mode in d or "Kb" in d:
                try:
                    if mode in d:
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
    commitTxnAPITime = {}
    sendOffsetTime = {}
    txnCommitTime = {}
    markPartTime = {}
    appendEpochMark = {}
    markEpochPrepare = {}
    all_stats_in_dir = {}
    for tps_per_work, dirpaths in dirs_dict.items():
        if tps_per_work not in stats:
            stats[tps_per_work] = {}
        if tps_per_work not in flush_all:
            flush_all[tps_per_work] = {}
        if tps_per_work not in epochMarkTimes:
            epochMarkTimes[tps_per_work] = {}
        if tps_per_work not in flush_at_least_one:
            flush_at_least_one[tps_per_work] = {}
        if tps_per_work not in commitTxnAPITime:
            commitTxnAPITime[tps_per_work] = {}
        if tps_per_work not in sendOffsetTime:
            sendOffsetTime[tps_per_work] = {}
        if tps_per_work not in txnCommitTime:
            txnCommitTime[tps_per_work] = {}
        if tps_per_work not in markPartTime:
            markPartTime[tps_per_work] = {}
        if tps_per_work not in appendEpochMark:
            appendEpochMark[tps_per_work] = {}
        if tps_per_work not in markEpochPrepare:
            markEpochPrepare[tps_per_work] = {}
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
                        if mode == "epoch" and "epochMarkTime" in line:
                            nums = get_nums(line)
                            update_dict(stats, tps_per_work, stage, nums)
                        elif mode == "epoch" and "markPart" in line:
                            nums = get_nums(line)
                            update_dict(markPartTime, tps_per_work, stage, nums)
                        elif mode == "epoch" and "appendEpochMark" in line:
                            nums = get_nums(line)
                            update_dict(appendEpochMark, tps_per_work, stage, nums)
                        elif mode == "epoch" and "markEpochPrepare" in line:
                            nums = get_nums(line)
                            update_dict(markEpochPrepare, tps_per_work, stage, nums)
                        elif "flushStage" in line and "[" in line:
                            nums = get_nums(line)
                            update_dict(flush_all, tps_per_work, stage, nums)
                        elif "flushAtLeastOne" in line and "[" in line:
                            nums = get_nums(line)
                            update_dict(flush_at_least_one, tps_per_work, stage, nums)
                        elif mode == "2pc" and "commitTxnAPITime" in line and "[" in line:
                            nums = get_nums(line)
                            update_dict(commitTxnAPITime, tps_per_work, stage, nums)
                        elif mode == "2pc" and "txnCommitTime" in line and "[" in line:
                            nums = get_nums(line)
                            update_dict(txnCommitTime, tps_per_work, stage, nums)
                        elif mode == "2pc" and "sendOffsetTime" in line and "[" in line:
                            nums = get_nums(line)
                            update_dict(sendOffsetTime, tps_per_work, stage, nums)
                        elif mode == "epoch" and "epoch_mark_times" in line:
                            l = int(line.strip().split(": ")[1])
                            update_dict(epochMarkTimes, tps_per_work, stage, l)
    if mode == "epoch":
        tp = sorted(stats.keys())
        statk = sorted(stats[tp[0]].keys())
        all_mark_stats = {}
        print("progress marking(us)")
        summary, per_stage_stats = printStats(tp, statk, stats, all_mark_stats)
        all_stats_in_dir['progress_mark'] = {
                'per_stage': per_stage_stats,
                'summary': summary,
        }

        print("mark part(us)")
        tp, fak = get_sorted_keys(markPartTime)
        all_mark_part = {}
        summ, per_stage = printStats(tp, fak, markPartTime, all_mark_part)
        all_stats_in_dir['mark_part'] = {
                'per_stage': per_stage,
                'summary': summ,
        }

        print("append epoch mark(us)")
        tp, fak = get_sorted_keys(appendEpochMark)
        all_append_mark = {}
        summ, per_stage = printStats(tp, fak, appendEpochMark, all_append_mark)
        all_stats_in_dir['append_mark'] = {
                'per_stage': per_stage,
                'summary': summ,
        }

        print("mark prepare(us)")
        tp, fak = get_sorted_keys(markEpochPrepare)
        all_prepare_mark = {}
        summ, per_stage = printStats(tp, fak, markEpochPrepare, all_prepare_mark)
        all_stats_in_dir['prepare_mark'] = {
                'per_stage': per_stage,
                'summary': summ,
        }
        # os.makedirs(args.out_dir, exist_ok=True)
        # p = os.path.join(args.out_dir, "mark_time.json")
        # with open(p, "w") as f:
        #     json.dump(summary, f)
                         
    print("flush all(us)")
    tp, fak = get_sorted_keys(flush_all)
    all_flush_stats = {}
    summ, per_stage = printStats(tp, fak, flush_all, all_flush_stats)
    all_stats_in_dir['flush_all'] = {
            'per_stage': per_stage,
            'summary': summ,
    }

    print("flush at least one(us)")
    tp, fak = get_sorted_keys(flush_at_least_one)
    all_flush_alone = {}
    summ, per_stage = printStats(tp, fak, flush_at_least_one, all_flush_alone)
    all_stats_in_dir['flush_at_least_one'] = {
            'per_stage': per_stage,
            'summary': summ,
    }

    if mode == "2pc":
        print("commit txn api(us)")
        tp, fak = get_sorted_keys(commitTxnAPITime)
        all_cmt_txn_api = {}
        summ, per_stage = printStats(tp, fak, commitTxnAPITime, all_cmt_txn_api)
        all_stats_in_dir['commitTxnAPITime'] = {
                'per_stage': per_stage,
                'summary': summ,
        }

        print("txn commit time(us)")
        tp, fak = get_sorted_keys(txnCommitTime)
        all_txn_commit = {}
        summ, per_stage = printStats(tp, fak, txnCommitTime, all_txn_commit)
        all_stats_in_dir['txnCommitTime'] = {
                'per_stage': per_stage,
                'summary': summ,
        }

        print("send offset time(us)")
        tp, fak = get_sorted_keys(sendOffsetTime)
        all_send_offset = {}
        summ, per_stage = printStats(tp, fak, sendOffsetTime, all_send_offset)
        all_stats_in_dir['sendOffsetTime'] = {
                'per_stage': per_stage,
                'summary': summ,
        }
    return all_stats_in_dir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True)
    parser.add_argument('--mode', required=True, help='2pc, epoch, align_chkpt')
    args = parser.parse_args()
    #         print(f"{tps_per_work},{stage},{mean(data)},{stdev(data)}")
    parse_single_topdir(args.dir, args.mode)


if __name__ == '__main__':
    main()
