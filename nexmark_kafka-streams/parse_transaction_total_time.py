import argparse
import os
import numpy as np

stats_name = {
    "blocked-time-ns-total",
    "txn-begin-time-ns-total",
    "txn-send-offsets-time-ns-total",
    "txn-commit-time-ns-total",
    "txn-abort-time-ns-total",
    "committed-time-ns-total",
    "commit-sync-time-ns-total",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True)
    args = parser.parse_args()
    stats = {}
    for root, dirs, files in os.walk(args.dir):
        for fname in files:
            if "kstreams-test_nexmark" in fname and "stdout" in fname and fname not in stats:
                fpath = os.path.join(root, fname)
                stats[fname] = {}
                stats[fname]["timeline"] = []
                with open(fpath, "r") as f:
                    for line in f:
                        if "emit metrics at" in line:
                            t = int(line.strip().split(" ")[3])
                            stats[fname]["timeline"].append(t)
                        elif "metrics" in line and ";" in line:
                            l = line.strip().split(";")
                            sp = l[0].split(" ")
                            name = sp[1]
                            if name in stats_name:
                                latStr = l[2].split(":")[1]
                                if "NaN" not in latStr:
                                    if name not in stats[fname]:
                                        stats[fname][name] = []
                                    stats[fname][name].append(float(latStr))
    time_interval = {}
    for fname, stat in stats.items():
        time_interval[fname] = {}
        for name, data in stat.items():
            if name not in time_interval[fname]:
                time_interval[fname][name] = []
            last_data_time = 0
            for i in range(len(stat["timeline"])):
                dur_data = data[i] - last_data_time
                time_interval[fname][name].append(dur_data)
                last_data_time = data[i]
    for fname, stat in time_interval.items():
        print(fname)
        timeline = np.array(stat["timeline"])
        for sn in stats_name:
            if sn in stat:
                data = stat[sn]
                percent = data / timeline * 100
                print(f"{sn}: {percent}")
        print()



                
if __name__ == '__main__':
    main()
