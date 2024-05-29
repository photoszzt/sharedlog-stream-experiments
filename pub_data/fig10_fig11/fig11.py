import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import subprocess
import sys
import os
import numpy as np

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from fig_const import markers, colors, headers

kafkas = [
    "./curated/kafka/q1-kafka-180s-0swarm-10ms-src10ms",
    "./curated/kafka/q2-kafka-180s-0swarm-10ms-src10ms",
    "./curated/kafka/q3-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q4-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q5-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q6-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q7-3t-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q8-kafka-180s-0swarm-100ms-src100ms",
]

syss = [
    "./pm_data/sys-boki/q1-boki-180s-0swarm-10ms-src10ms",
    "./pm_data/sys-boki/q2-boki-180s-0swarm-10ms-src10ms",
    "./q38_rerun/impeller/q3-180s-0swarm-100ms-src100ms",
    "./q38_rerun/impeller/q4-180s-0swarm-100ms-src100ms",
    "./q38_rerun/impeller/q5-180s-0swarm-100ms-src100ms",
    "./q38_rerun/impeller/q6-180s-0swarm-100ms-src100ms",
    "./q38_rerun/impeller/q7-180s-0swarm-100ms-src100ms",
    "./q38_rerun/impeller/q8-180s-0swarm-100ms-src100ms",
]

twopcs = [
    "./q38_rerun/2pc/q1-180s-0swarm-100ms-src10ms",
    "./q38_rerun/2pc/q2-180s-0swarm-100ms-src10ms",
    "./q38_rerun/2pc/q3-180s-0swarm-100ms-src100ms",
    "./q38_rerun/2pc/q4-180s-0swarm-100ms-src100ms",
    "./q38_rerun/2pc/q5-180s-0swarm-100ms-src100ms",
    "./q38_rerun/2pc/q6-180s-0swarm-100ms-src100ms",
    "./q38_rerun/2pc/q7-180s-0swarm-100ms-src100ms",
    "./q38_rerun/2pc/q8-180s-0swarm-100ms-src100ms",
]

remote_2pc = [
    "./q38_rerun/remote_2pc/q1-180s-0swarm-100ms-src10ms",
    "./q38_rerun/remote_2pc/q2-180s-0swarm-100ms-src10ms",
    "./q38_rerun/remote_2pc/q3-180s-0swarm-100ms-src100ms",
    "./q38_rerun/remote_2pc/q4-180s-0swarm-100ms-src100ms",
    "./q38_rerun/remote_2pc/q5-180s-0swarm-100ms-src100ms",
    "./q38_rerun/remote_2pc/q6-180s-0swarm-100ms-src100ms",
    "./q38_rerun/remote_2pc/q7-180s-0swarm-100ms-src100ms",
    "./q38_rerun/remote_2pc/q8-180s-0swarm-100ms-src100ms",
]

nones = [
    "./none_data/sys-boki/q1-boki-180s-0swarm-100ms-src10ms",
    "./none_data/sys-boki/q2-boki-180s-0swarm-100ms-src10ms",
    "./none_data/sys-boki/q3-boki-180s-0swarm-100ms-src100ms",
    "./none_data/sys-boki/q4-boki-180s-0swarm-100ms-src100ms",
    "./none_data/sys-boki/q5-boki-180s-0swarm-100ms-src100ms",
    "./none_data/sys-boki/q6-boki-180s-0swarm-100ms-src100ms",
    "./none_data/sys-boki/q7-boki-180s-0swarm-100ms-src100ms",
    "./none_data/sys-boki/q8-boki-180s-0swarm-100ms-src100ms",
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
    os.makedirs('comparisons_unsafe', exist_ok=True)
    for experiment in range(0, len(kafkas)):
        kafka = load(kafkas, experiment)
        sys = load(syss, experiment)
        twopc = load(twopcs, experiment)
        none = load(nones, experiment)
        r2pc = load(remote_2pc, experiment)

        sys_in_per_worker_tp = [int(row['tps']) for row in sys]
        none_in_per_worker_tp = [int(row['tps']) for row in none]
        kafka_in_per_worker_tp = [int(row['tps']) for row in kafka]
        remote2pc_in_per_worker_tp = [int(row['tps']) for row in r2pc]

        kafka_in_tp = [i*4 for i in kafka_in_per_worker_tp]
        sys_in_tp = [i*4 for i in sys_in_per_worker_tp]
        none_in_tp = [i*4 for i in none_in_per_worker_tp]
        r2pc_in_tp = [i*4 for i in remote2pc_in_per_worker_tp]

        sys_p50 = [int(row['p50']) for row in sys]
        sys_p99 = [int(row['p99']) for row in sys]
        r2pc_p50 = [int(row['p50']) for row in r2pc]
        r2pc_p99 = [int(row['p99']) for row in r2pc]
        unsafe_p50 = [int(row['p50']) for row in none]
        unsafe_p99 = [int(row['p99']) for row in none]

        print('Q' + str(experiment + 1))
        print(f"sys tp: {sys_in_tp}") 
        print(f"sys p50: {sys_p50}")
        print(f"sys p99: {sys_p99}")
        print(f"sys unsafe tp: {none_in_tp}")
        print(f"sys unsafe p50: {unsafe_p50}")
        print(f"sys unsafe p99: {unsafe_p99}")
        print(f"kafka tp: {kafka_in_tp}")
        print(f"kafka p50: {[int(row['p50']) for row in kafka]}")
        print(f"kafka p99: {[int(row['p99']) for row in kafka]}")

        fig, axs = plt.subplots(2, 1, figsize=(6, 3.2), layout='constrained')
        ax1 = axs[0]
        ax2 = axs[1]
        l1, = ax1.plot(sys_in_tp, [int(row['p50']) for row in sys], label='Impeller p50',  marker=markers[0],color=colors[0])
        l3, = ax2.plot(sys_in_tp, [int(row['p99']) for row in sys], label='Impeller p99', ls='--', marker=markers[0], color=colors[0])
        l2, = ax1.plot(kafka_in_tp, [int(row['p50']) for row in kafka], label='Kafka Streams p50',  marker=markers[1],color=colors[1])
        l4, = ax2.plot(kafka_in_tp, [int(row['p99']) for row in kafka], label='Kafka Streams p99', ls='--', marker=markers[1], color=colors[1])
        l5, = ax1.plot(none_in_tp, [int(row['p50']) for row in none], label='Impeller unsafe p50',  marker=markers[2],color=colors[2])
        l6, = ax2.plot(none_in_tp, [int(row['p99']) for row in none], label='Impeller unsafe p99', ls='--', marker=markers[2],color=colors[2])
        l7, = ax1.plot(r2pc_in_tp, r2pc_p50, label='Kafka Streams on Impeller p50',  marker=markers[3], color=colors[3])
        l8, = ax2.plot(r2pc_in_tp, r2pc_p99, label='Kafka Streams on Impeller p99',  ls='--', marker=markers[3],color=colors[3])

        fig.supxlabel('Input throughput(events/s)')
        fig.supylabel('Event time latency(ms)')
        fig.legend(ncol=2, handles=[l1, l3, l2, l4, l5, l6, l7, l8], loc='upper center', bbox_to_anchor=(0.55, 1.3))
        ax1.xaxis.set_major_formatter(ticker.EngFormatter())
        ax2.xaxis.set_major_formatter(ticker.EngFormatter())

        if experiment < 2:
            ax1.set_ylim([0, 60])
            ax2.set_ylim([0, 60])
        else:
            ax1.set_ylim([0, 1000])
            ax2.set_ylim([0, 1000])

        # plt.title('Q' + str(experiment + 1))
        plt.savefig('comparisons_unsafe/q' + str(experiment + 1) + '.pdf', bbox_inches='tight')
