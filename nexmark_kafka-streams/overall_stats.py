import argparse
from pathlib import Path
import json
import os
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
           "bids_by_win_queue", "bids_by_price_queue", "max_bids_queue", 
           "txn-begin", "txn-send-offsets", "txn-commit", "flush",
           "commitLat", "avgCommitLat", "execIntrMs"},
    "q8": ["subG1", "subG2", "auc_queue", "per_queue",
           "txn-begin", "txn-send-offsets", "txn-commit", "flush", 
           "commitLat", "avgCommitLat", "execIntrMs"],
}

out_stage_names = {
    "q3": {"aucQueueDelay":"auc_queue(ms)", "perQueueDelay":"per_queue(ms)",
           "q3_sink_ets-7_proc":"subG2(ns)"},
    "q4": {"aucQueueDelay":"auc_queue(ms)", "bidQueueDelay":"per_queue(ms)",
           "aucBidsQueueDelay":"aucBid_queue(ms)", "maxBidsQueueDelay":"maxBid_queue(ms)", 
           "subG2_proc":"subG2(ns)", "subG3_proc":"subG3(ns)", 
           "q4_sink_ets-7_proc":"subG4(ns)",},
    "q5": {"subG1ProcLat": "subG1(ns)", "subG2ProcLat": "subG2(ns)", 
           "bidsQueueDelay": "bid_queue(ms)", 
           "auctionBidsQueueDelay": "auc_queue(ms)", 
           "q5_sink_ets-7_proc": "subG3(ns)"},
    "q6": {"aucQueueTime": "aucQueueTime(ms)", 
           "bidQueueTime": "bidQueueTime(ms)", 
           "topo2_proc": "subG2(ns)",
           "topo3_proc": "subG3(ns)", "aucBidsQueueTime": "aucBidsQueueTime(ms)", 
           "q6_sink_ets-7_proc": "subG4(ns)"},
    "q7": {"topo2_proc": "subG2(ns)", "q7_sink_ets-7_proc": "subG3(ns)", 
           "bids_by_win_queue": "bids_by_win_queue(ms)", 
           "bids_by_price_queue": "bids_by_price_queue(ms)", 
           "max_bids_queue": "max_bids_queue(ms)", 
           "avgCommitLat": "avgCommitLat(ms)",
           "execIntrMs": "execIntr(ms)"},
    "q8": {"auc_queue": "auc_queue(ms)", "per_queue": "per_queue(ms)", 
           "avgCommitLat": "avgCommitLat(ms)",
           "execIntrMs": "execIntr(ms)"},
}

need_convert_ns_to_ms = {
    "q8": {"txn-send-offsets", 
           "txn-commit", "flush", 
           "commitLat"},
    "q7": {"txn-send-offsets",
           "txn-commit", "flush", 
           "commitLat"},
}

throughput = {
    "q3": [80000, 96000, 112000, 128000],
    "q4": [1000, 1250],
    "q5": [24000, 32000, 40000],
    "q6": [500, 750],
    "q7": [8000, 12000, 16000, 20000],
    "q8": [12000, 16000, 20000, 28000, 32000],
    #"q8": [200, 1000, 4000],
    #"q8": [20000],
}

def get_name(st, app_name):
    need_convert = False
    if st in out_stage_names[app_name]:
        st_name = out_stage_names[app_name][st]
    elif st in need_convert_ns_to_ms[app_name]:
        st_name = f"{st}(ms)"
        need_convert = True
    else:
        st_name = f"{st}(ns)"
    return st_name, need_convert


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, help="dir to parse", required=True)
    parser.add_argument("--app", type=str, help="app to parse", required=True)
    parser.add_argument("--out_stats", type=str, help="output stats dir", required=True)
    args = parser.parse_args()
    tp_stats = {}
    tp_stats_summary = {}
    for tp in throughput[args.app]:
        all_stats = {}
        stat_summary = {}
        for fname in Path(args.dir).glob(f"{tp}_*.pickle"):
            print(fname)
            with open(fname, "rb") as f:
                stats = pickle.load(f)
                s = stages[args.app]
                for st_name in s:
                    if st_name in stats:
                        if st_name not in all_stats:
                            all_stats[st_name] = []
                        one_stat = np.concatenate(stats[st_name])
                        stp50 = np.quantile(one_stat, 0.5)
                        stp99 = np.quantile(one_stat, 0.99)
                        if st_name in need_convert_ns_to_ms[args.app]:
                            stp50 = stp50 / 1000000.0
                            stp99 = stp99 / 1000000.0
                        if st_name not in stat_summary:
                            stat_summary[st_name] = {}
                            stat_summary[st_name]["p50"] = []
                            stat_summary[st_name]["p99"] = []
                            stat_summary[st_name]["files"] = []
                        stat_summary[st_name]["files"].append(fname)
                        stat_summary[st_name]["p50"].append(stp50)
                        stat_summary[st_name]["p99"].append(stp99)
                        all_stats[st_name].append(one_stat)
        tp_stats_summary[tp] = stat_summary
        for st in stages[args.app]:
            if st in all_stats:
                data_arr = np.concatenate(all_stats[st])
                all_stats[st] = data_arr
        tp_stats[tp] = all_stats

    for st in stages[args.app]:
        for tp in throughput[args.app]:
            stats_summary = tp_stats_summary[tp]
            if st in stats_summary:
                p50s = stats_summary[st]["p50"]
                p99s = stats_summary[st]["p99"]
                files = stats_summary[st]["files"]
                if st in need_convert_ns_to_ms[args.app]:
                    st_name = f"{st}(ms)"
                else:
                    st_name = f"{st}(ns)"
                for i in range(len(p50s)):
                    print(f"{tp},{files[i]},{st_name},{p50s[i]},{p99s[i]}")
        print()
    print()

    summary_stats = {}
    for st in stages[args.app]:
        p50s = []
        p99s = []
        for tp in throughput[args.app]:
            statsOfATp = tp_stats[tp]
            if st in statsOfATp:
                data_arr = tp_stats[tp][st]
                if st in out_stage_names[args.app]:
                    st_name = out_stage_names[args.app][st]
                else:
                    st_name = f"{st}(ns)"
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
        if p50s:
            summary_stats[st] = {}
            summary_stats[st]["p50"] = p50s
            summary_stats[st]["p99"] = p99s

    os.makedirs(args.out_stats, exist_ok=True)
    fpath = os.path.join(args.out_stats, f"{args.app}_stats.json")
    with open(fpath, "w") as f:
        json.dump(summary_stats, f)

    print()
    for st in stages[args.app]:
        if st in summary_stats:
            p50s = summary_stats[st]["p50"]
            p99s = summary_stats[st]["p99"]
            st_name, need_convert = get_name(st, args.app)
            print(f"{st_name},Kafka p50,Kafka p99")
            for i in range(len(throughput[args.app])):
                tp = throughput[args.app][i]
                if need_convert:
                    p50 = p50s[i] / 1000000.0
                    p99 = p99s[i] / 1000000.0
                else:
                    p50 = p50s[i]
                    p99 = p99s[i]
                print(f"{tp},{p50},{p99}")
            print()


if __name__ == '__main__':
    main()
