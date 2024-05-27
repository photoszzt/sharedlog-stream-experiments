import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import subprocess
import sys
import os
import numpy as np
from string import ascii_lowercase

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from fig_const import markers, colors, headers

syss = [
    "./q38_rerun/50ms/epoch/q1-180s-0swarm-50ms-src10ms",
    "./q38_rerun/50ms/epoch/q2-180s-0swarm-50ms-src10ms",
    "./q38_rerun/50ms/epoch/q3-180s-0swarm-50ms-src50ms",
    "./q38_rerun/50ms/epoch/q4-180s-0swarm-50ms-src50ms",
    "./q38_rerun/50ms/epoch/q5-180s-0swarm-50ms-src50ms",
    "./q38_rerun/50ms/epoch/q6-180s-0swarm-50ms-src50ms",
    "./q38_rerun/50ms/epoch/q7-180s-0swarm-50ms-src50ms",
    "./q38_rerun/50ms/epoch/q8-180s-0swarm-50ms-src50ms",
]

remote_2pc = [
    "./q38_rerun/50ms/remote_2pc/q1-180s-0swarm-50ms-src10ms",
    "./q38_rerun/50ms/remote_2pc/q2-180s-0swarm-50ms-src10ms",
    "./q38_rerun/50ms/remote_2pc/q3-180s-0swarm-50ms-src50ms",
    "./q38_rerun/50ms/remote_2pc/q4-180s-0swarm-50ms-src50ms",
    "./q38_rerun/50ms/remote_2pc/q5-180s-0swarm-50ms-src50ms",
    "./q38_rerun/50ms/remote_2pc/q6-180s-0swarm-50ms-src50ms",
    "./q38_rerun/50ms/remote_2pc/q7-180s-0swarm-50ms-src50ms",
    "./q38_rerun/50ms/remote_2pc/q8-180s-0swarm-50ms-src50ms",
]

throughputs = [
    [4000, 16000, 32000, 48000, 64000, 80000, 88000],
    [4000, 16000, 32000, 48000, 64000, 80000, 88000],
    [8000, 16000, 32000, 48000, 64000, 80000, 96000, 112000, 128000],
    [250, 500, 750, 1000, 1250, 1500],
    [1000, 8000, 16000, 24000, 32000, 40000, 48000, 56000, 64000],
    # [1000, 8000, 16000, 24000, 32000, 40000, 48000, 56000],
    [250, 500, 750, 1000, 1250, 1500],
    [4000, 8000, 12000, 16000, 20000, 24000, 28000, 32000, 36000, 40000],
    [4000, 8000, 12000, 16000, 20000, 24000, 28000, 32000, 36000],
]

def load(system, experiment):
    rows = subprocess.run(["./latency", "query", system[experiment]], stdout=subprocess.PIPE)
    rows = rows.stdout.decode('utf-8').strip().split('\n')
    rows = [row for row in csv.DictReader(rows, fieldnames=headers) 
            if (row['del'] == 'eo' or row['del'] == '2pc' or row['del'] == 'align_chkpt' or row['del'] == 'remote_2pc') and int(row['tps']) in throughputs[experiment]]
    rows.sort(key=lambda row: int(row['tps']))
    return rows

if __name__ == "__main__":
    fig, axs = plt.subplots(4, 4, figsize=(24, 12), layout='constrained')
    handles = None
    letters=[f'({i})' for i in ascii_lowercase]
    for experiment in range(0, len(syss)):
        sys = load(syss, experiment)
        r2pc = load(remote_2pc, experiment)

        sys_in_per_worker_tp = [int(row['tps']) for row in sys]
        remote2pc_in_per_worker_tp = [int(row['tps']) for row in r2pc]

        sys_in_tp = [i*4 for i in sys_in_per_worker_tp]
        r2pc_in_tp = [i*4 for i in remote2pc_in_per_worker_tp]

        sys_p50 = [int(row['p50']) for row in sys]
        sys_p99 = [int(row['p99']) for row in sys]
        r2pc_p50 = [int(row['p50']) for row in r2pc]
        r2pc_p99 = [int(row['p99']) for row in r2pc]

        print('Q' + str(experiment + 1))
        print(f"sys tp: {sys_in_tp}") 
        print(f"sys p50: {sys_p50}")
        print(f"sys p99: {sys_p99}")
        print(f"remote_2pc p50: {r2pc_p50}")
        print(f"remote_2pc p99: {r2pc_p99}")
        marksize=14

        r = (experiment // 4) * 2
        c = experiment % 4
        ax1 = axs[r][c]
        ax2 = axs[r+1][c]
        l1, = ax1.plot(sys_in_tp, sys_p50, label='Impeller p50',  marker=markers[0],color=colors[0], markersize=marksize)
        l3, = ax2.plot(sys_in_tp, sys_p99, label='Impeller p99', ls='--', marker=markers[0], color=colors[0], markersize=marksize)
        l7, = ax1.plot(r2pc_in_tp, r2pc_p50, label='2pc on Impeller p50',  marker=markers[3], color=colors[3], markersize=marksize)
        l8, = ax2.plot(r2pc_in_tp, r2pc_p99, label='2pc on Impeller p99',  ls='--', marker=markers[3],color=colors[3], markersize=marksize)
        lines = [l1, l3, l7, l8]
        for l in lines:
            l.set_linewidth(3)

        # ax1.set_xlabel('input throughput(events/s)', fontsize=16)
        # ax1.set_ylabel('event time latency(ms)', fontsize=16)
        if experiment == 7:
            handles = [l1, l3, l7, l8]
        ax1.set_title(f'{letters[experiment]} Query{experiment+1}', fontsize=18)
        ax1.tick_params(labelsize=18)
        ax1.xaxis.set_major_formatter(ticker.EngFormatter())
        ax2.tick_params(labelsize=18)
        ax2.xaxis.set_major_formatter(ticker.EngFormatter())

        if experiment < 2:
            ax1.set_ylim([0, 60])
            ax2.set_ylim([0, 60])
        else:
            ax1.set_ylim([0, 1000])
            ax2.set_ylim([0, 1000])

        # plt.title('Q' + str(experiment + 1))
    fig.legend(ncol=5, handles=handles, fontsize=18, loc='upper center', bbox_to_anchor=(0.5, 1.10))
    fig.supxlabel('Input throughput(events/s)', fontsize=20)
    fig.supylabel('Event time latency(ms)', fontsize=20)
    plt.savefig('q1-8_50ms.pdf', bbox_inches='tight')
