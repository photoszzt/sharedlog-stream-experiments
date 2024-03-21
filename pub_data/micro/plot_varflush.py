import json
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from fig_const import markers, colors, headers

markFreq = [10, 20, 40]
markIntr = [100, 50, 25]

throughputs = {4: "750", 6: "750", 7: "12000"}


def get_varflush(tp, top_dir, json_fname):
    epoch_dir = f"{top_dir}/epoch"
    twopc_dir = f"{top_dir}/2pc"
    epoch_p50 = []
    epoch_p99 = []
    twopc_p50 = []
    twopc_p99 = []
    for intr in markIntr:
        fname = os.path.join(epoch_dir, f"{intr}ms", json_fname)
        with open(fname, "r") as f:
            data = json.load(f)
        epoch_p50.append(data[tp]["p50"])
        epoch_p99.append(data[tp]["p99"])

        fname = os.path.join(twopc_dir, f"{intr}ms", json_fname)
        with open(fname, "r") as f:
            data = json.load(f)
        twopc_p50.append(data[tp]["p50"])
        twopc_p99.append(data[tp]["p99"])
    p50_ratio = np.array(twopc_p50) / np.array(epoch_p50)
    p99_ratio = np.array(twopc_p99) / np.array(epoch_p99)
    print(f"mark intr: {markIntr}")
    print(f"epoch p50: {epoch_p50}")
    print(f"epoch p99: {epoch_p99}")
    print(f"twopc p50: {twopc_p50}")
    print(f"twopc p99: {twopc_p99}")
    print(f"twopc/epoch p50: {p50_ratio}")
    print(f"twopc/epoch p99: {p99_ratio}")
    return epoch_p50, epoch_p99, twopc_p50, twopc_p99


def main():
    queries = [4, 6, 7]
    fig = plt.figure(figsize=(9.5, 3.5), layout='constrained')
    axs = fig.subplots(2, 3)
    for idx, q in enumerate(queries):
        epoch_p50, epoch_p99, twopc_p50, twopc_p99 = get_varflush(throughputs[q], f"./q{q}_varflush", f"q{q}.json")
        l1, = axs[0][idx].plot(markFreq, epoch_p50, label="Impeller p50", color=colors[0], marker=markers[0])
        l2, = axs[1][idx].plot(markFreq, epoch_p99, label="Impeller p99", color=colors[0], marker=markers[0], ls='--')
        l3, = axs[0][idx].plot(markFreq, twopc_p50, label="2pc on Impeller p50", color=colors[3], marker=markers[3])
        l4, = axs[1][idx].plot(markFreq, twopc_p99, label="2pc on Impeller p99", color=colors[3], marker=markers[3], ls='--')
        if idx == 0:
            handles = [l1, l2, l3, l4]
        axs[0][idx].set_title(f"q{q}")
    axs[0][0].set_ylim(0, 200)
    axs[1][0].set_ylim(0, 300)
    axs[0][1].set_ylim(0, 220)
    axs[1][1].set_ylim(0, 1400)
    axs[0][2].set_ylim(0, 120)
    axs[1][2].set_ylim(0, 200)
    fig.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, handles=handles)
    fig.supxlabel('Progress marking frequency(marks/s)', fontsize=14)
    fig.supylabel('Event time latency (ms)', fontsize=14)
    # plt.subplots_adjust(bottom=0.15)
    plt.savefig('varMarkTime.pdf', bbox_inches='tight')



if __name__ == '__main__':
    main()
