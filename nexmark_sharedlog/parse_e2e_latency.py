import argparse
import os
import gzip
import json
from statistics import quantiles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True)
    parser.add_argument('--prefix', required=True)
    args = parser.parse_args()
    prog_dirs = {}
    latency = {}
    absdir = os.path.abspath(args.dir)
    basedir = os.path.basename(absdir)
    if "tps" not in basedir:
        for root, dirs, files in os.walk(args.dir):
            for dname in dirs:
                if "tps" in dname:
                    dpath = os.path.join(root, dname)
                    tps = dname.split("_")[0][:-3]
                    prog_dirs[dpath] = int(tps)
    else:
        tps = basedir.split("_")[0][:-3]
        prog_dirs[absdir] = int(tps)
    for (dpath, tps) in prog_dirs.items():
        e2e_latency = []
        stats_dir = os.path.join(dpath, "stats")
        print(stats_dir)
        for root, dirs, files in os.walk(stats_dir):
            for fname in files:
                if "gz" in fname and args.prefix in fname:
                    fpath = os.path.join(root, fname)
                    with gzip.open(fpath, 'rb') as f:
                        st = json.load(f)
                        print(st.keys())
                        print(st['Latencies'].keys())
                        if st['Latencies']['eventTimeLatency']:
                            e2e_latency.extend(st['Latencies']['eventTimeLatency'])
                        else:
                            print(f"{fpath} event time latency is empty: {st['Latencies']['eventTimeLatency']}")
                    # with open(fpath, 'r') as f:
                    #     st = json.load(f)
                    #     e2e_latency.extend(st['Latencies']['eventTimeLatency'])
        if e2e_latency:
            quan = quantiles(e2e_latency, n=100)
            p50 = quan[49]
            p99 = quan[98]
            if tps not in latency:
                latency[tps] = {}
            latency[tps][dpath] = (p50, p99)
            # print(f"dpath {dpath} tps {tps} {args.prefix} p50: {p50} ms, p99: {p99} ms")
    for tps, stats in latency.items():
        print(f"tps {tps}")
        for dpath, stat in stats.items():
            print(f"{dpath} p50: {stat[0]} ms, p99: {stat[1]} ms")



if __name__ == '__main__':
    main()
