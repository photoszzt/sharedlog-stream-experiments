import argparse
import os
from pathlib import Path
import json
import numpy as np
import pickle

stages = {
    "q3": {"aucProc", "perProc", "subG2_left", "subG2_right", 
           "procToq3_aucsBySellerID_out_src", "procToq3_personsByID_out_src", },
    "q4": {"aucProc", "bidProc", "subG2_left", "subG2_right", 
           "subG3Proc", "subG4Proc", "procToq46_aucsByID_src", "procToq46_bidsByAucID_src",
           "procToq4_aucIDCat_src", "procToq4_maxBids_src"},
    "q5": {"subG1Proc", "subG2Proc", "subG3Proc", "procTobids_src", "procToaucBids_src"},
    "q6": {"aucProc", "bidProc", "subG2_left", "subG2_right",
           "subG3Proc", "subG4Proc", "procToq46_aucsByID_src", 
           "procToq46_bidsByAucID_src", "procToq6_aucIDSeller_src", 
           "procToq6_maxBids_src"},
    "q7": {"bidByPriceProc", "bidByWinProc", "subG2Proc", "subG2_left", "subG2_right",
           "procTobid_by_price_src", "procTobid_by_win_src", "procTomax_bids_src"},
    "q8": {"aucProc", "perProc", "subG2_left", "subG2_right", 
           "procToq8_aucsBySellerID_out_src", "procToq8_personsByID_out_src",
           "streamTimeq8_aucsBySellerID_out", "streamTimeq8_personsByID_out",
           "msgBatchTimeq8_aucsBySellerID_out_src", "msgBatchTimeq8_personsByID_out_src", 
           "flushStage", "flushAtLeastOne", "markPartUs"},
}

translate = {
    "q3": {"aucProc": "subG1", "perProc": "subG1",
           "subG2_left": "subG2", "subG2_right": "subG2", },
    "q4": {"aucProc": "subG1", "bidProc": "subG1",
           "subG2_left": "subG2", "subG2_right": "subG2",},
    "q5": {},
    "q6": {"aucProc": "subG1", "bidProc": "subG1",
           "subG2_left": "subG2", "subG2_right": "subG2",},
    "q7": {"subG2_left": "subG3", "subG2_right": "subG3"},
    "q8": {"aucProc": "subG1", "perProc": "subG1",
           "subG2_left": "subG2", "subG2_right": "subG2",
           "procToq8_aucsBySellerID_out_src": "auc_queue",
           "procToq8_personsByID_out_src": "per_queue",
           "streamTimeq8_aucsBySellerID_out": "streamTimeAuc",
           "streamTimeq8_personsByID_out": "streamTimePer",
           "msgBatchTimeq8_aucsBySellerID_out_src": "msgBatchTimeAuc",
           "msgBatchTimeq8_personsByID_out_src": "msgBatchTimePer"},
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
            if "epoch" in d:
                tps_per_work = int(d.split("_")[0][:-3])
                if tps_per_work not in dirs_dict:
                    dirs_dict[tps_per_work] = []
                dirs_dict[tps_per_work].append(os.path.join(root, d, "logs"))
    print(dirs_dict)
    os.makedirs(args.out_stats, exist_ok=True)
    for tps_per_work, dirpaths in dirs_dict.items():
        visited_files = set()
        for dirpath in dirpaths:
            stats = {}
            for fname in Path(dirpath).glob("**/*.stderr"):
                print(fname)
                basename = os.path.basename(fname)
                if basename in visited_files:
                    continue
                visited_files.add(basename)
                with open(fname, "r") as f:
                    for line in f:
                        if ": [" in line:
                            l = line.strip().split(": ")
                            name = l[0].strip()
                            if name in stages[args.app]:
                                data = l[1].strip("[]").split(" ")
                                data = [int(x) for x in data]
                                if args.app in translate and name in translate[args.app]:
                                    name = translate[args.app][name]
                                if name not in stats:
                                    stats[name] = []
                                stats[name].append(data)
            mtime = int(os.stat(dirpath).st_mtime)
            data_path = os.path.join(args.out_stats, f"{tps_per_work}_{mtime}.pickle")
            with open(data_path, "wb") as f:
                pickle.dump(stats, f)


if __name__ == '__main__':
    main()
