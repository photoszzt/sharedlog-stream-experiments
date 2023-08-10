import argparse
import os
from pathlib import Path
import subprocess as sp
import json
import matplotlib.pyplot as plt


def parse_dir(sar_dir, top_dir, tps_per_work, source_paths):
    net_stats = {}
    max_rx = 0.0
    max_tx = 0.0
    max_rw = 0.0
    for dirname in Path(sar_dir).glob("*.compute.internal"):
        d = os.path.basename(dirname)
        if d not in source_paths:
            path = os.path.join(dirname, "sar_st")
            print(path)
            p = sp.run(['sadf', "-j", path, "--", "-n", "DEV", "--iface=ens5"],
                        capture_output=True)
            net_str = p.stdout.decode()
            net = json.loads(net_str)
            rx_arr = []
            tx_arr = []
            rw_arr = []
            for st in net['sysstat']['hosts'][0]['statistics']:
                rx = float(st['network']['net-dev'][0]['rxkB']) / 1024
                tx = float(st['network']['net-dev'][0]['txkB']) / 1024
                rx_arr.append(rx)
                tx_arr.append(tx)
                rw_arr.append(rx+tx)
            cur_max_rx = max(rx_arr)
            cur_max_tx = max(tx_arr)
            cur_max_rw = max(rw_arr)
            max_rx = max(max_rx, cur_max_rx)
            max_tx = max(max_tx, cur_max_tx)
            max_rw = max(max_rw, cur_max_rw)
            print(f'{d}, max rx(MiB): {cur_max_rx}, max tx(MiB): {cur_max_tx}, max sum(MiB): {cur_max_rw}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, type=str)
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
            # storage_sar = os.path.join(dirpath, "storage_sar")
            pdir = os.path.basename(os.path.dirname(dirpath))
            # out_dir = os.path.join(args.out_dir, pdir)
            # out_engine_dir = os.path.join(out_dir, "engine")
            # out_storage_dir = os.path.join(out_dir, "storage")
            # os.makedirs(out_engine_dir, exist_ok=True)
            # os.makedirs(out_storage_dir, exist_ok=True)

            top_dir = os.path.basename(os.path.dirname(dirpath))
            print(top_dir)

            parse_dir(engine_sar, top_dir, tps_per_work, source_paths)
            # parse_dir(storage_sar, out_storage_dir, top_dir, tps_per_work, set())


if __name__ == '__main__':
    main()
