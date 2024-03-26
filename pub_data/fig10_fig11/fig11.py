import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import subprocess
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from fig_const import markers, colors

headers = ['del', 'tps', 'trials', 'pts', 'avg', 'std', 'min', 'p25', 'p50', 'p75', 'p90', 'p99', 'max']

kafkas = [
    "./curated/kafka/q1-kafka-180s-0swarm-10ms-src10ms",
    "./curated/kafka/q2-kafka-180s-0swarm-10ms-src10ms",
    "./curated/kafka/q3-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q4-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q5-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q6-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q7-kafka-180s-0swarm-100ms-src100ms",
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
    rows = subprocess.run(["latency", "query", system[experiment]], stdout=subprocess.PIPE)
    rows = rows.stdout.decode('utf-8').strip().split('\n')
    rows = [row for row in csv.DictReader(rows, fieldnames=headers) if row['del'] == 'eo' and int(row['tps']) in throughputs[experiment]]
    rows.sort(key=lambda row: int(row['tps']))
    return rows

if __name__ == "__main__":
    os.makedirs('comparisons_unsafe', exist_ok=True)
    for experiment in range(0, len(kafkas)):
        kafka = load(kafkas, experiment)
        sys = load(syss, experiment)
        none = load(nones, experiment)

        sys_in_per_worker_tp = [int(row['tps']) for row in sys]
        none_in_per_worker_tp = [int(row['tps']) for row in none]
        kafka_in_per_worker_tp = [int(row['tps']) for row in kafka]

        kafka_in_tp = [i*4 for i in kafka_in_per_worker_tp]
        sys_in_tp = [i*4 for i in sys_in_per_worker_tp]
        none_in_tp = [i*4 for i in none_in_per_worker_tp]

        print('Q' + str(experiment + 1))
        print(f"sys tp: {sys_in_tp}") 
        print(f"sys p50: {[int(row['p50']) for row in sys]}")
        print(f"sys p99: {[int(row['p99']) for row in sys]}")
        print(f"sys unsafe tp: {none_in_tp}")
        print(f"sys unsafe p50: {[int(row['p50']) for row in none]}")
        print(f"sys unsafe p99: {[int(row['p99']) for row in none]}")
        print(f"kafka tp: {kafka_in_tp}")
        print(f"kafka p50: {[int(row['p50']) for row in kafka]}")
        print(f"kafka p99: {[int(row['p99']) for row in kafka]}")

        fig = plt.figure(figsize=(6, 3.2))
        ax1 = plt.subplot(111)
        l1, = ax1.plot(sys_in_tp, [int(row['p50']) for row in sys], label='Impeller p50',  marker=markers[0],color=colors[0])
        l3, = ax1.plot(sys_in_tp, [int(row['p99']) for row in sys], label='Impeller p99', ls='--', marker=markers[0], color=colors[0])
        l2, = ax1.plot(kafka_in_tp, [int(row['p50']) for row in kafka], label='Kafka p50',  marker=markers[1],color=colors[1])
        l4, = ax1.plot(kafka_in_tp, [int(row['p99']) for row in kafka], label='Kafka p99', ls='--', marker=markers[1], color=colors[1])
        l5, = ax1.plot(none_in_tp, [int(row['p50']) for row in none], label='Impeller unsafe p50',  marker=markers[2],color=colors[2])
        l6, = ax1.plot(none_in_tp, [int(row['p99']) for row in none], label='Impeller unsafe p99', ls='--', marker=markers[2],color=colors[2])

        ax1.set_xlabel('input throughput(events/s)')
        ax1.set_ylabel('event time latency(ms)')
        ax1.legend(loc=(0, 1.1), ncol=2, handles=[l1, l5, l2, l3, l6, l4], handlelength=3)
        ax1.xaxis.set_major_formatter(ticker.EngFormatter())
        # ax1.legend(loc=(0, 1.1), ncol=2, handles=[l1, l2, l3, l4], handlelength=3)

        if experiment < 2:
            plt.ylim([0, 60])
        else:
            plt.ylim([0, 1000])

        # plt.title('Q' + str(experiment + 1))
        plt.savefig('comparisons_unsafe/q' + str(experiment + 1) + '.pdf', bbox_inches='tight')
