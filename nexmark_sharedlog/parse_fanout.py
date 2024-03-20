import argparse
import os
import gzip
import json
import numpy as np
import pickle
from statistics import mean, stdev


def get_dirs_dict(target, input_dir):
    dirs_dict = {}
    for root, dirs, _ in os.walk(input_dir):
        for d in dirs:
            if target in d:
                try:
                    splits = d.split("_")
                    fanout = int(splits[-1])
                    tps_per_work = int(splits[0][:-3])
                    k = (tps_per_work, fanout)
                    if k not in dirs_dict:
                        dirs_dict[k] = []
                    dirs_dict[k].append(os.path.join(root, d))
                except Exception:
                    pass
    return dirs_dict


def get_data_in_dir(dpath, all_data, latency, k):
    e2e_latency = []
    prefix = "fanout"
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
        if k not in latency:
            latency[k] = {}
            latency[k]["p50"] = []
            latency[k]["p99"] = []
        latency[k]["p50"].append(p50)
        latency[k]["p99"].append(p99)
        print(f"{dpath} p50: {p50} ms, p99: {p99} ms")
        all_data.append(e2e_lat)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, help='dir to parse', required=True)
    parser.add_argument('--out_stats', type=str, required=True)
    parser.add_argument('--target', type=str, required=True)
    args = parser.parse_args()
    dirs_dict = get_dirs_dict(args.target, args.dir)
    os.makedirs(args.out_stats, exist_ok=True)
    tpss = sorted(dirs_dict.keys())
    latency = {}
    all_stats = {}
    for (tps, fanout) in tpss:
        dirpaths = dirs_dict[(tps, fanout)]
        all_data = []
        k = (tps, fanout)
        for dpath in dirpaths:
            get_data_in_dir(dpath, all_data, latency, k)
        print()
        if all_data:
            all_data_cat = np.concatenate(all_data)
            all_p50 = np.quantile(all_data_cat, 0.5)
            all_p99 = np.quantile(all_data_cat, 0.99)
            print(f"{tps},{fanout} p50: {all_p50} ms, p99: {all_p99} ms")
            if tps not in all_stats:
                all_stats[k] = {}
            all_stats[k]["p50"] = all_p50
            all_stats[k]["p99"] = all_p99
            p50Mean = mean(latency[k]["p50"])
            p50std = 0
            if len(latency[k]["p50"]) >= 2:
                p50std = stdev(latency[k]["p50"])
            p99Mean = mean(latency[k]["p99"])
            p99Std = 0
            if len(latency[k]["p50"]) >= 2:
                p99Std = stdev(latency[k]["p99"])
            p50cv = p50std/p50Mean
            p99cv = p99Std/p99Mean
            print(f"{k} p50 mean: {p50Mean} ms, std: {p50std}, cv: {p50cv}, p99 mean: {p99Mean}"
                  f"ms, std: {p99Std}, cv: {p99cv}")
        else:
            print(f"{k} doesn't have data")
    all_stats_path = os.path.join(args.out_stats, f"fanout_{args.target}.pickle")
    print(all_stats_path)
    with open(all_stats_path, "wb") as f:
        pickle.dump(all_stats, f, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    main()
