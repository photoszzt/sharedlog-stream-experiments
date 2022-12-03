import argparse
import os
import gzip
import json
import numpy as np
import pickle
from statistics import mean, stdev
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, help='dir to parse', required=True)
    parser.add_argument('--out_stats', type=str, required=True)
    parser.add_argument('--app', type=str, required=True)
    args = parser.parse_args()
    dirs_dict = {}
    latency = {}
    all_stats = {}
    for root, dirs, _ in os.walk(args.dir):
        for d in dirs:
            if "eo" in d:
                try:
                    tps_per_work = int(d.split("_")[0][:-3])
                    if tps_per_work not in dirs_dict:
                        dirs_dict[tps_per_work] = []
                    dirs_dict[tps_per_work].append(os.path.join(root, d))
                except Exception:
                    pass
    print(dirs_dict)
    os.makedirs(args.out_stats, exist_ok=True)
    tpss = sorted(dirs_dict.keys())
    for tps in tpss:
        dirpaths = dirs_dict[tps]
        all_data = []
        for dpath in dirpaths:
            e2e_latency = []
            stats_dir = os.path.join(dpath, "logs")
            for root, dirs, files in os.walk(stats_dir):
                for fname in files:
                    if "sink_ets" in fname:
                        fpath = os.path.join(root, fname)
                        with open(fpath, 'r') as f:
                            for line in f:
                                l = line.strip("[]\n").split(", ")
                                l = [int(i) for i in l]
                                e2e_latency.append(l)
            if e2e_latency:
                e2e_lat = np.concatenate(e2e_latency)
                p50 = np.quantile(e2e_lat, 0.5)
                p99 = np.quantile(e2e_lat, 0.99)
                if tps not in latency:
                    latency[tps] = {}
                    latency[tps]["p50"] = []
                    latency[tps]["p99"] = []
                latency[tps]["p50"].append(p50)
                latency[tps]["p99"].append(p99)
                tlevel_run_dir = os.path.dirname(dpath)
                tdir_name = os.path.basename(tlevel_run_dir)
                outfig_dir = os.path.join(args.out_stats, args.app, str(tps))
                os.makedirs(outfig_dir, exist_ok=True)
                outfig = os.path.join(outfig_dir, f"{tdir_name}.pdf")
                fig = plt.figure()
                plt.plot(e2e_lat)
                plt.savefig(outfig, bbox_inches='tight')
                plt.close(fig)
                print(f"{dpath} p50: {p50} ms, p99: {p99} ms")
                all_data.append(e2e_lat)
        print()
        if all_data:
            all_data_cat = np.concatenate(all_data)
            all_p50 = np.quantile(all_data_cat, 0.5)
            all_p99 = np.quantile(all_data_cat, 0.99)
            print(f"{tps} p50: {all_p50} ms, p99: {all_p99} ms")
            if tps not in all_stats:
                all_stats[tps] = {}
            all_stats[tps]["p50"] = p50
            all_stats[tps]["p99"] = p99
            p50Mean = mean(latency[tps]["p50"])
            p50Std = stdev(latency[tps]["p50"])
            p99Mean = mean(latency[tps]["p99"])
            p99Std = stdev(latency[tps]["p99"])
            p50cv = p50Std/p50Mean
            p99cv = p99Std/p99Mean
            print(f"{tps} p50 mean: {p50Mean} ms, std: {p50Std}, cv: {p50cv}, p99 mean: {p99Mean}"
                  f"ms, std: {p99Std}, cv: {p99cv}")
        else:
            print(f"{tps} doesn't have data")
    mtime = int(os.stat(args.dir).st_mtime)
    all_stats_path = os.path.join(args.out_stats, f"{args.app}_{mtime}.pickle")
    splitlat_stats_path = os.path.join(args.out_stats, f"{args.app}_split_{mtime}.pickle")
    with open(all_stats_path, "wb") as f:
        pickle.dump(all_stats, f)
    with open(splitlat_stats_path, "wb") as f:
        pickle.dump(latency, f)


if __name__ == '__main__':
    main()
