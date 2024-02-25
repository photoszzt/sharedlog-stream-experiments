import argparse
import os
from pathlib import Path
import subprocess as sp


def main():
    parser = argparse.ArgumentParser(description='Parse stage time')
    parser.add_argument('--dir', type=str, help='dir to parse', required=True)
    parser.add_argument('--out_dir', type=str, help='output_dir', required=True)
    args = parser.parse_args()
    dirs_dict = {}

    for root, dirs, _ in os.walk(args.dir):
        for d in dirs:
            if "eo" in d:
                try:
                    tps_per_work = int(d.split("_")[0][:-3])
                    if tps_per_work not in dirs_dict:
                        dirs_dict[tps_per_work] = []
                    dirs_dict[tps_per_work].append(os.path.join(root, d))
                except Exception:
                    pass
    for tps_per_work, dirpaths in dirs_dict.items():
        for dirpath in dirpaths:
            broker_sar = os.path.join(dirpath, "broker_sar")
            app_sar = os.path.join(dirpath, "app_sar")
            pdir = os.path.basename(os.path.dirname(dirpath))
            out_dir = os.path.join(args.out_dir, pdir)
            out_broker_dir = os.path.join(out_dir, "broker")
            out_app_dir = os.path.join(out_dir, "app")
            os.makedirs(out_broker_dir, exist_ok=True)
            os.makedirs(out_app_dir, exist_ok=True)

            for dirname in Path(broker_sar).glob("*.compute.internal"):
                base_dirname = os.path.basename(dirname)
                parent_dir = os.path.dirname(dirname)
                dev_info = os.path.join(parent_dir, f"{base_dirname}_dev")
                dev_name = ""
                if os.path.exists(dev_info):
                    with open(dev_info, "r") as f:
                        for line in f:
                            if "nvme1n1" in line:
                                l = line.strip().split(" ") 
                                major = l[4].strip(",")
                                minor = l[5]
                                dev_name = f"dev{major}-{minor}"
                    if dev_name == "":
                        raise Exception("doesn't find nvme1n1 in _dev file")

                tps_broker_out = os.path.join(out_broker_dir, str(tps_per_work))
                os.makedirs(tps_broker_out, exist_ok=True)


                if dev_name != "":
                    disk_cmd = ["sadf", "-g", os.path.join(dirname, "sar_st"), 
                        "--", "-d", f"--dev={dev_name}"]
                    disk_out = os.path.join(tps_broker_out, f"{base_dirname}_broker_disk.svg")
                    p = sp.run(disk_cmd, stdout=sp.PIPE, stderr=sp.PIPE)
                    with open(disk_out, "wb") as f:
                        f.write(p.stdout)
                    # print(" ".join(disk_cmd))
                # sp.run(disk_cmd, shell=True)
                net_cmd = ["sadf", "-g", os.path.join(dirname, "sar_st"), 
                    "--", "-n", "DEV", "--iface=ens5"]
                net_out = os.path.join(tps_broker_out, f"{base_dirname}_broker_net.svg")
                p = sp.run(net_cmd, stdout=sp.PIPE, stderr=sp.PIPE)
                with open(net_out, "wb") as f:
                    f.write(p.stdout)
                # print(" ".join(net_cmd))
                # sp.run(net_cmd, shell=True)

            for dirname in Path(app_sar).glob("*.compute.internal"):
                base_dirname = os.path.basename(dirname)
                tps_app_out = os.path.join(out_app_dir, str(tps_per_work))
                os.makedirs(tps_app_out, exist_ok=True)

                net_cmd = ["sadf", "-g", os.path.join(dirname, "sar_st"), 
                    "--", "-n", "DEV", "--iface=ens5"]
                net_out = os.path.join(tps_app_out, f"{base_dirname}_app_net.svg")]
                p = sp.run(net_cmd, stdout=sp.PIPE, stderr=sp.PIPE)
                with open(net_out, "wb") as f:
                    f.write(p.stdout)
                # print(" ".join(net_cmd))



if __name__ == '__main__':
    main()
