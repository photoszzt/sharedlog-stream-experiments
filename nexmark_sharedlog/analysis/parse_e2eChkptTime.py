import os
import numpy as np
from pathlib import Path
from statistics import quantiles, mean, stdev
import subprocess as sp
import argparse

dirs = {
    "q1": "../q1_boki/4src_3/180s_0swarm_100ms_src10ms/",
    "q2": "../q2_boki/4src_3/180s_0swarm_100ms_src10ms/",
    "q3": "../q3_boki/mem/4src_3/180s_0swarm_100ms_src100ms/",
    "q4": "../q4_boki/4src_3/180s_0swarm_100ms_src100ms/",
    "q5": "../q5_boki/mem/4src_3/180s_0swarm_100ms_src100ms/",
    "q6": "../q6_boki/4src_3/180s_0swarm_100ms_src100ms/",
    "q7": "../q7_boki/mem_nosync/4src_3/180s_0swarm_100ms_src100ms_comm100ms/",
    "q8": "../q8_boki/mem/4src_3/180s_0swarm_100ms_src100ms/",
}

SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))


def gen_path(app_str):
    if app_str != "":
        dir = dirs[app_str]
        for i in range(0, 6):
            path = os.path.join(SCRIPT_DIR, dir, str(i))
            if os.path.exists(path):
                yield app_str, path
    else:
        for app, dir in dirs.items():
            for i in range(0, 6):
                path = os.path.join(SCRIPT_DIR, dir, str(i))
                if os.path.exists(path):
                    yield app, path


def parse_stat(fname, tps_stat, stat_id):
    p = sp.run(['rg', stat_id, fname], stdout=sp.PIPE, stderr=sp.PIPE, encoding='utf-8')
    for line in p.stdout.splitlines():
        if stat_id in line:
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
        if tps_per_work not in stat:
            stat[tps_per_work] = {'raw_data': [], 'p50': [], 'p99': []}
        for dirpath in dirpaths:
            for fname in Path(dirpath).glob("**/*.stderr"):
                basename = os.path.basename(fname)
                stage = basename.split("_")[0]
                if stage == 'chkptmngr':
                    parse_stat(fname, stat[tps_per_work], "e2eChkptElapsed")
    return stat


def update_per_app_dir(p, dirs_dict):
    for root, dirs, _ in os.walk(p):
        for d in dirs:
            if ("epoch" in d or "align_chkpt" in d) and ("ex-" not in d):
                try:
                    tps_per_work = int(d.split("_")[0][:-3])
                    if tps_per_work not in dirs_dict:
                        dirs_dict[tps_per_work] = []
                    dirs_dict[tps_per_work].append(os.path.join(root, d, "logs"))
                except Exception:
                    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=str, help='app to parse', required=True)
    args = parser.parse_args()
    
    all_app_stat = {}
    dirs_dicts = {}
    for app, p in gen_path(args.app):
        if app not in all_app_stat:
            all_app_stat[app] = {}
        if app not in dirs_dicts:
            dirs_dicts[app] = {}
        update_per_app_dir(p, dirs_dicts[app])
    # for app, dirs_dict in dirs_dicts.items():
    #     print(app)
    #     for tps, dirs in dirs_dict.items():
    #         print(tps, dirs)
    for app, dirs_dict in dirs_dicts.items():
        stat = parse_files(dirs_dict)
        for tps, st in stat.items():
            if tps not in all_app_stat[app]:
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
            mean_p50 = -1
            mean_p99 = -1
            all_data_arr = np.concatenate(st['raw_data'])
            if len(st['p50']) != 0:
                all_p50 = np.concatenate(st['p50'])
                mean_p50 = mean(all_p50)
            if len(st['p99']) != 0:
                all_p99 = np.concatenate(st['p99'])
                mean_p99 = mean(all_p99)
            p50 = np.quantile(all_data_arr, 0.5)
            p99 = np.quantile(all_data_arr, 0.99)
            print(f'{app}, {tps}, m_p50: {mean_p50}, m_p99: {mean_p99}, p50_rest: {p50}, p99_rest: {p99}')


if __name__ == '__main__':
    main()
