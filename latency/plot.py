import csv
import matplotlib.pyplot as plt
import subprocess
import sys

headers = ['del', 'tps', 'trials', 'pts', 'avg', 'std', 'min', 'p25', 'p50', 'p75', 'p90', 'p99', 'max']

kafkas = [
    "curated/kafka/q1-kafka-180s-0swarm-100ms-src10ms",
    "curated/kafka/q2-kafka-180s-0swarm-100ms-src10ms",
    "curated/kafka/q3-kafka-180s-0swarm-100ms-src100ms",
    "curated/kafka/q4-kafka-180s-0swarm-100ms-src100ms",
    "curated/kafka/q5-kafka-180s-0swarm-100ms-src100ms",
    "curated/kafka/q6-kafka-180s-0swarm-100ms-src100ms",
    "curated/kafka/q7-kafka-180s-0swarm-100ms-src100ms",
    "curated/kafka/q8-kafka-180s-0swarm-100ms-src100ms",
]

syss = [
    "curated/sys-boki/q1-boki-180s-0swarm-100ms-src10ms",
    "curated/sys-boki/q2-boki-180s-0swarm-100ms-src10ms",
    "curated/sys-boki/q3-boki-180s-0swarm-100ms-src100ms",
    "curated/sys-boki/q4-boki-180s-0swarm-100ms-src100ms",
    "curated/sys-boki/q5-boki-180s-0swarm-100ms-src100ms",
    "curated/sys-boki/q6-boki-180s-0swarm-100ms-src100ms",
    "curated/sys-boki/q7-boki-180s-0swarm-100ms-src100ms",
    "curated/sys-boki/q8-boki-180s-0swarm-100ms-src100ms",
]

throughputs = [
    [4000, 16000, 32000, 48000, 64000, 80000, 88000],
    [4000, 16000, 32000, 48000, 64000, 80000, 88000],
    [8000, 16000, 32000, 48000, 64000, 80000, 96000, 112000, 128000],
    [250, 500, 750, 1000, 1250, 1500, 1750, 2000],
    [1000, 8000, 16000, 24000, 32000, 40000, 48000, 56000, 64000],
    [250, 500, 750, 1000, 1250, 1500, 1750, 2000],
    [4000, 8000, 12000, 16000, 20000, 24000, 28000, 32000, 36000, 40000],
    [4000, 8000, 12000, 16000, 20000, 24000, 28000, 32000, 36000],
]

colors = ['blue', 'orange']

def load(system, experiment):
    rows = subprocess.run(["latency", "query", system[experiment]], stdout=subprocess.PIPE)
    rows = rows.stdout.decode('utf-8').strip().split('\n')
    rows = [row for row in csv.DictReader(rows, fieldnames=headers) if row['del'] == 'eo' and int(row['tps']) in throughputs[experiment]]
    rows.sort(key=lambda row: int(row['tps']))
    return rows

if __name__ == "__main__":
    for experiment in range(0, len(kafkas)):
        kafka = load(kafkas, experiment)
        sys = load(syss, experiment)

        sys_in_per_worker_tp = [int(row['tps']) for row in sys]
        kafka_in_per_worker_tp = [int(row['tps']) for row in kafka]

        kafka_in_tp = [i*4 for i in kafka_in_per_worker_tp]
        sys_in_tp = [i*4 for i in sys_in_per_worker_tp]

        fig = plt.figure()
        ax1 = plt.subplot(111)
        l1, = ax1.plot(sys_in_tp, [int(row['p50']) for row in sys], label='sys p50',  marker='o',color=colors[0])
        l2, = ax1.plot(kafka_in_tp, [int(row['p50']) for row in kafka], label='kafka p50',  marker='o',color=colors[1])
        l3, = ax1.plot(sys_in_tp, [int(row['p99']) for row in sys], label='sys (--) p99', ls='--', marker='o', color=colors[0])
        l4, = ax1.plot(kafka_in_tp, [int(row['p99']) for row in kafka], label='kafka (--) p99', ls='--', marker='o', color=colors[1])

        ax1.set_xlabel('input throughput(events/s)')
        ax1.set_ylabel('event time latency(ms)')
        ax1.legend(loc=(0, 1.1), ncol=2, handles=[l1, l2, l3, l4], handlelength=3)

        if experiment < 2:
            plt.ylim([0, 60])
        else:
            plt.ylim([0, 1000])

        plt.title('Q' + str(experiment + 1))
        plt.savefig('comparisons/q' + str(experiment + 1) + '.pdf', bbox_inches='tight')
