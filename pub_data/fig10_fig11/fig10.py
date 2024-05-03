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

kafkas = [
    "./curated/kafka/q1-kafka-180s-0swarm-100ms-src10ms",
    "./curated/kafka/q2-kafka-180s-0swarm-100ms-src10ms",
    "./curated/kafka/q3-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q4-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q5-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q6-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q7-3t-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q8-kafka-180s-0swarm-100ms-src100ms",
]

syss = [
    "./pm_data/sys-boki/q1-180s-0swarm-100ms-src10ms2",
    "./pm_data/sys-boki/q2-180s-0swarm-100ms-src10ms2",
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

alignchkpts = [
    "./q38_rerun/align_chkpt_kvrocks2/q1-180s-0swarm-100ms-src10ms",
    "./q38_rerun/align_chkpt_kvrocks2/q2-180s-0swarm-100ms-src10ms",
    "./q38_rerun/align_chkpt_kvrocks2/q3-180s-0swarm-100ms-src100ms",
    "./q38_rerun/align_chkpt_kvrocks2/q4-180s-0swarm-100ms-src100ms",
    "./q38_rerun/align_chkpt_kvrocks2/q5-180s-0swarm-100ms-src100ms",
    "./q38_rerun/align_chkpt_kvrocks2/q6-180s-0swarm-100ms-src100ms",
    "./q38_rerun/align_chkpt_kvrocks2/q7-180s-0swarm-100ms-src100ms",
    "./q38_rerun/align_chkpt_kvrocks2/q8-180s-0swarm-100ms-src100ms",
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
            if (row['del'] == 'eo' or row['del'] == '2pc' or row['del'] == 'align_chkpt') and int(row['tps']) in throughputs[experiment]]
    rows.sort(key=lambda row: int(row['tps']))
    return rows


if __name__ == "__main__":
    for experiment in range(0, len(kafkas)):
        kafka = load(kafkas, experiment)
        sys = load(syss, experiment)
        twopc = load(twopcs, experiment)
        ackpt = load(alignchkpts, experiment)

        sys_in_per_worker_tp = [int(row['tps']) for row in sys]
        kafka_in_per_worker_tp = [int(row['tps']) for row in kafka]
        ackpt_in_per_worker_tp = [int(row['tps']) for row in ackpt]

        kafka_in_tp = [i*4 for i in kafka_in_per_worker_tp]
        sys_in_tp = [i*4 for i in sys_in_per_worker_tp]
        ackpt_in_tp = [i*4 for i in ackpt_in_per_worker_tp]

        sys_p50 = np.array([int(row['p50']) for row in sys])
        sys_p99 = np.array([int(row['p99']) for row in sys])
        twopc_p50 = np.array([int(row['p50']) for row in twopc])
        twopc_p99 = np.array([int(row['p99']) for row in twopc])
        ackpt_p50 = [int(row['p50']) for row in ackpt]
        ackpt_p99 = [int(row['p99']) for row in ackpt]

        print('Q' + str(experiment + 1))
        print(f"sys tp: {sys_in_tp}") 
        print(f"sys p50: {sys_p50}")
        print(f"sys p99: {sys_p99}")
        print(f"kafka tp: {kafka_in_tp}")
        print(f"kafka p50: {[int(row['p50']) for row in kafka]}")
        print(f"kafka p99: {[int(row['p99']) for row in kafka]}")
        print(f"2pc tp: {sys_in_tp}") 
        print(f"2pc p50: {twopc_p50}")
        print(f"2pc p99: {twopc_p99}")
        print(f"2pc/sys p50: {twopc_p50/sys_p50}")
        print(f"2pc/sys p99: {twopc_p99/sys_p99}")
        print(f"ackpt tp: {ackpt_in_tp}")
        print(f"alignchkpt p50: {ackpt_p50}")
        print(f"alignchkpt p99: {ackpt_p99}")
        marksize=14

        fig = plt.figure(figsize=(6, 2.8))
        ax1 = plt.subplot(111)
        l1, = ax1.plot(sys_in_tp, [int(row['p50']) for row in sys], label='Impeller p50',  marker='o',color=colors[0])
        l2, = ax1.plot(kafka_in_tp, [int(row['p50']) for row in kafka], label='Kafka Streams p50',  marker='v',color=colors[1])
        l3, = ax1.plot(sys_in_tp, [int(row['p99']) for row in sys], label='Impeller p99', ls='--', marker='o', color=colors[0])
        l4, = ax1.plot(kafka_in_tp, [int(row['p99']) for row in kafka], label='Kafka Streams p99', ls='--', marker='v', color=colors[1])
        l5, = ax1.plot(sys_in_tp, [int(row['p50']) for row in twopc], label='2PC on Impeller p50',  marker='s', color=colors[3])
        l6, = ax1.plot(sys_in_tp, [int(row['p99']) for row in twopc], label='2PC on Impeller p99',  ls='--', marker='s',color=colors[3])
        lines = [l1, l2, l3, l4, l5, l6]
        # if experiment == 6:
        #     l9, = ax1.plot(ackpt_in_tp, ackpt_p50, label='Align chkpt nosync WAL on Impeller p50',  marker=markers[5], color=colors[5], markersize=marksize)
        #     l10, = ax1.plot(ackpt_in_tp, ackpt_p99, label='Align chkpt nosync WAL on Impeller p99',  ls='--', marker=markers[5],color=colors[5], markersize=marksize)
        #     lines = [l1, l2, l3, l4, l5, l6, l9, l10]
        # else:
        #     l7, = ax1.plot(ackpt_in_tp, ackpt_p50, label='Align chkpt on Impeller p50',  marker=markers[4], color=colors[4], markersize=marksize)
        #     l8, = ax1.plot(ackpt_in_tp, ackpt_p99, label='Align chkpt on Impeller p99',  ls='--', marker=markers[4],color=colors[4], markersize=marksize)
        #     lines = [l1, l2, l3, l4, l5, l6, l7, l8]
        for l in lines:
            l.set_linewidth(3)
        handles = [l1, l3, l2, l4, l5, l6]
        # if experiment == 6:
        #     handles = [l1, l3, l2, l4, l5, l6, l9, l10]
        # else:
        #     handles = [l1, l3, l2, l4, l5, l6, l7, l8]

        ax1.set_xlabel('Input throughput(events/s)', fontsize=16)
        ax1.set_ylabel('Event time latency(ms)', fontsize=16)
        ax1.legend(loc=(0, 1.05), ncol=2, handles=handles, handlelength=3, fontsize=11)
        ax1.xaxis.set_major_formatter(ticker.EngFormatter())

        if experiment < 2:
            plt.ylim([0, 60])
        else:
            plt.ylim([0, 1000])

        # plt.title('Q' + str(experiment + 1))
        plt.savefig('comparisons/q' + str(experiment + 1) + '.png', bbox_inches='tight')
