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
    fig, axs = plt.subplots(4, 4, figsize=(28, 18), layout='constrained')
    handles = None
    letters=[f'({i})' for i in ascii_lowercase]
    print(axs)
    sys_dict = {}
    kafka_dict = {}
    ktos_p50_min_ratio = None
    ktos_p50_max_ratio = None
    ktos_p99_min_ratio = None
    ktos_p99_max_ratio = None

    atos_p50_min_ratio = None
    atos_p50_max_ratio = None
    atos_p99_min_ratio = None
    atos_p99_max_ratio = None
    stoa_p50_min_ratio = None
    stoa_p50_max_ratio = None

    for experiment in range(0, len(kafkas)):
        kafka = load(kafkas, experiment)
        sys = load(syss, experiment)
        twopc = load(twopcs, experiment)
        ackpt = load(alignchkpts, experiment)
        r2pc = load(remote_2pc, experiment)

        sys_in_per_worker_tp = [int(row['tps']) for row in sys]
        kafka_in_per_worker_tp = [int(row['tps']) for row in kafka]
        ackpt_in_per_worker_tp = [int(row['tps']) for row in ackpt]
        remote2pc_in_per_worker_tp = [int(row['tps']) for row in r2pc]
        sys_p99_over1 = None
        kafka_p99_over1 = None
        for row in sys:
            sys_dict[int(row['tps'])] = {"p50": int(row['p50']), "p99": int(row['p99'])}
            if int(row['p99']) > 1000 and sys_p99_over1 is None:
                sys_p99_over1 = int(row['tps'])
        for row in kafka:
            kafka_dict[int(row['tps'])] = {"p50": int(row['p50']), "p99": int(row['p99'])}
            if int(row['p99']) > 1000 and kafka_p99_over1 is None:
                kafka_p99_over1 = int(row['tps'])
        if sys_p99_over1 is None:
            sys_p99_over1 = sys_in_per_worker_tp[-1]
        if kafka_p99_over1 is None:
            kafka_p99_over1 = kafka_in_per_worker_tp[-1]
        print('Q' + str(experiment + 1))
        print(f"kafka p99 over 1s: {kafka_p99_over1}, epoch p99 over 1s: {sys_p99_over1}, ratio: {sys_p99_over1/kafka_p99_over1}")

        kafka_in_tp = [i*4 for i in kafka_in_per_worker_tp]
        sys_in_tp = [i*4 for i in sys_in_per_worker_tp]
        ackpt_in_tp = [i*4 for i in ackpt_in_per_worker_tp]
        r2pc_in_tp = [i*4 for i in remote2pc_in_per_worker_tp]

        sys_p50 = [int(row['p50']) for row in sys]
        sys_p99 = [int(row['p99']) for row in sys]
        twopc_p50 = np.array([int(row['p50']) for row in twopc])
        twopc_p99 = np.array([int(row['p99']) for row in twopc])
        ackpt_p50 = [int(row['p50']) for row in ackpt]
        ackpt_p99 = [int(row['p99']) for row in ackpt]
        kafka_p50 = [int(row['p50']) for row in kafka]
        kafka_p99 = [int(row['p99']) for row in kafka]

        r2pc_p50 = [int(row['p50']) for row in r2pc]
        r2pc_p99 = [int(row['p99']) for row in r2pc]

        print(f"sys tp: {sys_in_tp}") 
        print(f"sys p50: {sys_p50}")
        print(f"sys p99: {sys_p99}")
        sys_p50_arr = np.array(sys_p50)
        sys_p99_arr = np.array(sys_p99)
        print(f"kafka tp: {kafka_in_tp}")
        print(f"kafka p50: {kafka_p50}")
        print(f"kafka p99: {kafka_p99}")
        kafka_p50_ratio = []
        kafka_p99_ratio = []
        for tps in kafka_in_per_worker_tp:
            p50_ratio = round(kafka_dict[tps]["p50"]/sys_dict[tps]["p50"], 1)
            p99_ratio = round(kafka_dict[tps]["p99"]/sys_dict[tps]["p99"], 1)
            if kafka_dict[tps]["p50"] <= 1000 and experiment >= 2:
                if ktos_p50_min_ratio is None:
                    ktos_p50_min_ratio = p50_ratio
                if ktos_p50_max_ratio is None:
                    ktos_p50_max_ratio = p50_ratio
                ktos_p50_max_ratio = max(p50_ratio, ktos_p50_max_ratio)
                ktos_p50_min_ratio = min(p50_ratio, ktos_p50_min_ratio)
            if kafka_dict[tps]["p99"] <= 1000 and experiment >= 2:
                if ktos_p99_min_ratio is None:
                    ktos_p99_min_ratio = p99_ratio
                if ktos_p99_max_ratio is None:
                    ktos_p99_max_ratio = p99_ratio
                ktos_p99_max_ratio = max(p99_ratio, ktos_p99_max_ratio)
                ktos_p99_min_ratio = min(p99_ratio, ktos_p99_min_ratio)
            kafka_p50_ratio.append(p50_ratio)
            kafka_p99_ratio.append(p99_ratio)
        print(f"kafka/sys p50: {kafka_p50_ratio}")
        print(f"kafka/sys p99: {kafka_p99_ratio}")
        print(f"remote_2pc p50: {r2pc_p50}")
        print(f"remote_2pc p99: {r2pc_p99}")
        r2pc_p50_ratio = np.array(r2pc_p50)/sys_p50_arr
        r2pc_p99_ratio = np.array(r2pc_p99)/sys_p99_arr
        print(f"r2pc/sys p50: {r2pc_p50_ratio}")
        print(f"r2pc/sys p99: {r2pc_p99_ratio}")
        print(f"ackpt tp: {ackpt_in_tp}")
        print(f"alignchkpt p50: {ackpt_p50}")
        print(f"alignchkpt p99: {ackpt_p99}")
        ackpt_p50_arr = np.array(ackpt_p50)
        ackpt_p99_arr = np.array(ackpt_p99)
        sys_to_align_p50_ratio = sys_p50_arr / ackpt_p50_arr
        sys_to_align_p99_ratio = sys_p99_arr / ackpt_p99_arr
        align_to_sys_p50_ratio = ackpt_p50_arr / sys_p50_arr
        align_to_sys_p99_ratio = ackpt_p99_arr / sys_p99_arr
        print(f"sys/alignchkpt p50: {sys_to_align_p50_ratio}")
        print(f"sys/alignchkpt p99: {sys_to_align_p99_ratio}")
        print(f"alignchkpt/sys p50: {align_to_sys_p50_ratio}")
        print(f"alignchkpt/sys p99: {align_to_sys_p99_ratio}")
        for idx, r in enumerate(align_to_sys_p50_ratio):
            if r > 1 and ackpt_p50[idx] <= 1000 and sys_p50[idx] < 1000:
                if atos_p50_min_ratio is None:
                    atos_p50_min_ratio = r
                if atos_p50_max_ratio is None:
                    atos_p50_max_ratio = r
                atos_p50_min_ratio = min(r, atos_p50_min_ratio)
                atos_p50_max_ratio = max(r, atos_p50_max_ratio)
        for idx, r in enumerate(align_to_sys_p99_ratio):
            if r > 1 and ackpt_p99[idx] <= 1000 and sys_p99[idx] < 1000:
                if atos_p99_min_ratio is None:
                    atos_p99_min_ratio = r
                if atos_p99_max_ratio is None:
                    atos_p99_max_ratio = r
                atos_p99_min_ratio = min(r, atos_p99_min_ratio)
                atos_p99_max_ratio = max(r, atos_p99_max_ratio)
        for idx, r in enumerate(sys_to_align_p50_ratio):
            if r > 1 and ackpt_p50[idx] <= 1000 and sys_p50[idx] < 1000:
                if stoa_p50_min_ratio is None:
                    stoa_p50_min_ratio = r
                if stoa_p50_max_ratio is None:
                    stoa_p50_max_ratio = r
                stoa_p50_min_ratio = min(r, stoa_p50_min_ratio)
                stoa_p50_max_ratio = max(r, stoa_p50_max_ratio)

        target_idx = 0
        assert len(sys_in_tp) == len(r2pc_in_tp)
        print(f"ratio to 1st p99: {[i/sys_p99[0] for i in sys_p99]}")
        if experiment == 0 or experiment == 1:
            allow=0.25
        else:
            allow=0.15
        lat_max = sys_p99[0] * (1+allow)
        for idx, t in enumerate(sys_p99):
            if t <= 400 and sys_p50[idx] <= 400 and t <= lat_max and abs(r2pc_p99_ratio[idx]-1) <= allow:
                target_idx = idx
        print(f"idx: {target_idx}, tp: {sys_in_per_worker_tp[target_idx]}, epoch_p50: {sys_p50[target_idx]}, epoch_p99: {sys_p99[target_idx]}")

        marksize=14

        r = (experiment // 4) * 2
        c = experiment % 4
        ax1 = axs[r][c]
        ax2 = axs[r+1][c]
        l1, = ax1.plot(sys_in_tp, sys_p50, label='Impeller p50',  marker=markers[0],color=colors[0], markersize=marksize)
        l3, = ax2.plot(sys_in_tp, sys_p99, label='Impeller p99', ls='--', marker=markers[0], color=colors[0], markersize=marksize)
        l2, = ax1.plot(kafka_in_tp, [int(row['p50']) for row in kafka], label='Kafka Streams p50',  marker=markers[1],color=colors[1], markersize=marksize)
        l4, = ax2.plot(kafka_in_tp, [int(row['p99']) for row in kafka], label='Kafka Streams p99', ls='--', marker=markers[1], color=colors[1], markersize=marksize)
        # l5, = ax1.plot(sys_in_tp, twopc_p50, label='2pc on Impeller p50',  marker=markers[3], color=colors[3], markersize=marksize)
        # l6, = ax1.plot(sys_in_tp, twopc_p99, label='2pc on Impeller p99',  ls='--', marker=markers[3],color=colors[3], markersize=marksize)
        l7, = ax1.plot(r2pc_in_tp, r2pc_p50, label='Kafka Streams transaction on Impeller p50',  marker=markers[3], color=colors[3], markersize=marksize)
        l8, = ax2.plot(r2pc_in_tp, r2pc_p99, label='Kafka Streams transaction on Impeller p99',  ls='--', marker=markers[3],color=colors[3], markersize=marksize)
        l11, = ax1.plot(ackpt_in_tp, ackpt_p50, label='Align chkpt on Impeller p50',  marker=markers[4], color=colors[4], markersize=marksize)
        l12, = ax2.plot(ackpt_in_tp, ackpt_p99, label='Align chkpt on Impeller p99',  ls='--', marker=markers[4],color=colors[4], markersize=marksize)
        lines = [l1, l2, l3, l4, l7, l8, l11, l12]
        for l in lines:
            l.set_linewidth(3)

        # ax1.set_xlabel('input throughput(events/s)', fontsize=16)
        # ax1.set_ylabel('event time latency(ms)', fontsize=16)
        if experiment == 7:
            handles = [l1, l3, l2, l4, l7, l8, l11, l12]
            # ax1.legend(loc=(3, 1.05), ncol=2, handles=[l1, l5, l2, l3, l6, l4], handlelength=3, fontsize=11)
        ax1.set_title(f'{letters[experiment]} Q{experiment+1}', fontsize=22)
        ax1.tick_params(labelsize=20)
        ax1.xaxis.set_major_formatter(ticker.EngFormatter(sep=""))
        ax2.tick_params(labelsize=20)
        ax2.xaxis.set_major_formatter(ticker.EngFormatter(sep=""))
        ax1.set_xticks(sys_in_tp)
        ax2.set_xticks(sys_in_tp)
        ax1.xaxis.set_tick_params(labelrotation=45)
        ax2.xaxis.set_tick_params(labelrotation=45)

        if experiment < 2:
            ax1.set_ylim([0, 60])
            ax2.set_ylim([0, 60])
        else:
            ax1.set_ylim([0, 1000])
            ax2.set_ylim([0, 1000])

        # plt.title('Q' + str(experiment + 1))
    fig.legend(ncol=4, handles=handles, fontsize=22, loc='upper center', bbox_to_anchor=(0.5, 1.08))
    fig.supxlabel('Input throughput(events/s)', fontsize=22)
    fig.supylabel('Event time latency(ms)', fontsize=22)
    plt.savefig('q1-8.pdf', bbox_inches='tight', pad_inches = 0)
    print(f"kafka/sys p50 min ratio: {ktos_p50_min_ratio}")
    print(f"kafka/sys p50 max ratio: {ktos_p50_max_ratio}")
    print(f"kafka/sys p99 min ratio: {ktos_p99_min_ratio}")
    print(f"kafka/sys p99 max ratio: {ktos_p99_max_ratio}")
    print()
    print(f"align/sys p50 min ratio: {atos_p50_min_ratio}")
    print(f"align/sys p50 max ratio: {atos_p50_max_ratio}")
    print(f"sys/align p50 min ratio: {stoa_p50_min_ratio}")
    print(f"sys/align p50 max ratio: {stoa_p50_max_ratio}")

    print(f"align/sys p99 min ratio: {atos_p99_min_ratio}")
    print(f"align/sys p99 max ratio: {atos_p99_max_ratio}")
