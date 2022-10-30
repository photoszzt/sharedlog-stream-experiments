import argparse
from pathlib import Path
import pickle
import numpy as np

stages = {
    "q3": {"subG1", "aucQueueDelay", "perQueueDelay",
           "q3_sink_ets-7_proc"},
    "q4": {"subG1", "aucQueueDelay", "bidQueueDelay",
           "aucBidsQueueDelay", "maxBidsQueueDelay", "subG2_proc", "subG3_proc", 
           "q4_sink_ets-7_proc",},
    "q5": {"subG1ProcLat", "subG2ProcLat", "bidsQueueDelay", "auctionBidsQueueDelay", 
           "q5_sink_ets-7_proc"},
    "q6": {"subG1", "aucQueueTime", "bidQueueTime", "topo2_proc",
           "topo3_proc", "aucBidsQueueTime", "q6_sink_ets-7_proc"},
    "q7": {"bids_by_win_proc", "bids_by_price_proc", "topo2_proc", "q7_sink_ets-7_proc", 
           "bids_by_win_queue", "bids_by_price_queue", "max_bids_queue", },
    "q8": {"subG1", "auc_queue", "per_queue", "q8_sink_ets-7_proc"},
}

throughput = {
    "q3": [80000, 96000, 112000, 128000],
    "q4": [1000, 1250],
    "q5": [24000, 32000, 40000],
    "q6": [500, 750],
    "q7": [12000, 16000, 28000, 32000, 36000],
    #"q8": [16000, 20000, 28000, 32000],
    "q8": [200, 1000, 4000],
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
                    if st not in all_stats:
                        all_stats[st] = []
                    all_stats[st].extend(stats[st])
        for st in stages[args.app]:
            data_arr = np.concatenate(all_stats[st])
            all_stats[st] = data_arr
        tp_stats[tp] = all_stats

    for st in stages[args.app]:
        for tp in throughput[args.app]:
            data_arr = tp_stats[tp][st]
            print(f"{tp},{st},{np.mean(data_arr)},{np.std(data_arr)},{np.min(data_arr)},{np.quantile(data_arr, 0.25)},{np.quantile(data_arr, 0.5)},{np.quantile(data_arr, 0.9)},{np.quantile(data_arr, 0.99)},{np.max(data_arr)}")


if __name__ == '__main__':
    main()
