import argparse
import os
from pathlib import Path
import json
from statistics import mean, stdev, quantiles 

stages = {"q3": set("subGAuc_proc", "subGPer_proc", "aucQueueDelay", "perQueueDelay"),
          "q4": set("subGAuc_proc",    "subGBid_proc",    "aucQueueDelay",    "bidQueueDelay",
                    "aucBidsQueueDelay",    "maxBidsQueueDelay",    "subG2_proc",    "subG3_proc",),
          "q5": set("subG1ProcLat", "subG2ProcLat", "bidsQueueDelay", "auctionBidsQueueDelay",),
          "q6": set("subGAuc_proc", "subGBid_proc", "aucQueueTime", "bidQueueTime", "topo2_proc", "topo3_proc", "aucBidsQueueTime",),
          "q7": set("bids_by_win_proc", "bids_by_price_proc", "bids_by_win_queue", "bids_by_price_queue", "max_bids_queue", "topo2_proc",),
          "q8": set("subAuc_proc", "subPer_proc", "auc_queue", "per_queue",),
          }


def main():
    parser = argparse.ArgumentParser(description='Parse stage time')
    parser.add_argument('dir', type=str, help='dir to parse')
    parser.add_argument('app', type=str, help='app to parse')
    parser.add_argument('out_stats', type=str, help='output stats dir')
    args = parser.parse_args()
    dirs = {}
    stats = {}

    with _, dirs, _ in os.walk(args.dir):
        for d in dirs:
            if "eo" in d:
                tps_per_work = int(d.split("_")[0])
                dirs[tps_per_work] = os.path.join(root, d, "logs")
    for tps_per_work, dir in dirs.items():
        stats[tps_per_work] = {}
        for fname in Path(dir).glob("*nexmark*.stdout"):
            with open(fname, "r") as f:
                for line in f:
                    if ": [" in line:
                        stat = json.loads[line]
                        for name, data in stat.items():
                            if name in stages[args.app]:
                                if name not in stats[tps_per_work]:
                                    stats[tps_per_work][name] = []
                                stats[tps_per_work][name].extend(data)
    for tps_per_work, stat in stats.items():
        mtime = os.stat(dirs[tps_per_work]).st_mtime
        all_data_path = os.path.join(
            args.out_stats, f"{args.app}_{tps_per_work}_{mtime}.json")
        with open(all_data_path, "w") as f:
            json.dump(stat, f)
        summary = os.path.join(
            args.out_stats, f"{args.app}_{tps_per_work}_{mtime}_stat.json")
        summary_stat = {}
        for name, data in stat.items():
            summary_stat[name] = {"mean": mean(data), "std": stdev(data_arr), "min": min(data), "max": max(data),
                                  "p25": quantiles(data, 25), "p50": quantiles(data, 50),
                                  "p90": quantiles(data, 90), "p99": quantiles(data, 99)}
        with open(summary, "w") as f:
            json.dump(summary_stat, f)


if __name__ == '__main__':
    main()
