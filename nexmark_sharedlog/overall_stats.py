import argparse
from pathlib import Path
import pickle
import numpy as np
from parse_stage_time import stages

throughput = {
    "q3": [80000, 96000, 112000, 128000],
    "q4": [],
    "q5": [24000, 32000, 40000, 56000, 64000],
    "q6": [],
    "q7": [12000, 16000, 28000, 32000, 36000],
    "q8": [16000, 20000, 28000, 32000],
}

stages = {
    "q3": {"subG1", "subG2", "procToq3_aucsBySellerID_out_src",
           "procToq3_personsByID_out_src"},
    "q4": {},
    "q5": {"subG1Proc", "subG2Proc", "subG3Proc", "procTobids_src", "procToaucBids_src"},
    "q6": {},
    "q7": {"bidByPriceProc", "bidByWinProc", "subG2Proc", "subG3", 
           "procTobid_by_price_src", "procTobid_by_win_src", "procTomax_bids_src"},
    "q8": {"subG1", "subG2", "procToq8_aucsBySellerID_out_src", "procToq8_personsByID_out_src"},
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, help="dir to parse", required=True)
    parser.add_argument("--app", type=str, help="app to parse", required=True)
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

    for st in stages[args.app]:
        for tp in throughput[args.app]:
            if st in tp_stats[tp]:
                data_arr = tp_stats[tp][st]
                print(f"{tp},{st},{np.mean(data_arr)},{np.std(data_arr)},{np.min(data_arr)},{np.quantile(data_arr, 0.25)},{np.quantile(data_arr, 0.5)},{np.quantile(data_arr, 0.9)},{np.quantile(data_arr, 0.99)},{np.max(data_arr)}")


if __name__ == '__main__':
    main()
