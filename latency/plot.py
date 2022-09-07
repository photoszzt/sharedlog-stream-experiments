import csv
import matplotlib.pyplot as plt
import subprocess
import sys

headers = ['del', 'tps', 'trials', 'pts', 'avg', 'std', 'min', 'p25', 'p50', 'p75', 'p90', 'p99', 'max']

kafkas = [
    "data/kafka/q1-kafka-180s-0swarm-100ms-src10ms",
    "data/kafka/q2-kafka-180s-0swarm-100ms-src10ms",
    "data/kafka/q3-kafka-180s-0swarm-100ms-src100ms",
    "data/kafka/q4-kafka-180s-0swarm-100ms-src100ms",
    "data/kafka/q5-kafka-180s-0swarm-100ms-src100ms",
    "data/kafka/q6-kafka-180s-0swarm-100ms-src100ms",
    "data/kafka/q7-kafka-180s-0swarm-100ms-src100ms",
    "data/kafka/q8-kafka-180s-0swarm-100ms-src100ms",
]

syss = [
    "data/sys-boki/q1-boki-180s-0swarm-100ms-src10ms",
    "data/sys-boki/q2-boki-180s-0swarm-100ms-src10ms",
    "data/sys-boki/q3-boki-180s-0swarm-100ms-src100ms",
    "data/sys-boki/q4-boki-180s-0swarm-100ms-src100ms",
    "data/sys-boki/q5-boki-180s-0swarm-100ms-src100ms",
    "data/sys-boki/q6-boki-180s-0swarm-100ms-src100ms",
    "data/sys-boki/q7-boki-180s-0swarm-100ms-src100ms",
    "data/sys-boki/q8-boki-180s-0swarm-100ms-src100ms",
]

windows = [
    (None, 80000),
    (1000, 88000),
    (None, None),
    (None, 750),
    (None, 16000),
    (None, 625),
    (None, 2000),
    (None, 12000),
]

colors = ['blue', 'orange', 'green', 'red']

def load(system, experiment):
    lo, hi = windows[experiment]
    lo = 0 if lo is None else lo
    hi = 1000000000 if hi is None else hi

    rows = subprocess.run(["target/release/latency", "query", system[experiment]], stdout=subprocess.PIPE)
    rows = rows.stdout.decode('utf-8').strip().split('\n')
    rows = [row for row in csv.DictReader(rows, fieldnames=headers) if row['del'] == 'eo' and int(row['tps']) >= lo and int(row['tps']) <= hi]
    rows.sort(key=lambda row: int(row['tps']))
    return rows


if __name__ == "__main__":
    for experiment in range(0, len(kafkas)):
        kafka = load(kafkas, experiment)
        sys = load(syss, experiment)

        sys_in_per_worker_tp = [int(row['tps']) for row in sys]
        print(sys_in_per_worker_tp)
        in_per_worker_tp = [int(row['tps']) for row in kafka]
        print(in_per_worker_tp)

        in_tp = [i*4 for i in in_per_worker_tp]
        sys_in_tp = [i*4 for i in sys_in_per_worker_tp]

        fig = plt.figure()
        ax1 = plt.subplot(111)
        l5, = ax1.plot(sys_in_tp, [int(row['p50']) for row in sys], label='sys p50', color=colors[0])
        l6, = ax1.plot(in_tp, [int(row['p50']) for row in kafka], label='kafka p50', color=colors[1])
        l7, = ax1.plot(sys_in_tp, [int(row['p99']) for row in sys], label='sys p99', ls='--', color=colors[0])
        l8, = ax1.plot(in_tp, [int(row['p99']) for row in kafka], label='kafka p99', ls='--', color=colors[1])

        ax1.set_xlabel('input throughput(events/s)')
        ax1.set_ylabel('event time latency(ms)')
        ax1.legend(loc=(0, 1.1), ncol=2, handles=[l5,l6,l7,l8])
        plt.title('Q' + str(experiment + 1))
        plt.savefig('comparisons/q' + str(experiment + 1) + '.png', bbox_inches='tight')
