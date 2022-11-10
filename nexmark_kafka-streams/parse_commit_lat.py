import argparse
import os
from pathlib import Path
from statistics import mean

stats_name = {
    "commit-latency-max",
    "commit-latency-avg",
    "batch-size-avg",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True)
    args = parser.parse_args()
    stats = {}
    dirs_dict = {}
    for root, dirs, _ in os.walk(args.dir):
        for d in dirs:
            if "eo" in d:
                tps_per_work = int(d.split("_")[0][:-3])
                if tps_per_work not in dirs_dict:
                    dirs_dict[tps_per_work] = []
                dirs_dict[tps_per_work].append(os.path.join(root, d, "logs"))
    print(dirs_dict)
    for tps_per_work, dirpaths in dirs_dict.items():
        stats[tps_per_work] = {}
        commit_num = {}
        for dirpath in dirpaths:
            for fname in Path(dirpath).glob("*nexmark*.stdout"):
                print(fname)
                with open(fname, "r") as f:
                    for line in f:
                        if "metrics" in line and ";" in line:
                            l = line.strip().split(";")
                            sp = l[0].split(" ")
                            name = sp[1]
                            if name == "commit-total" and sp[0] == "stream-thread-metrics":
                                latStr = l[2].split(":")[1]
                                if "NaN" not in latStr:
                                    commit_num[fname] = float(latStr)
                            if name in stats_name:
                                latStr = l[2].split(":")[1]
                                if "NaN" not in latStr:
                                    if name not in stats[tps_per_work]:
                                        stats[tps_per_work][name] = []
                                    stats[tps_per_work][name].append(float(latStr))
        commit_times = []
        for _, ct in commit_num.items():
            commit_times.append(ct)
        stats[tps_per_work]['commit-times'] = commit_times

    throughput = stats.keys()
    throughput = sorted(throughput)
    for st_name in stats_name:
        for tp in throughput:
            data_arr = stats[tp][st_name]
            m = mean(data_arr)
            print(f"{tp},{st_name},{m}")
        

if __name__ == '__main__':
    main()
