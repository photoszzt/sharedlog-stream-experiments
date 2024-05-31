import json
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import csv
import matplotlib.ticker as ticker

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from fig_const import markers, colors, headers

markFreq = [10, 20, 40, 100]
markIntr = [100, 50, 25, 10]

throughputs = {1: "32000", 2: "64000", 3: "64000", 4: "750", 5: "32000", 6: "500", 7: "12000", 8: "16000"}

allow_throughputs = [
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


def load(dpath, experiment):
    rows = subprocess.run(["./latency", "query", dpath], stdout=subprocess.PIPE)
    rows = rows.stdout.decode('utf-8').strip().split('\n')
    rows = [row for row in csv.DictReader(rows, fieldnames=headers) 
            if (row['del'] == 'eo' or row['del'] == '2pc' or row['del'] == 'align_chkpt' or row['del'] == 'remote_2pc') and int(row['tps']) in allow_throughputs[experiment]]
    rows.sort(key=lambda row: int(row['tps']))
    return rows


def get_varflush(markIntr, query):
    top_dir=f"q{query}_varflush"
    json_fname=f"q{query}.json"
    tp = throughputs[query]
    epoch_dir = f"{top_dir}/epoch"
    twopc_dir = f"{top_dir}/remote_2pc"
    epoch_p50 = []
    epoch_p99 = []
    twopc_p50 = []
    twopc_p99 = []
    for intr in markIntr:
        ep_fname = os.path.join(epoch_dir, f"{intr}ms", json_fname)
        if intr == 100:
            if query == 1 or query == 2:
                ep_dir = f"../fig10_fig11/pm_data/sys-boki/q{query}-180s-0swarm-100ms-src10ms2"
            else:
                ep_dir = f"../fig10_fig11/q38_rerun/impeller/q{query}-180s-0swarm-100ms-src100ms"
            epoch = load(ep_dir, query-1)
            for row in epoch:
                if row['tps'] == tp:
                    epoch_p50.append(int(row['p50']))
                    epoch_p99.append(int(row['p99']))
        elif os.path.exists(ep_fname):
            with open(ep_fname, "r") as f:
                data = json.load(f)
            if tp in data:
                epoch_p50.append(data[tp]["p50"])
                epoch_p99.append(data[tp]["p99"])

        fname = os.path.join(twopc_dir, f"{intr}ms", json_fname)
        if intr == 100:
            if query == 1 or query == 2:
                r2pc_dir = f"../fig10_fig11/q38_rerun/remote_2pc/q{query}-180s-0swarm-100ms-src10ms"
            else:
                r2pc_dir = f"../fig10_fig11/q38_rerun/remote_2pc/q{query}-180s-0swarm-100ms-src100ms"
            r2pc = load(r2pc_dir, query-1)
            for row in r2pc:
                if row['tps'] == tp:
                    twopc_p50.append(int(row['p50']))
                    twopc_p99.append(int(row['p99']))
        elif os.path.exists(fname):
            with open(fname, "r") as f:
                data = json.load(f)
            if tp in data:
                twopc_p50.append(data[tp]["p50"])
                twopc_p99.append(data[tp]["p99"])

    print(f"mark intr: {markIntr}")
    print(f"epoch p50: {epoch_p50}")
    print(f"epoch p99: {epoch_p99}")
    print(f"twopc p50: {twopc_p50}")
    print(f"twopc p99: {twopc_p99}")
    p50_ratio = np.array(twopc_p50) / np.array(epoch_p50)
    p99_ratio = np.array(twopc_p99) / np.array(epoch_p99)
    print(f"twopc/epoch p50: {p50_ratio}")
    print(f"twopc/epoch p99: {p99_ratio}")
    return epoch_p50, epoch_p99, twopc_p50, twopc_p99


def main():
    # queries = [4, 6, 7]
    queries = [1, 2, 3, 4, 5, 6, 7, 8]
    fig = plt.figure(figsize=(28, 15), layout='constrained')
    # axs = fig.subplots(2, 3)
    axs = fig.subplots(4, 4)
    handles=[]
    formatter = ticker.EngFormatter(sep="")
    marksize=14
    for idx, q in enumerate(queries):
        print(f"q{q}")
        mIntr = markIntr
        mFreq = markFreq
        r = ((q-1) // 4) * 2
        c = (q-1) % 4
        ax1 = axs[r][c]
        ax2 = axs[r+1][c]
        epoch_p50, epoch_p99, twopc_p50, twopc_p99 = get_varflush(mIntr, q)
        l1, = ax1.plot(mFreq, epoch_p50, label="Impeller p50", color=colors[0], marker=markers[0], markersize=marksize)
        l2, = ax2.plot(mFreq, epoch_p99, label="Impeller p99", color=colors[0], marker=markers[0], ls='--', markersize=marksize)
        l3, = ax1.plot(mFreq, twopc_p50, label="Multi-stream atomic append on Impeller p50", color=colors[3], marker=markers[3], markersize=marksize)
        l4, = ax2.plot(mFreq, twopc_p99, label="Multi-stream atomic append on Impeller p99", color=colors[3], marker=markers[3], ls='--', markersize=marksize)
        if idx == 0:
            handles = [l1, l2, l3, l4]
        lines = [l1, l2, l3, l4]
        for l in lines:
            l.set_linewidth(3)
        tp = int(throughputs[q]) * 4
        ax1.set_title(f"Query{q}, {formatter.format_eng(tp)} events/s", fontsize=18)
        ax1.set_xticks(mFreq, labels=mIntr)
        ax2.set_xticks(mFreq, labels=mIntr)
        ax1.tick_params(labelsize=18)
        ax2.tick_params(labelsize=18)
        if q == 1:
            ax1.set_ylim([0, 15])
            ax2.set_ylim([0, 30])
        elif q == 2:
            ax1.set_ylim([0, 15])
            ax2.set_ylim([0, 40])
        elif q == 7:
            ax1.set_ylim([0, 200])
            ax2.set_ylim([0, 400])
        else:
            ax1.set_ylim(ymin=0)
            ax2.set_ylim(ymin=0)
    fig.legend(loc='upper center', bbox_to_anchor=(0.5, 1.07), ncol=2, handles=handles, fontsize=18)
    fig.supxlabel('Commit interval(ms)', fontsize=18)
    fig.supylabel('Event time latency (ms)', fontsize=18)
    plt.savefig('varMarkTime.pdf', bbox_inches='tight', pad_inches = 0)


if __name__ == '__main__':
    main()
