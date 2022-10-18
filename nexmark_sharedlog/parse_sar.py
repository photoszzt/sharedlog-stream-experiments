import argparse
import os
from pathlib import Path
import subprocess as sp
import json
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, type=str)
    parser.add_argument("--out_dir", required=True, type=str)
    parser.add_argument("--target_dir", required=True, type=str)
    args = parser.parse_args()
    dirs_dict = {}
    for root, dirs, _ in os.walk(args.dir):
        for d in dirs:
            if "epoch" in d or "eo" in d:
                tps_per_work = int(d.split("_")[0][:-3])
                dirs_dict[tps_per_work] = os.path.join(root, d, args.target_dir)
    for tps_per_work, dirpath in dirs_dict.items():
        cpu_stats = {}
        # net_stats = {}
        for fname in Path(dirpath).glob("**/sar_st"):
            d = os.path.basename(os.path.dirname(fname))
            p = sp.run(['sadf', "-j", "-t", fname, "--", "-P", "ALL"], capture_output=True)
            cpu_str = p.stdout.decode()
            cpu = json.loads(cpu_str)
            cpu_st = []
            for st in cpu['sysstat']['hosts'][0]['statistics']:
                cpu_util = 0
                for cpu_ut in st['cpu-load'][1:]:
                    cpu_util += cpu_ut['user'] + cpu_ut['system']
                cpu_st.append(cpu_util)
            cpu_stats[d] = cpu_st
            # p = sp.run(['sadf', "-j", "-t", fname, "--", "-n", "DEV", "--iface=ens5"], capture_output=True)
            # net_str = p.stdout.decode()
            # net = json.loads(net_str)
            # print(net_str)

        mtime = int(os.stat(dirpath).st_mtime)
        cpu_out = os.path.join(args.out_dir, f"{tps_per_work}_cpu_{mtime}.json")
        os.makedirs(os.path.join(args.out_dir, "cpu_fig"), exist_ok=True)
        cpu_fig = os.path.join(args.out_dir, "cpu_fig", f"{tps_per_work}_cpu_{mtime}.png")
        with open(cpu_out, "w") as f:
            json.dump(cpu_stats, f)
        plt.figure()
        for d, st in cpu_stats.items():
            plt.plot(st, label=d)
        plt.legend(loc=(0, 1.1), ncol=2)
        plt.savefig(cpu_fig, bbox_inches='tight')


if __name__ == '__main__':
    main()
