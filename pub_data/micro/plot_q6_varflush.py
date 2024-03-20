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
epoch_dir = "./q6_varflush/epoch"
twopc_dir = "./q6_varflush/2pc"


def main():
    epoch_p50 = []
    epoch_p99 = []
    twopc_p50 = []
    twopc_p99 = []
    for intr in markIntr:
        fname = os.path.join(epoch_dir, f"{intr}ms", "q6.json")
        with open(fname, "r") as f:
            data = json.load(f)
        epoch_p50.append(data["750"]["p50"])
        epoch_p99.append(data["750"]["p99"])

        fname = os.path.join(twopc_dir, f"{intr}ms", "q6.json")
        with open(fname, "r") as f:
            data = json.load(f)
        twopc_p50.append(data["750"]["p50"])
        twopc_p99.append(data["750"]["p99"])
    p50_ratio = np.array(twopc_p50) / np.array(epoch_p50)
    p99_ratio = np.array(twopc_p99) / np.array(epoch_p99)
    print(f"mark intr: {markIntr}")
    print(f"epoch p50: {epoch_p50}")
    print(f"epoch p99: {epoch_p99}")
    print(f"twopc p50: {twopc_p50}")
    print(f"twopc p99: {twopc_p99}")
    print(f"twopc/epoch p50: {p50_ratio}")
    print(f"twopc/epoch p99: {p99_ratio}")
    fig = plt.figure(figsize=(6.5, 3))
    axs = fig.subplots(1, 2)
    l1, = axs[0].plot(markFreq, epoch_p50, label="Impeller p50", color=colors[0], marker=markers[0])
    l2, = axs[1].plot(markFreq, epoch_p99, label="Impeller p99", color=colors[0], marker=markers[0], ls='--')
    l3, = axs[0].plot(markFreq, twopc_p50, label="2pc on Impeller p50", color=colors[3], marker=markers[3])
    l4, = axs[1].plot(markFreq, twopc_p99, label="2pc on Impeller p99", color=colors[3], marker=markers[3], ls='--')
    axs[0].legend(loc=(0.3, 1.05), ncol=2, handles=[l1, l2, l3, l4])
    fig.supxlabel('Progress marking frequency(marks/s)', fontsize=14)
    fig.supylabel('Event time latency (ms)', fontsize=14)
    plt.subplots_adjust(bottom=0.15)
    plt.savefig('q6_varMarkTime.pdf', bbox_inches='tight')



if __name__ == '__main__':
    main()
