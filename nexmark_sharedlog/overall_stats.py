import argparse
from pathlib import Path
import pickle
import os
import numpy as np
import json
from parse_stage_time import stages

throughput = {
    "q3": [80000, 96000, 112000, 128000],
    "q4": [1000, 1250],
    "q5": [24000, 32000, 40000, 56000, 64000],
    "q6": [500, 750],
    "q7": [12000, 16000, 28000, 32000, 36000],
    #"q8": [200, 1000, 4000],
    "q8": [12000, 16000, 20000, 28000, 32000],
}

stages = {
    "q3": {"subG1", "subG2", "procToq3_aucsBySellerID_out_src",
           "procToq3_personsByID_out_src"},
    "q4": {"subG1", "subG2", "subG3Proc", "subG4Proc", 
           "procToq46_aucsByID_src", "procToq46_bidsByAucID_src",
           "procToq4_aucIDCat_src", "procToq4_maxBids_src"},
    "q5": {"subG1Proc", "subG2Proc", "subG3Proc", "procTobids_src", "procToaucBids_src"},
    "q6": {"subG1", "subG2","subG3Proc", "subG4Proc", 
           "procToq46_aucsByID_src", 
           "procToq46_bidsByAucID_src", "procToq6_aucIDSeller_src", 
           "procToq6_maxBids_src"},
    "q7": {"bidByPriceProc", "bidByWinProc", "subG2Proc", "subG3", 
           "procTobid_by_price_src", "procTobid_by_win_src", "procTomax_bids_src"},
    "q8": ["subG1", "subG2", "auc_queue", "per_queue",
           "streamTimeAuc", "streamTimePer",
           "msgBatchTimeAuc", "msgBatchTimePer",
           "flushStage", "flushAtLeastOne", "markPartUs", 
           "execIntrMs", "thisAndLastCmtMs"],
}

out_stage_names = {
        "q8": {"subG1": "subG1(ns)", "subG2": "subG2(ns)", 
            "auc_queue": "auc_queue(ms)", 
            "per_queue": "per_queue(ms)",
            "streamTimeAuc": "streamTimeAuc(ms)", 
            "streamTimePer": "streamTimePer(ms)",
            "msgBatchTimeAuc": "msgBatchTimeAuc(ms)", 
            "msgBatchTimePer": "msgBatchTimePer(ms)",
            "flushStage": "flushStage(us)", 
            "flushAtLeastOne": "flushAtLeastOne(us)",
            "markPartUs": "markPart(us)",
            "execIntrMs": "execIntr(ms)", "thisAndLastCmtMs": "thisAndLastCmt(ms)"},
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, help="dir to parse", required=True)
    parser.add_argument("--app", type=str, help="app to parse", required=True)
    parser.add_argument("--out_stats", type=str, help="output stats dir", required=True)
    args = parser.parse_args()
    tp_stats = {}
    for tp in throughput[args.app]:
        all_stats = {}
        for fname in Path(args.dir).glob(f"{tp}_*.pickle"):
            with open(fname, "rb") as f:
                stats = pickle.load(f)
                print(stats.keys())
                s = stages[args.app]
                for st in s:
                    if st in stats:
                        if st not in all_stats:
                            all_stats[st] = stats[st]
                        else:
                            all_stats[st].extend(stats[st])
        for st in stages[args.app]:
            if st in all_stats:
                data_arr = np.concatenate(all_stats[st])
                all_stats[st] = data_arr
        tp_stats[tp] = all_stats

    summary_stats = {}
    for st in stages[args.app]:
        p50s = []
        p99s = []
        for tp in throughput[args.app]:
            if st in tp_stats[tp]:
                data_arr = tp_stats[tp][st]
                st_name = out_stage_names[args.app][st]
                mean = np.mean(data_arr)
                std = np.std(data_arr)
                min_data = np.min(data_arr)
                p25 = np.quantile(data_arr, 0.25)
                p50 = np.quantile(data_arr, 0.5)
                p90 = np.quantile(data_arr, 0.9)
                p99 = np.quantile(data_arr, 0.99)
                max_data = np.max(data_arr)
                p50s.append(p50)
                p99s.append(p99)
                print(f"{tp},{st_name},{mean},{std},{min_data},{p25},{p50},{p90},{p99},{max_data}")
        summary_stats[st] = {}
        summary_stats[st]["p50"] = p50s
        summary_stats[st]["p99"] = p99s

    os.makedirs(args.out_stats, exist_ok=True)
    fpath = os.path.join(args.out_stats, f"{args.app}_stats.json")
    with open(fpath, "w") as f:
        json.dump(summary_stats, f)

    print()
    for st in stages[args.app]:
        p50s = summary_stats[st]["p50"]
        p99s = summary_stats[st]["p99"]
        if p50s and p99s:
            st_name = out_stage_names[args.app][st]
            print(f"{st_name},Impeller p50,Impeller p99")
            for i in range(len(throughput[args.app])):
                tp = throughput[args.app][i]
                print(f"{tp},{p50s[i]},{p99s[i]}")
            print()


if __name__ == '__main__':
    main()
