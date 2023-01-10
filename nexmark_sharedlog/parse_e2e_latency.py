import argparse
import os
import gzip
import json
import numpy as np
import matplotlib.pyplot as plt
from statistics import mean, stdev

stages = {
    "q1": "query1",
    "q2": "query2",
    "q3": "q3JoinTable",
    "q4": "q4Avg",
    "q5": "q5maxbid",
    "q6": "q6Avg",
    "q7": "q7JoinMaxBid",
    "q8": "q8JoinStream",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, help='dir to parse', required=True)
    parser.add_argument('--out_stats', type=str, required=True)
    parser.add_argument('--app', type=str, required=True)
    parser.add_argument('--target', type=str, required=True)
    args = parser.parse_args()
    dirs_dict = {}
    latency = {}
    all_stats = {}
    for root, dirs, _ in os.walk(args.dir):
        for d in dirs:
            if args.target in d:
                try:
                    tps_per_work = int(d.split("_")[0][:-3])
                    if tps_per_work not in dirs_dict:
                        dirs_dict[tps_per_work] = []
                    dirs_dict[tps_per_work].append(os.path.join(root, d))
                except Exception:
                    pass
    print(dirs_dict)
    os.makedirs(args.out_stats, exist_ok=True)
    prefix = stages[args.app]
    tpss = sorted(dirs_dict.keys())
    for tps in tpss:
        dirpaths = dirs_dict[tps]
        all_data = []
        for dpath in dirpaths:
            e2e_latency = []
            stats_dir = os.path.join(dpath, "stats")
            for root, dirs, files in os.walk(stats_dir):
                for fname in files:
                    if "gz" in fname and prefix in fname:
                        fpath = os.path.join(root, fname)
                        with gzip.open(fpath, 'rb') as f:
                            st = json.load(f)
                            found = False
                            for key, value in st['Latencies'].items():
                                if 'eventTimeLatency' in key:
                                    if st['Latencies'][key] is not None:
                                        e2e_latency.append(st['Latencies'][key])
                                        found = True
                            if not found:
                                print(f"{fpath} event time latency is empty")
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

                # tlevel_run_dir = os.path.dirname(dpath)
                # tdir_name = os.path.basename(tlevel_run_dir)
                # outfig_dir = os.path.join(args.out_stats, args.app, str(tps))
                # os.makedirs(outfig_dir, exist_ok=True)
                # outfig = os.path.join(outfig_dir, f"{tdir_name}.pdf")
                # fig = plt.figure()
                # plt.plot(e2e_lat)
                # plt.savefig(outfig, bbox_inches='tight')
                # plt.close(fig)

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
            all_stats[tps]["p50"] = all_p50
            all_stats[tps]["p99"] = all_p99
            p50Mean = mean(latency[tps]["p50"])
            p50std = 0
            if len(latency[tps]["p50"]) >= 2:
                p50std = stdev(latency[tps]["p50"])
            p99Mean = mean(latency[tps]["p99"])
            p99Std = 0
            if len(latency[tps]["p50"]) >= 2:
                p99Std = stdev(latency[tps]["p99"])
            p50cv = p50std/p50Mean
            p99cv = p99Std/p99Mean
            print(f"{tps} p50 mean: {p50Mean} ms, std: {p50std}, cv: {p50cv}, p99 mean: {p99Mean}"
                  f"ms, std: {p99Std}, cv: {p99cv}")
        else:
            print(f"{tps} doesn't have data")
    all_stats_path = os.path.join(args.out_stats, f"{args.app}.json")
    with open(all_stats_path, "w") as f:
        json.dump(all_stats, f)


if __name__ == '__main__':
    main()
