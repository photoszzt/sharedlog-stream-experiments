import argparse
import os
from pathlib import Path
from statistics import mean

stats_name = {
        "commit-latency-max",
        "commit-latency-avg",
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
                dirs_dict[tps_per_work] = os.path.join(root, d, "logs")
    for tps_per_work, dirpath in dirs_dict.items():
        stats[tps_per_work] = {}
        for fname in Path(dirpath).glob("*nexmark*.stdout"):
            with open(fname, "r") as f:
                for line in f:
                    if "metrics" in line and ";" in line:
                        l = line.strip().split(";")
                        sp = l[0].split(" ")
                        name = sp[1]
                        if name in stats_name:
                            latStr = l[2].split(":")[1]
                            if "NaN" not in latStr:
                                if name not in stats[tps_per_work]:
                                    stats[tps_per_work][name] = []
                                stats[tps_per_work][name].append(float(latStr))
    for tps_per_work, stat in stats.items():
        for st_name, data in stat.items():
            m = mean(data)
            print(f"{tps_per_work},{st_name},{m}")



if __name__ == '__main__':
    main()
