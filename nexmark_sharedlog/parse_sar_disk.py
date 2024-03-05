import argparse
import os
from pathlib import Path
import subprocess as sp
import json
import matplotlib.pyplot as plt
import numpy as np

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, type=str)
    parser.add_argument("--out_dir", required=True, type=str)
    args = parser.parse_args()
    dirs_dict = {}
    for root, dirs, _ in os.walk(args.dir):
        for d in dirs:
            if "epoch" in d or "eo" in d or "align_chkpt" in d:
                try:
                    tps_per_work = d.split("_")[0][:-3]
                    if 'ex-' not in tps_per_work:
                        tps_per_work = int(tps_per_work)
                    if tps_per_work not in dirs_dict:
                        dirs_dict[tps_per_work] = []
                    dirs_dict[tps_per_work].append(os.path.join(root, d))
                except Exception:
                    pass
    for tps_per_work, dirpaths in dirs_dict.items():
        for dirpath in dirpaths:
            logs_path = os.path.join(dirpath, "logs")

            storage_sar = os.path.join(dirpath, "storage_sar")
            pdir = os.path.basename(os.path.dirname(dirpath))
            out_dir = os.path.join(args.out_dir, pdir)
            out_storage_dir = os.path.join(out_dir, "storage")
            os.makedirs(out_storage_dir, exist_ok=True)

            for dirname in Path(storage_sar).glob("*.compute.internal"):
                base_dirname = os.path.basename(dirname)
                parent_dir = os.path.dirname(dirname)
                dev_info = os.path.join(parent_dir, f"{base_dirname}_dev")
                dev_name = ""
                with open(dev_info, "r") as f:
                    for line in f:
                        if "nvme1n1" in line:
                            l = line.strip().split(" ") 
                            major = l[4].strip(",")
                            minor = l[5]
                            dev_name = f"dev{major}-{minor}"
                if dev_name == "":
                    raise Exception("doesn't find nvme1n1 in _dev file")

                tps_storage_out = os.path.join(out_storage_dir, str(tps_per_work))
                os.makedirs(tps_storage_out, exist_ok=True)
                disk_cmd = ["sadf", "-j", "-t", os.path.join(dirname, "sar_st"), 
                        "--", "-d", f"--dev={dev_name}"]
                p = sp.run(disk_cmd, stdout=sp.PIPE, stderr=sp.PIPE)
                disk_str = p.stdout.decode()
                disk_stat = json.loads(disk_str)
                disk_json_out = os.path.join(tps_storage_out, f"{base_dirname}_storage_disk.json")
                with open(disk_json_out, "wb") as f:
                    f.write(p.stdout)
                keys = ['tps', 'wkB', 'rkB']
                data = {}
                for k in keys:
                    data[k] = []
                stat = {}
                for st in disk_stat['sysstat']['hosts'][0]['statistics']:
                    for k in keys:
                        data[k].append(st['disk'][0][k])
                for k in keys:
                    p50 = np.quantile(data[k], 0.5)
                    p99 = np.quantile(data[k], 0.99)
                    if k not in stat:
                        stat[k] = {}
                    stat[k]['p50'] = p50
                    stat[k]['p99'] = p50
                stat_out = os.path.join(tps_storage_out, f"{base_dirname}_storage_disk_stat.json")
                with open(stat_out, "w") as f:
                    json.dump(stat, f)


if __name__ == '__main__':
    main()
