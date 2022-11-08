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
    "q8": ["subG1", "subG2", "auc_queue", "per_queue",
           "txn-begin", "txn-send-offsets", "txn-commit", "flush", 
           "commitLat", "avgCommitLat", "execIntrMs"],
}

out_stage_names = {
    "q3": {"subG1", "aucQueueDelay", "perQueueDelay",
           "q3_sink_ets-7_proc"},
    "q4": {"subG1", "aucQueueDelay", "bidQueueDelay",
           "aucBidsQueueDelay", "maxBidsQueueDelay", "subG2_proc", "subG3_proc", 
           "q4_sink_ets-7_proc",},
    "q5": {"subG1ProcLat", "subG2ProcLat", "bidsQueueDelay", "auctionBidsQueueDelay", 
           "q5_sink_ets-7_proc"},
    "q6": {"subG1": "subG1(ns)", "aucQueueTime": "aucQueueTime(ms)", 
           "bidQueueTime": "bidQueueTime(ms)", "topo2_proc": "subG2(ns)",
           "topo3_proc": "subG3(ns)", "aucBidsQueueTime": "aucBidsQueueTime(ms)", 
           "q6_sink_ets-7_proc": "subG4(ns)"},
    "q7": {"bids_by_win_proc": "bids_by_win_proc(ns)", "bids_by_price_proc": "bids_by_price_proc(ns)", 
           "topo2_proc": "subG2(ns)", "q7_sink_ets-7_proc": "subG3(ns)", 
           "bids_by_win_queue": "bids_by_win_queue(ms)", 
           "bids_by_price_queue": "bids_by_price_queue(ms)", 
           "max_bids_queue": "max_bids_queue(ms)", },
    "q8": {"subG1": "subG1(ns)", "auc_queue": "auc_queue(ms)", "per_queue": "per_queue(ms)", 
           "subG2": "subG2(ns)",
           "txn-begin": "txn-begin(ns)", "txn-send-offsets": "txn-send-offsets(ns)", 
           "txn-commit": "txn-commit(ns)", "flush": "flush(ns)", 
           "commitLat": "commitLat(ns)", "avgCommitLat": "avgCommitLat(ms)",
           "execIntrMs": "execIntr(ms)"},
}

throughput = {
    "q3": [80000, 96000, 112000, 128000],
    "q4": [1000, 1250],
    "q5": [24000, 32000, 40000],
    "q6": [500, 750],
    "q7": [12000, 16000, 28000, 32000, 36000],
    "q8": [12000, 16000, 20000, 28000, 32000],
    #"q8": [200, 1000, 4000],
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
                            all_stats[st] = []
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

    print()
    for st in stages[args.app]:
        if st in summary_stats:
            p50s = summary_stats[st]["p50"]
            p99s = summary_stats[st]["p99"]
            st_name = out_stage_names[args.app][st]
            print(f"{st_name},Kafka p50,Kafka p99")
            for i in range(len(throughput[args.app])):
                tp = throughput[args.app][i]
                print(f"{tp},{p50s[i]},{p99s[i]}")
            print()


if __name__ == '__main__':
    main()
