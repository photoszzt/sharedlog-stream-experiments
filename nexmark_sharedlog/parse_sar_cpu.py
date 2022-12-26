import argparse
import os
from pathlib import Path
import subprocess as sp
import json
import matplotlib.pyplot as plt


def parse_dir(sar_dir, sar_out_dir, top_dir, tps_per_work, source_paths):
    cpu_stats = {}
    for dirname in Path(sar_dir).glob("*.compute.internal"):
        d = os.path.basename(dirname)
        p = sp.run(['sadf', "-j", "-t", os.path.join(dirname, "sar_st"), "--", "-P", "ALL"],
                    capture_output=True)
        cpu_str = p.stdout.decode()
        cpu = json.loads(cpu_str)
        cpu_st = []
        for st in cpu['sysstat']['hosts'][0]['statistics']:
            cpu_util = 0
            for cpu_ut in st['cpu-load'][1:]:
                cpu_util += cpu_ut['user'] + cpu_ut['system']
            cpu_st.append(cpu_util)
        cpu_stats[d] = cpu_st

    cpu_out = os.path.join(sar_out_dir, f"{tps_per_work}_cpu_{top_dir}.json")
    os.makedirs(os.path.join(sar_out_dir, "cpu_fig"), exist_ok=True)
    cpu_fig = os.path.join(sar_out_dir, "cpu_fig", f"{tps_per_work}_cpu_{top_dir}.pdf")
    with open(cpu_out, "w") as f:
        json.dump(cpu_stats, f)
    if source_paths:
        sourcegen_cpu_fig = os.path.join(sar_out_dir, "cpu_fig", 
                f"{tps_per_work}_cpu_{top_dir}_sourcegen.pdf")
        app_cpu_fig = os.path.join(sar_out_dir, "cpu_fig", 
                f"{tps_per_work}_cpu_{top_dir}_app.pdf")
        fig = plt.figure()
        for d, st in cpu_stats.items():
            if d in source_paths:
                plt.plot(st, label=d)
        plt.legend(loc=(0, 1.1), ncol=2)
        plt.savefig(sourcegen_cpu_fig, bbox_inches='tight')
        plt.close(fig)

        fig = plt.figure()
        for d, st in cpu_stats.items():
            if d not in source_paths:
                plt.plot(st, label=d)
        plt.legend(loc=(0, 1.1), ncol=2)
        plt.savefig(app_cpu_fig, bbox_inches='tight')
        plt.close(fig)
    else:
        fig = plt.figure()
        for d, st in cpu_stats.items():
            plt.plot(st, label=d)
        plt.legend(loc=(0, 1.1), ncol=2)
        plt.savefig(cpu_fig, bbox_inches='tight')
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, type=str)
    parser.add_argument("--out_dir", required=True, type=str)
    args = parser.parse_args()
    dirs_dict = {}
    for root, dirs, _ in os.walk(args.dir):
        for d in dirs:
            if "epoch" in d or "eo" in d:
                try:
                    tps_per_work = int(d.split("_")[0][:-3])
                    if tps_per_work not in dirs_dict:
                        dirs_dict[tps_per_work] = []
                    dirs_dict[tps_per_work].append(os.path.join(root, d))
                except Exception:
                    pass
    print(dirs_dict)
    for tps_per_work, dirpaths in dirs_dict.items():
        for dirpath in dirpaths:
            logs_path = os.path.join(dirpath, "logs")
            source_paths = set()
            for source_file in Path(logs_path).glob("**/source*.stderr"):
                size = os.stat(source_file).st_size
                if size > 4100:
                    d = os.path.dirname(os.path.dirname(source_file))
                    d = os.path.basename(os.path.dirname(d))
                    source_paths.add(d)

            engine_sar = os.path.join(dirpath, "engine_sar")
            storage_sar = os.path.join(dirpath, "storage_sar")
            pdir = os.path.basename(os.path.dirname(dirpath))
            out_dir = os.path.join(args.out_dir, pdir)
            out_engine_dir = os.path.join(out_dir, "engine")
            out_storage_dir = os.path.join(out_dir, "storage")
            os.makedirs(out_engine_dir, exist_ok=True)
            os.makedirs(out_storage_dir, exist_ok=True)

            top_dir = os.path.basename(os.path.dirname(dirpath))
            print(top_dir)

            parse_dir(engine_sar, out_engine_dir, top_dir, tps_per_work, source_paths)
            parse_dir(storage_sar, out_storage_dir, top_dir, tps_per_work, set())


if __name__ == '__main__':
    main()
