import argparse
import os
from pathlib import Path
import subprocess as sp


def main():
    parser = argparse.ArgumentParser(description='Parse stage time')
    parser.add_argument('--dir', type=str, help='dir to parse', required=True)
    parser.add_argument('--out_dir', type=str, help='output_dir', required=True)
    args = parser.parse_args()
    dirs_arr = []

    for root, dirs, _ in os.walk(args.dir):
        for d in dirs:
            if "epoch" in d or "align_chkpt" or "2pc" in d:
                try:
                    tps_per_work = int(d.split("_")[0][:-3])
                    dirs_arr.append(os.path.join(root, d))
                except Exception:
                    pass
    print(dirs_arr)
    for dirpath in dirs_arr:
        logs_path = os.path.join(dirpath, "logs")
        source_paths = set()
        for source_file in Path(logs_path).glob("**/source*.stderr"):
            size = os.stat(source_file).st_size
            if size > 8192:
                d = os.path.dirname(os.path.dirname(source_file))
                d = os.path.basename(os.path.dirname(d))
                source_paths.add(d)

        storage_sar = os.path.join(dirpath, "storage_sar")
        engine_sar = os.path.join(dirpath, "engine_sar")

        tps_storage_out = os.path.join(args.out_dir, dirpath, "storage")
        os.makedirs(tps_storage_out, exist_ok=True)
        tps_engine_out = os.path.join(args.out_dir, dirpath, "engine")
        os.makedirs(tps_engine_out, exist_ok=True)

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

            cpu_cmd = ["sadf", "-g", os.path.join(dirname, "sar_st"), 
                "--", "-P", "ALL"]
            p = sp.run(cpu_cmd, stdout=sp.PIPE, stderr=sp.PIPE)
            storage_cpu_out = os.path.join(tps_storage_out, f"{base_dirname}_storage_cpu.svg")
            with open(storage_cpu_out, "wb") as f:
                f.write(p.stdout)
            # print(" ".join(cpu_cmd))


            disk_cmd = ["sadf", "-g", os.path.join(dirname, "sar_st"), 
                    "--", "-d", f"--dev={dev_name}"]
            p = sp.run(disk_cmd, stdout=sp.PIPE, stderr=sp.PIPE)
            storage_disk_out = os.path.join(tps_storage_out, f"{base_dirname}_storage_disk.svg")
            with open(storage_disk_out, "wb") as f:
                f.write(p.stdout)
            # print(" ".join(disk_cmd))

            net_cmd = ["sadf", "-g", os.path.join(dirname, "sar_st"), 
                "--", "-n", "DEV", "--iface=ens5"]
            storage_net_out = os.path.join(tps_storage_out, f"{base_dirname}_storage_net.svg")
            p = sp.run(net_cmd, stdout=sp.PIPE, stderr=sp.PIPE)
            with open(storage_net_out, "wb") as f:
                f.write(p.stdout)
            # print(" ".join(net_cmd))

            mem_cmd = ["sadf", "-g", os.path.join(dirname, "sar_st"), 
                "--", "-r"]
            storage_mem_out = os.path.join(tps_storage_out, f"{base_dirname}_storage_mem.svg")
            p = sp.run(mem_cmd, stdout=sp.PIPE, stderr=sp.PIPE)
            with open(storage_mem_out, "wb") as f:
                f.write(p.stdout)
            # print(" ".join(mem_cmd))

        for dirname in Path(engine_sar).glob("*.compute.internal"):
            base_dirname = os.path.basename(dirname)
            if base_dirname in source_paths:
                name = "sourcegen"
            else:
                name = "app"

            cpu_cmd = ["sadf", "-g", os.path.join(dirname, "sar_st"), 
                "--", "-P", "ALL"]
            c_cpu_out = os.path.join(tps_engine_out, f"{base_dirname}_{name}_cpu.svg")
            p = sp.run(cpu_cmd, stdout=sp.PIPE, stderr=sp.PIPE)
            with open(c_cpu_out, "wb") as f:
                f.write(p.stdout)
            # print(" ".join(cpu_cmd))

            net_cmd = ["sadf", "-g", os.path.join(dirname, "sar_st"), 
                "--", "-n", "DEV", "--iface=ens5"]
            c_net_out = os.path.join(tps_engine_out, f"{base_dirname}_{name}_net.svg")
            p = sp.run(net_cmd, stdout=sp.PIPE, stderr=sp.PIPE)
            with open(c_net_out, "wb") as f:
                f.write(p.stdout)
            # print(" ".join(net_cmd))

            mem_cmd = ["sadf", "-g", os.path.join(dirname, "sar_st"), 
                "--", "-r"]
            c_mem_out = os.path.join(tps_engine_out, f"{base_dirname}_{name}_mem.svg")
            p = sp.run(mem_cmd, stdout=sp.PIPE, stderr=sp.PIPE)
            with open(c_mem_out, "wb") as f:
                f.write(p.stdout)
            # print(" ".join(mem_cmd))


if __name__ == '__main__':
    main()
