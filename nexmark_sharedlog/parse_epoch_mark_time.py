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


def get_name_nums(line):
    sps = line.strip().split(": ")
    name = sps[0].split(" ")[0]
    nsp = name.rsplit("_", 1)
    name = nsp[0]
    try:
        idx = int(nsp[1])
    except ValueError:
        idx = int(nsp[1].split("(")[0])
    l = sps[1]
    if '=' in l:
        l = l.split('=')[1]
    nums = l.strip("[]{}").split(" ")
    nums = [int(i) for i in nums]
    return nums, name, idx


def update_dict(dic, tps_per_work, stage, item):
    if stage not in dic[tps_per_work]:
        dic[tps_per_work][stage] = []
    dic[tps_per_work][stage].append(item)


def update_idx_dict(dic, tps_per_work, idx, stage, item):
    if stage not in dic[tps_per_work][idx]:
        dic[tps_per_work][idx][stage] = []
    dic[tps_per_work][idx][stage].append(item)


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


def get_dirs_dict(directory, mode, app):
    dirs_dict = {}
    for root, dirs, _ in os.walk(directory):
        for d in dirs:
            if mode in d or "Kb" in d:
                try:
                    splits = d.split("_")
                    if mode in d:
                        tps_per_work = int(splits[0][:-3])
                    else:
                        tps_per_work = d
                    k = tps_per_work
                    if app == "fanout":
                        f = int(splits[-1])
                        k = (tps_per_work, f)
                    if k not in dirs_dict:
                        dirs_dict[k] = []
                    dirs_dict[k].append(os.path.join(root, d, "logs"))
                except Exception:
                    pass
    return dirs_dict


def parse_single_topdir(directory, mode, app):
    dirs_dict = get_dirs_dict(directory, mode, app)
    progress_mark = {}
    flush_all = {}
    flush_at_least_one = {}
    epochMarkTimes = {}
    commitTxnAPITime = {}
    sendOffsetTime = {}
    txnCommitTime = {}
    markPartTime = {}
    appendEpochMark = {}
    markEpochPrepare = {}
    waitPrevTxn = {}
    appendTxnMeta2pc = {}
    waitPrevTxn2pc = {}
    epochMarkerSize = {}
    all_stats_in_dir = {}
    # q8_personsByID_out_flushBuf = {}
    # q8_aucsBySellerID_out_flushBuf = {}
    # q8_out_flushBuf = {}
    # q8AuctionsBySellerIDWinTab_changelog_flushBuf = {}
    # q8PersonsByIDWinTab_changelog_flushBuf = {}
    # for i in range(0, 32):
    #     q8_personsByID_out_flushBuf[i] = {}
    #     q8_aucsBySellerID_out_flushBuf[i] = {}
    #     q8_out_flushBuf[i] = {}
    #     q8AuctionsBySellerIDWinTab_changelog_flushBuf[i] = {}
    #     q8PersonsByIDWinTab_changelog_flushBuf[i] = {}
    for tps_per_work in dirs_dict:
        if tps_per_work not in progress_mark:
            progress_mark[tps_per_work] = {}
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
        if tps_per_work not in waitPrevTxn:
            waitPrevTxn[tps_per_work] = {}
        if tps_per_work not in epochMarkerSize:
            epochMarkerSize[tps_per_work] = {}
        if tps_per_work not in waitPrevTxn2pc:
            waitPrevTxn2pc[tps_per_work] = {}
        if tps_per_work not in appendTxnMeta2pc:
            appendTxnMeta2pc[tps_per_work] = {}
        #for i in range(0, 32):
        #    if tps_per_work not in q8_personsByID_out_flushBuf[i]:
        #        q8_personsByID_out_flushBuf[i][tps_per_work] = {}
        #    if tps_per_work not in q8_aucsBySellerID_out_flushBuf[i]:
        #        q8_aucsBySellerID_out_flushBuf[i][tps_per_work] = {}
        #    if tps_per_work not in q8_out_flushBuf[i]:
        #        q8_out_flushBuf[i][tps_per_work] = {}
        #    if tps_per_work not in q8AuctionsBySellerIDWinTab_changelog_flushBuf[i]:
        #        q8AuctionsBySellerIDWinTab_changelog_flushBuf[i][tps_per_work] = {}
        #    if tps_per_work not in q8PersonsByIDWinTab_changelog_flushBuf[i]:
        #        q8PersonsByIDWinTab_changelog_flushBuf[i][tps_per_work] = {}
    for tps_per_work, dirpaths in dirs_dict.items():
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
                            update_dict(progress_mark, tps_per_work, stage, nums)
                        elif mode == "epoch" and "markPart" in line:
                            nums = get_nums(line)
                            update_dict(markPartTime, tps_per_work, stage, nums)
                        elif mode == "epoch" and "appendEpochMark" in line:
                            nums = get_nums(line)
                            update_dict(appendEpochMark, tps_per_work, stage, nums)
                        elif mode == "epoch" and "markEpochPrepare" in line:
                            nums = get_nums(line)
                            update_dict(markEpochPrepare, tps_per_work, stage, nums)
                        elif mode == "epoch" and "epochMarkerSize" in line:
                            nums = get_nums(line)
                            update_dict(epochMarkerSize, tps_per_work, stage, nums)
                        elif mode == "epoch" and "epoch_mark_times" in line:
                            l = int(line.strip().split(": ")[1])
                            update_dict(epochMarkTimes, tps_per_work, stage, l)
                        elif "flushStage" in line and "[" in line:
                            nums = get_nums(line)
                            update_dict(flush_all, tps_per_work, stage, nums)
                        elif "flushAtLeastOne" in line and "[" in line:
                            nums = get_nums(line)
                            update_dict(flush_at_least_one, tps_per_work, stage, nums)
                        # elif "q8_personsByID_out_flushBuf" in line and "[" in line:
                        #     nums, name, idx = get_name_nums(line)
                        #     update_dict(q8_personsByID_out_flushBuf[idx], tps_per_work, stage, nums)
                        # elif "q8_aucsBySellerID_out_flushBuf" in line and "[" in line:
                        #     nums, name, idx = get_name_nums(line)
                        #     update_dict(q8_aucsBySellerID_out_flushBuf[idx], tps_per_work, stage, nums)
                        # elif "q8_out_flushBuf" in line and "[" in line:
                        #     nums, name, idx = get_name_nums(line)
                        #     update_dict(q8_out_flushBuf[idx], tps_per_work, stage, nums)
                        # elif "q8AuctionsBySellerIDWinTab-changelog_flushBuf" in line and "[" in line:
                        #     nums, name, idx = get_name_nums(line)
                        #     update_dict(q8AuctionsBySellerIDWinTab_changelog_flushBuf[idx], tps_per_work, stage, nums)
                        # elif "q8PersonsByIDWinTab-changelog_flushBuf" in line and "[" in line:
                        #     nums, name, idx = get_name_nums(line)
                        #     update_dict(q8PersonsByIDWinTab_changelog_flushBuf[idx], tps_per_work, stage, nums)
                        elif mode == "2pc" and "commitTxnAPITime" in line and "[" in line:
                            nums = get_nums(line)
                            update_dict(commitTxnAPITime, tps_per_work, stage, nums)
                        elif mode == "2pc" and "txnCommitTime" in line and "[" in line:
                            nums = get_nums(line)
                            update_dict(txnCommitTime, tps_per_work, stage, nums)
                        elif mode == "2pc" and "sendOffsetTime" in line and "[" in line:
                            nums = get_nums(line)
                            update_dict(sendOffsetTime, tps_per_work, stage, nums)
                        elif mode == "2pc" and "waitPrevTxn2pc " in line and "[" in line:
                            nums = get_nums(line)
                            update_dict(waitPrevTxn2pc, tps_per_work, stage, nums)
                        elif mode == "2pc" and "waitPrevTxn " in line and "[" in line:
                            nums = get_nums(line)
                            update_dict(waitPrevTxn, tps_per_work, stage, nums)
                        elif mode == "2pc" and "appendTxnMeta2pc " in line and "[" in line:
                            nums = get_nums(line)
                            update_dict(appendTxnMeta2pc, tps_per_work, stage, nums)
    if mode == "epoch":
        tp, fak = get_sorted_keys(progress_mark)
        all_mark_stats = {}
        print("progress marking(us)")
        summary, per_stage_stats = printStats(tp, fak, progress_mark, all_mark_stats)
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

        print("epoch marker size(B)")
        tp, fak = get_sorted_keys(epochMarkerSize)
        all_marker_size = {}
        summ, per_stage = printStats(tp, fak, epochMarkerSize, all_marker_size)
        all_stats_in_dir['marker_size'] = {
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
    # all_stats_in_dir['q8_personsByID_out_flushBuf'] = {}
    # all_stats_in_dir['q8_aucsBySellerID_out_flushBuf'] = {}
    # all_stats_in_dir['q8_out_flushBuf'] = {}
    # all_stats_in_dir['q8AuctionsBySellerIDWinTab-changelog_flushBuf'] = {}
    # all_stats_in_dir['q8PersonsByIDWinTab-changelog_flushBuf'] = {}
    # for i in range(0, 32):
    #     tp, fak = get_sorted_keys(q8_personsByID_out_flushBuf[i])
    #     if len(fak) != 0:
    #         print(f"q8_personsByID_out_flushBuf_{i}")
    #         s = {}
    #         summ, per_stage = printStats(tp, fak, q8_personsByID_out_flushBuf[i], s)
    #         all_stats_in_dir['q8_personsByID_out_flushBuf'][i] = {
    #             'per_stage': per_stage,
    #             'summary': summ,
    #         }

    # for i in range(0, 32):
    #     tp, fak = get_sorted_keys(q8_aucsBySellerID_out_flushBuf[i])
    #     if len(fak) != 0:
    #         print(f"q8_aucsBySellerID_out_flushBuf_{i}")
    #         s = {}
    #         summ, per_stage = printStats(tp, fak, q8_aucsBySellerID_out_flushBuf[i], s)
    #         all_stats_in_dir['q8_aucsBySellerID_out_flushBuf'][i] = {
    #             'per_stage': per_stage,
    #             'summary': summ,
    #         }

    # for i in range(0, 32):
    #     tp, fak = get_sorted_keys(q8_out_flushBuf[i])
    #     if len(fak) != 0:
    #         print(f"q8_out_flushBuf_{i}")
    #         s = {}
    #         summ, per_stage = printStats(tp, fak, q8_out_flushBuf[i], s)
    #         all_stats_in_dir['q8_out_flushBuf'][i] = {
    #             'per_stage': per_stage,
    #             'summary': summ,
    #         }

    # for i in range(0, 32):
    #     tp, fak = get_sorted_keys(q8PersonsByIDWinTab_changelog_flushBuf[i])
    #     if len(fak) != 0:
    #         print(f"q8PersonsByIDWinTab-changelog_flushBuf_{i}")
    #         s = {}
    #         summ, per_stage = printStats(tp, fak, q8PersonsByIDWinTab_changelog_flushBuf[i], s)
    #         all_stats_in_dir['q8PersonsByIDWinTab-changelog_flushBuf'][i] = {
    #             'per_stage': per_stage,
    #             'summary': summ,
    #         }

    # for i in range(0, 32):
    #     tp, fak = get_sorted_keys(q8PersonsByIDWinTab_changelog_flushBuf[i])
    #     if len(fak) != 0:
    #         print(f"q8PersonsByIDWinTab-changelog_flushBuf_{i}")
    #         s = {}
    #         summ, per_stage = printStats(tp, fak, q8PersonsByIDWinTab_changelog_flushBuf[i], s)
    #         all_stats_in_dir['q8PersonsByIDWinTab-changelog_flushBuf'][i] = {
    #             'per_stage': per_stage,
    #             'summary': summ,
    #         }

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

        print("wait prev txn(us)")
        tp, fak = get_sorted_keys(waitPrevTxn)
        all_wait_prev_txn = {}
        summ, per_stage = printStats(tp, fak, waitPrevTxn, all_wait_prev_txn)
        all_stats_in_dir['waitPrevTxn'] = {
                'per_stage': per_stage,
                'summary': summ,
        }

        print("wait prev txn part1(us)")
        tp, fak = get_sorted_keys(waitPrevTxn2pc)
        all_wait_prev_txn_2pc = {}
        summ, per_stage = printStats(tp, fak, waitPrevTxn2pc, all_wait_prev_txn_2pc)
        print(per_stage)
        all_stats_in_dir['waitPrevTxn2pc'] = {
                'per_stage': per_stage,
                'summary': summ,
        }

        print("wait prev txn part2(us)")
        tp, fak = get_sorted_keys(appendTxnMeta2pc)
        all_appendTxnMeta2pc = {}
        summ, per_stage = printStats(tp, fak, appendTxnMeta2pc, all_appendTxnMeta2pc)
        all_stats_in_dir['appendTxnMeta2pc'] = {
                'per_stage': per_stage,
                'summary': summ,
        }
    return all_stats_in_dir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True)
    parser.add_argument('--mode', required=True, help='2pc, epoch, align_chkpt')
    parser.add_argument('--app', required=True, help='app name')
    args = parser.parse_args()
    parse_single_topdir(args.dir, args.mode, args.app)


if __name__ == '__main__':
    main()
