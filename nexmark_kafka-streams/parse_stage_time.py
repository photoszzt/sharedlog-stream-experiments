import argparse
import os
from pathlib import Path
import json
import numpy as np
import pickle

stages = {
    "q3": {"subGAuc_proc", "subGPer_proc", "aucQueueDelay", "perQueueDelay",
           "q3_sink_ets-7_proc"},
    "q4": {"subGAuc_proc", "subGBid_proc", "aucQueueDelay", "bidQueueDelay",
           "aucBidsQueueDelay", "maxBidsQueueDelay", "subG2_proc", "subG3_proc",
           "q4_sink_ets-7_proc"},
    "q5": {"subG1ProcLat", "subG2ProcLat", "bidsQueueDelay", "auctionBidsQueueDelay",
           "q5_sink_ets-7_proc"},
    "q6": {"subGAuc_proc", "subGBid_proc", "aucQueueTime", "bidQueueTime", "topo2_proc",
           "topo3_proc", "aucBidsQueueTime", "q6_sink_ets-7_proc"},
    "q7": {"bids_by_win_proc", "bids_by_price_proc", "bids_by_win_queue",
           "bids_by_price_queue", "max_bids_queue", "topo2_proc", "q7_sink_ets-7_proc"},
    "q8": {"subAuc_proc", "subPer_proc", "auc_queue", "per_queue", "q8_sink_ets-7_proc",
           "txn-begin", "txn-send-offsets", "txn-commit", "flush"},
}

translate = {
    "q3": {"subGAuc_proc": "subG1", "subGPer_proc": "subG1"},
    "q8": {"subAuc_proc": "subG1", "subPer_proc": "subG1", 
           "q8_sink_ets-7_proc": "subG2"},
    "q4": {"subGAuc_proc": "subG1", "subGBid_proc": "subG1"},
    "q6": {"subGAuc_proc": "subG1", "subGBid_proc": "subG1"},
}


def main():
    parser = argparse.ArgumentParser(description='Parse stage time')
    parser.add_argument('--dir', type=str, help='dir to parse', required=True)
    parser.add_argument('--app', type=str, help='app to parse', required=True)
    parser.add_argument('--out_stats', type=str,
                        help='output stats dir', required=True)
    args = parser.parse_args()
    dirs_dict = {}

    for root, dirs, _ in os.walk(args.dir):
        for d in dirs:
            if "eo" in d:
                tps_per_work = int(d.split("_")[0][:-3])
                if tps_per_work not in dirs_dict:
                    dirs_dict[tps_per_work] = []
                dirs_dict[tps_per_work].append(os.path.join(root, d, "logs"))
    print(dirs_dict)
    os.makedirs(args.out_stats, exist_ok=True)
    for tps_per_work, dirpaths in dirs_dict.items():
        for dirpath in dirpaths:
            stats = {}
            for fname in Path(dirpath).glob("*nexmark*.stdout"):
                print(fname)
                with open(fname, "r") as f:
                    for line in f:
                        if "{" in line and ": [" in line:
                            l = line.strip().split(": ")
                            name = l[0].strip("{\"")
                            if name in stages[args.app] or "commitLat" in name or "avgCommitLat" in name or "execIntrMs" in name:
                                data = l[1].strip("[]{}\"").split(", ")
                                data = [float(x) for x in data]
                                if args.app in translate and name in translate[args.app]:
                                    name = translate[args.app][name]
                                if "commitLat" in name:
                                    name = "commitLat"
                                if "avgCommitLat" in name:
                                    name = "avgCommitLat"
                                if "execIntrMs" in name:
                                    name = "execIntrMs"
                                if name not in stats:
                                    stats[name] = []
                                stats[name].append(data)
            mtime = int(os.stat(dirpath).st_mtime)
            data_path = os.path.join(args.out_stats, f"{tps_per_work}_{mtime}.pickle")
            with open(data_path, "wb") as f:
                pickle.dump(stats, f)


if __name__ == '__main__':
    main()
