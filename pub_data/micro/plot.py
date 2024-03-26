import matplotlib.pyplot as plt
import subprocess
import csv
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from fig_const import markers, colors, headers

def load(exp_dir):
    rows = subprocess.run(["./latency", "query", exp_dir], stdout=subprocess.PIPE)
    rows = rows.stdout.decode('utf-8').strip().split('\n')
    rows = [row for row in csv.DictReader(rows, fieldnames=headers) 
            if (row['del'] == 'eo' or row['del'] == '2pc' or row['del'] == 'align_chkpt') and int(row['tps']) in [28000, 14000, 7000, 4000, 3500, 2800]]
    rows.sort(key=lambda row: int(row['tps']))
    return rows


def get_tps(ins, m):
    tps = []
    for i in ins:
        v = load(f"{m}/{i}ins/q8-180s-0swarm-100ms-src100ms/")
        tps.append(v[0])
    return tps


def main():
    # plot('./multi_instances_0extra_kvrocks', 'q8_4-32_0extra.pdf')
    # plot('./multi_instances_200extra_kvrocks', 'q8_4-32_200extra.pdf')
    plot('./multi_instances_0extra_kvrocks_4xlarge3', 'q8_4-32_0extra_4xlarge.pdf')


def plot(dir, fname):
    ins=[4, 8, 16, 28, 32]
    fig = plt.figure(figsize=(7, 3.2), layout='constrained')
    ax1 = plt.subplot(111)
    impeller_tps = get_tps(ins, f'{dir}/impeller/')
    twopc_tps = get_tps(ins, f'{dir}/2pc/')
    # align_chkpt_tps = get_tps(ins, f'{dir}/align_chkpt/')

    impeller_p50 = [int(row['p50']) for row in impeller_tps]
    impeller_p99 = [int(row['p99']) for row in impeller_tps]
    twopc_p50 = [int(row['p50']) for row in twopc_tps]
    twopc_p99 = [int(row['p99']) for row in twopc_tps]
    # align_chkpt_p50 = [int(row['p50']) for row in align_chkpt_tps]
    # align_chkpt_p99 = [int(row['p99']) for row in align_chkpt_tps]
    print(f'impeller p50: {impeller_p50}')
    print(f'impeller p99: {impeller_p99}')
    print(f'2PC p50: {twopc_p50}')
    print(f'2PC p99: {twopc_p99}')
    # print(f'align_chkpt p50: {align_chkpt_p50}')
    # print(f'align_chkpt p99: {align_chkpt_p99}')

    l1, = ax1.plot(ins, impeller_p50, label='Impeller p50', marker=markers[0], color=colors[0])
    l2, = ax1.plot(ins, impeller_p99, label='Impeller p99', ls='--', marker=markers[0], color=colors[0])
    l3, = ax1.plot(ins, twopc_p50, label='2PC on Impeller p50', marker=markers[3], color=colors[3])
    l4, = ax1.plot(ins, twopc_p99, label='2PC on Impeller p99', ls='--', marker=markers[3], color=colors[3])
    # l5, = ax1.plot(ins, align_chkpt_p50, label='Align chkpt on Impeller p50', marker='p', color=colors[4])
    # l6, = ax1.plot(ins, align_chkpt_p99, label='Align chkpt on Impeller p99', ls='--', marker='p', color=colors[4])
    # handles = [l1, l2, l3, l4, l5, l6]
    handles = [l1, l2, l3, l4]

    ax1.tick_params(labelsize=16)
    ax1.set_xticks(ins)
    ax1.set_xlabel('Number of streams', fontsize=16)
    ax1.set_ylabel('Event time latency(ms)', fontsize=16)
    fig.legend(ncol=2, handles=handles, fontsize=16, loc='upper center', bbox_to_anchor=(0.5, 1.3))
    plt.savefig(fname, bbox_inches='tight')


if __name__ == "__main__":
    main()
