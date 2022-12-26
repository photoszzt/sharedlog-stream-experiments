import os
import numpy as np
import json
import matplotlib.pyplot as plt

input_throughput = [48000, 64000, 80000, 112000, 128000]
per_work_in_tp = [12000, 16000, 20000, 28000, 32000]
times = [10, 50, 100]
colors = ['orange', 'blue', ]

kafkas = [
    "../q8_stats/kafka/180s_0swarm_10ms_src10ms/q8_stats.json",
    "../q8_stats/kafka/180s_0swarm_50ms_src50ms/q8_stats.json",
    "../q8_stats/kafka/180s_0swarm_100ms_src100ms/q8_stats.json",
]

impellers = [
    "../q8_stats2/impeller/180s_0swarm_10ms_src10ms/mark_time.json",
    "../q8_stats2/impeller/180s_0swarm_50ms_src50ms/mark_time.json",
    "../q8_stats2/impeller/180s_0swarm_100ms_src100ms/mark_time.json",
]


def main():
    fig = plt.figure(figsize=(9, 7))
    l1, l2, l3, l4 = None, None, None, None
    axs = fig.subplots(2, 3, sharey='row')
    ax1 = None
    for i in range(0, len(times)):
        t = times[i]
        kpath = kafkas[i]
        ipath = impellers[i]
        with open(kpath, "r") as f:
            kdata = json.load(f)
        with open(ipath, "r") as f:
            idata = json.load(f)
        idata = [row for row in idata if row[0] in per_work_in_tp]
        klat = kdata['avgCommitLat']
        if i == 0:
            ax1 = axs[0, i]
        ll1, = axs[0, i].plot(input_throughput, klat['p50'], label=f'Kafka Streams p50',
                color=colors[0], marker='v')
        ll2, = axs[1, i].plot(input_throughput, klat['p99'], label=f'Kafka Streams p99',
                color=colors[0], marker='v', ls='--')
        ll3, = axs[0, i].plot(input_throughput, [row[1]/1000.0 for row in idata], 
                label=f'Impeller p50', color=colors[1], marker='o')
        ll4, = axs[1, i].plot(input_throughput, [row[2]/1000.0 for row in idata], 
                label=f'Impeller p99', color=colors[1], marker='o', ls='--')
        if i == 1:
            axs[0, i].set_title(f'p50\n{t}ms', fontsize=16)
            axs[1, i].set_title(f'p99', fontsize=16)
        else:
            axs[0, i].set_title(f'{t}ms', fontsize=16)
        if i == 0:
            l1, l2, l3, l4 = ll1, ll2, ll3, ll4
    ax1.legend(loc=(0.9, 1.25), ncol=2, handles = [l1, l2, l3, l4])
    fig.supxlabel('input throughput(events/s)', fontsize=16)
    fig.supylabel('commit/progress marking time(ms)', fontsize=16)
    plt.savefig('q8_commit_time.pdf', bbox_inches='tight')


if __name__ == '__main__':
    main()
