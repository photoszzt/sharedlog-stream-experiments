import os
import csv
import subprocess
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(current))
sys.path.append(parent)

from fig_const import markers, colors, headers

input_throughput = [48000, 64000, 80000, 112000, 128000]
per_worker_in_tp = [12000, 16000, 20000, 28000, 32000]
times = [10, 50, 100]

kafkas = [
    "../q8_e2e/kafka/180s_0swarm_10ms_src10ms/",
    "../q8_e2e/kafka/180s_0swarm_50ms_src50ms/",
    "../q8_e2e/kafka/180s_0swarm_100ms_src100ms/",
]

impellers = [
    "../q8_e2e2/impeller/180s_0swarm_10ms_src10ms/",
    "../q8_e2e2/impeller/180s_0swarm_50ms_src50ms/",
    "../q8_e2e2/impeller/180s_0swarm_100ms_src100ms/",
]

twopcs = [
    "../q8_e2e2/2pc/180s_0swarm_10ms_src10ms/",
    "../q8_e2e2/2pc/180s_0swarm_50ms_src50ms/",
    "../q8_e2e2/2pc/180s_0swarm_100ms_src100ms/",
]

def load(system, experiment):
    rows = subprocess.run(["latency", "query", system[experiment]], stdout=subprocess.PIPE)
    rows = rows.stdout.decode('utf-8').strip().split('\n')
    rows = [row for row in csv.DictReader(rows, fieldnames=headers) 
            if (row['del'] == 'eo' or row['del'] == '2pc') and int(row['tps']) in per_worker_in_tp]
    rows.sort(key=lambda row: int(row['tps']))
    return rows


def main():
    fig = plt.figure(figsize=(9, 4.5))
    l1, l2, l3, l4 = None, None, None, None
    axs = fig.subplots(1, 3, sharey='row')
    ax1 = None
    for i in range(0, len(times)):
        t = times[i]
        kafka = load(kafkas, i)
        impeller = load(impellers, i)
        twopc = load(twopcs, i)
        ax = axs[i]
        if i == 0:
            ax1 = ax
        ll1, = ax.plot(input_throughput, [int(row['p50']) for row in kafka], label='Kafka Streams p50',
                color=colors[1], marker=markers[1])
        ll2, = ax.plot(input_throughput, [int(row['p99']) for row in kafka], label='Kafka Streams p99',
                color=colors[1], marker=markers[1], ls='--')
        ll3, = ax.plot(input_throughput, [int(row['p50']) for row in impeller], 
                label=f'Impeller p50', color=colors[0], marker=markers[0])
        ll4, = ax.plot(input_throughput, [int(row['p99']) for row in impeller], label='Impeller p99',
                color=colors[0], marker=markers[0], ls='--')
        ll5, = ax.plot(input_throughput, [int(row['p50']) for row in twopc], 
                label=f'2pc on Impeller p50', color=colors[3], marker=markers[3])
        ll6, = ax.plot(input_throughput, [int(row['p99']) for row in twopc], 
                label='2pc on Impeller p99',
                color=colors[3], marker=markers[3], ls='--')
        if i == 0:
            l1, l2, l3, l4 = ll1, ll2, ll3, ll4
        ax.set_ylim(0, 1000)
        ax.set_title(f'{t}ms', fontsize=16)
    ax1.legend(loc=(0.9, 1.1), ncol=2, handles = [l1, l2, l3, l4])
    ax1.xaxis.set_major_formatter(ticker.EngFormatter())
    fig.supxlabel('input throughput (events/s)', fontsize=16)
    fig.supylabel('event time latency (ms)', fontsize=16)
    plt.savefig('q8_compare_e2e.pdf', bbox_inches='tight')


if __name__ == '__main__':
    main()
