import os
import numpy as np
from pathlib import Path
from statistics import quantiles, mean, stdev
import subprocess as sp

dirs = {
    "q1": "../q1_boki/4src_2/180s_0swarm_100ms_src10ms/",
    "q2": "../q2_boki/4src_2/180s_0swarm_100ms_src10ms/",
    "q3": "../q3_boki/mem/4src_2/180s_0swarm_100ms_src100ms/",
    "q4": "../q4_boki/4src_2/180s_0swarm_100ms_src100ms/",
    "q5": "../q5_boki/mem/4src_2/180s_0swarm_100ms_src100ms/",
    "q6": "../q6_boki/4src_2/180s_0swarm_100ms_src100ms/",
    "q7": "../q7_boki/mem/4src_2/180s_0swarm_100ms_src100ms_comm100ms/",
    "q8": "../q8_boki/mem/4src_2/180s_0swarm_100ms_src100ms/",
}

SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))


def gen_path():
    for app, dir in dirs.items():
        for i in range(0, 3):
            path = os.path.join(SCRIPT_DIR, dir, str(i))
            if os.path.exists(path):
                yield app, path


def parse_e2eChkptElapsed(fname, tps_stat):
    p = sp.run(['rg', 'e2eChkptElapsed', fname], stdout=sp.PIPE, stderr=sp.PIPE, encoding='utf-8')
    for line in p.stdout.splitlines():
        if "e2eChkptElapsed" in line:
            l = line.strip().split(": ")[1]
            data = l.split(", ")
            if "data" in l:
                d = data[1].split('=')[1].strip("[]{}").split(" ")
                d = [int(i) for i in d]
                tps_stat['raw_data'].append(d)
            else:
                p50 = int(data[1].split('=')[1])
                p99 = int(data[3].split('=')[1])
                tps_stat['p50'].append(p50)
                tps_stat['p99'].append(p99)


def parse_files(dirs_dict):
    stat = {}
    for tps_per_work, dirpaths in dirs_dict.items():
        stat[tps_per_work] = {'raw_data': [], 'p50': [], 'p99': []}
        visited_files = set()
        for dirpath in dirpaths:
            for fname in Path(dirpath).glob("**/*.stderr"):
                basename = os.path.basename(fname)
                if basename in visited_files:
                    continue
                visited_files.add(basename)
                stage = basename.split("_")[0]
                if stage == 'chkptmngr':
                    parse_e2eChkptElapsed(fname, stat[tps_per_work])
    return stat


def main():
    all_app_stat = {}
    for app, p in gen_path():
        if app not in all_app_stat:
            all_app_stat[app] = {}
        dirs_dict = {}
        for root, dirs, _ in os.walk(p):
            for d in dirs:
                if "epoch" in d or "align_chkpt" in d:
                    try:
                        tps_per_work = int(d.split("_")[0][:-3])
                        if tps_per_work not in dirs_dict:
                            dirs_dict[tps_per_work] = []
                        dirs_dict[tps_per_work].append(os.path.join(root, d, "logs"))
                    except Exception:
                        pass
        stat = parse_files(dirs_dict)
        for tps, st in stat.items():
            if len(st['p50']) != 0:
                if tps not in all_app_stat:
                    all_app_stat[app][tps] = {'raw_data': [], 'p50': [], 'p99': []}
                if len(st['p50']) != 0:
                    all_app_stat[app][tps]['p50'].append(st['p50'])
                    all_app_stat[app][tps]['p99'].append(st['p99'])
                if len(st['raw_data']) != 0:
                    all_data_arr = np.concatenate(st['raw_data'])
                    all_app_stat[app][tps]['raw_data'].append(all_data_arr)
    for app, app_st_arr in all_app_stat.items():
        all_tps = sorted(app_st_arr.keys())
        for tps in all_tps:
            st = app_st_arr[tps]
            all_data_arr = np.concatenate(st['raw_data'])
            all_p50 = np.concatenate(st['p50'])
            all_p99 = np.concatenate(st['p99'])
            p50 = np.quantile(all_data_arr, 0.5)
            p99 = np.quantile(all_data_arr, 0.99)
            mean_p50 = mean(all_p50)
            mean_p99 = mean(all_p99)
            print(f'{app}, {tps}, m_p50: {mean_p50}, m_p99: {mean_p99}, p50_rest: {p50}, p99_rest: {p99}')


if __name__ == '__main__':
    main()
