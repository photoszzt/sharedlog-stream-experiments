import argparse
import os
from pathlib import Path
import json
import numpy as np

stages = {"q3": {"subGAuc_proc", "subGPer_proc", "aucQueueDelay", "perQueueDelay"},
        "q4": {"subGAuc_proc", "subGBid_proc",    "aucQueueDelay",    "bidQueueDelay",
            "aucBidsQueueDelay",    "maxBidsQueueDelay",    "subG2_proc",    "subG3_proc",},
          "q5": {"subG1ProcLat", "subG2ProcLat", "bidsQueueDelay", "auctionBidsQueueDelay",},
          "q6": {"subGAuc_proc", "subGBid_proc", "aucQueueTime", "bidQueueTime", "topo2_proc",
              "topo3_proc", "aucBidsQueueTime",},
          "q7": {"bids_by_win_proc", "bids_by_price_proc", "bids_by_win_queue",
              "bids_by_price_queue", "max_bids_queue", "topo2_proc",},
          "q8": {"subAuc_proc", "subPer_proc", "auc_queue", "per_queue",},
          }


def main():
    parser = argparse.ArgumentParser(description='Parse stage time')
    parser.add_argument('--dir', type=str, help='dir to parse', required=True)
    parser.add_argument('--app', type=str, help='app to parse', required=True)
    parser.add_argument('--out_stats', type=str, help='output stats dir', required=True)
    args = parser.parse_args()
    dirs_dict = {}
    stats = {}

    for root, dirs, _ in os.walk(args.dir):
        for d in dirs:
            if "eo" in d:
                tps_per_work = int(d.split("_")[0][:-3])
                dirs_dict[tps_per_work] = os.path.join(root, d, "logs")
    for tps_per_work, dirpath in dirs_dict.items():
        stats[tps_per_work] = {}
        for fname in Path(dirpath).glob("*nexmark*.stdout"):
            with open(fname, "r") as f:
                for line in f:
                    if "{" in line and ": [" in line:
                        stat = json.loads(line.strip())
                        for name, data in stat.items():
                            if name in stages[args.app]:
                                if name not in stats[tps_per_work]:
                                    stats[tps_per_work][name] = numpy.array()
                                np.append(stats[tps_per_work][name], data)
    for tps_per_work, stat in stats.items():
        mtime = int(os.stat(dirs_dict[tps_per_work]).st_mtime)
        all_data_path = os.path.join(
            args.out_stats, f"{tps_per_work}_{mtime}.pickle")
        with open(all_data_path, "wb") as f:
            pickle.dump(stat, f)
        # summary = os.path.join(
        #     args.out_stats, f"{args.app}_{tps_per_work}_{mtime}_stat.json")
        # summary_stat = {}
        # for name, data in stat.items():
        #     quan = quantiles(data, n=100)
        #     summary_stat[name] = {"mean": mean(data), "std": stdev(data), "min": min(data), "max": max(data),
        #                           "p25": quan[24], "p50": quan[49],
        #                           "p90": quan[89], "p99": quan[98]}
        # with open(summary, "w") as f:
        #     json.dump(summary_stat, f)


if __name__ == '__main__':
    main()
