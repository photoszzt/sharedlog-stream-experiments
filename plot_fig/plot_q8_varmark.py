import json
import os
import matplotlib.pyplot as plt

markIntr = [3, 5, 7, 10]
markFreq = [333, 200, 142, 100]
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
    print(f"mark intr: {markIntr}")
    print(f"epoch p50: {epoch_p50}")
    print(f"epoch p99: {epoch_p99}")
    print(f"twopc p50: {twopc_p50}")
    print(f"twopc p99: {twopc_p99}")

    fig = plt.figure(figsize=(6.5, 3))
    axs = fig.subplots(1, 2)
    l1, = axs[0].plot(markFreq, epoch_p50, label="Impeller p50", color=colors[0], marker='o')
    l3, = axs[0].plot(markFreq, twopc_p50, label="2pc on Impeller p50", color=colors[1], marker='s')
    l2, = axs[1].plot(markFreq, epoch_p99, label="Impeller p99", color=colors[0], marker='o', ls='--')
    l4, = axs[1].plot(markFreq, twopc_p99, label="2pc on Impeller p99", color=colors[1], marker='s', ls='--')
    axs[0].legend(loc=(0.3, 1.05), ncol=2, handles=[l1, l2, l3, l4])
    fig.supxlabel('progress marking frequency(marks/s)', fontsize=14)
    fig.supylabel('event time latency (ms)', fontsize=14)
    axs[0].set_ylim(0, 150)
    axs[1].set_ylim(0, 1100)
    plt.subplots_adjust(bottom=0.15)
    plt.savefig('q8_varMarkTime.pdf', bbox_inches='tight')


if __name__ == '__main__':
    main()
