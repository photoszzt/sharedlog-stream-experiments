import json
import os
import matplotlib.pyplot as plt

markIntr = [3, 5, 7, 10]
epoch_dir = "../q8_varflush_stats/epoch/" 
twopc_dir = "../q8_varflush_stats/2pc/"

colors = ['blue', 'purple']

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

        fname = os.path.join(twopc_dir, f"{intr}ms", "q8.json")
        with open(fname, "r") as f:
            data = json.load(f)
        twopc_p50.append(data["12000"]["p50"])
        twopc_p99.append(data["12000"]["p99"])

    fig = plt.figure(figsize=(6, 2.8))
    l1, = plt.plot(markIntr, epoch_p50, label="Impeller p50", color=colors[0], marker='o')
    l2, = plt.plot(markIntr, epoch_p99, label="Impeller p99", color=colors[0], marker='o', ls='--')
    l3, = plt.plot(markIntr, twopc_p50, label="2pc on Impeller p50", color=colors[1], marker='s')
    l4, = plt.plot(markIntr, twopc_p99, label="2pc on Impeller p99", color=colors[1], marker='s', ls='--')
    plt.legend(loc=(0, 1.1), ncol=2, handles=[l1, l2, l3, l4], )
    plt.xlabel('flush interval(ms)', fontsize=16)
    plt.ylabel('event time latency(ms)', fontsize=16)
    plt.savefig('q8_varMarkTime.pdf', bbox_inches='tight')


if __name__ == '__main__':
    main()
