import json
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(os.path.join(parent, 'pub_data'))

from fig_const import markers, colors, headers

markIntr = [5, 7, 10, 25, 50]
markFreq = [200, 142, 100, 40, 20]
# epoch_dir = "../q8_varflush_stats/epoch/" 
# twopc_dir = "../q8_varflush_stats/2pc/"
epoch_dir = "../pub_data/micro/q8_varflush/epoch/" 
r2pc_dir = "../pub_data/micro/q8_varflush/remote_2pc/"

def main():
    epoch_p50 = []
    epoch_p99 = []
    twopc_p50 = []
    twopc_p99 = []
    for intr in markIntr:
        fname = os.path.join(epoch_dir, f"{intr}ms", "q8.json")
        with open(fname, "r") as f:
            data = json.load(f)
        epoch_p50.append(data["12000"]["p50"])
        epoch_p99.append(data["12000"]["p99"])

        fname = os.path.join(r2pc_dir, f"{intr}ms", "q8.json")
        with open(fname, "r") as f:
            data = json.load(f)
        twopc_p50.append(data["12000"]["p50"])
        twopc_p99.append(data["12000"]["p99"])
    print(f"mark intr: {markIntr}")
    print(f"epoch p50: {epoch_p50}")
    print(f"epoch p99: {epoch_p99}")
    print(f"twopc p50: {twopc_p50}")
    print(f"twopc p99: {twopc_p99}")
    p50_ratio = np.array(twopc_p50) / np.array(epoch_p50)
    p99_ratio = np.array(twopc_p99) / np.array(epoch_p99)
    print(f"2pc/epoch p50: {p50_ratio}")
    print(f"2pc/epoch p99: {p99_ratio}")

    fig = plt.figure(figsize=(6.5, 3))
    axs = fig.subplots(1, 2)
    l1, = axs[0].plot(markFreq, epoch_p50, label="Impeller p50", color=colors[0], marker=markers[0])
    l2, = axs[1].plot(markFreq, epoch_p99, label="Impeller p99", color=colors[0], marker=markers[0], ls='--')
    l3, = axs[0].plot(markFreq, twopc_p50, label="Kafka Stream on Impeller p50", color=colors[3], marker=markers[3])
    l4, = axs[1].plot(markFreq, twopc_p99, label="Kafka Stream on Impeller p99", color=colors[3], marker=markers[3], ls='--')
    axs[0].legend(loc=(0.2, 1.05), ncol=2, handles=[l1, l2, l3, l4])
    fig.supxlabel('Progress marking frequency(marks/s)', fontsize=14)
    fig.supylabel('Event time latency (ms)', fontsize=14)
    axs[0].set_ylim(0, 80)
    axs[1].set_ylim(0, 250)
    plt.subplots_adjust(bottom=0.15)
    plt.savefig('q8_varMarkTime.pdf', bbox_inches='tight')


if __name__ == '__main__':
    main()
