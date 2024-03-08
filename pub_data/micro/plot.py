import matplotlib.pyplot as plt
import subprocess
import csv
headers = ['del', 'tps', 'trials', 'pts', 'avg', 'std', 'min', 'p25', 'p50', 'p75', 'p90', 'p99', 'max']

def load(exp_dir):
    rows = subprocess.run(["./latency", "query", exp_dir], stdout=subprocess.PIPE)
    rows = rows.stdout.decode('utf-8').strip().split('\n')
    rows = [row for row in csv.DictReader(rows, fieldnames=headers) 
            if (row['del'] == 'eo' or row['del'] == '2pc' or row['del'] == 'align_chkpt') and int(row['tps']) in [24000]]
    rows.sort(key=lambda row: int(row['tps']))
    return rows


def get_tps(ins, m):
    tps = []
    for i in ins:
        v = load(f"./{m}/{i}ins/q8-180s-0swarm-100ms-src100ms/")
        tps.append(v[0])
    return tps

colors = ['blue', 'orange', 'green', 'purple', 'olive']


def main():
    ins=[4, 8, 16]
    fig = plt.figure(figsize=(7, 3.2), layout='constrained')
    ax1 = plt.subplot(111)
    impeller_tps = get_tps(ins, 'impeller')
    twopc_tps = get_tps(ins, '2pc')
    align_chkpt_tps = get_tps(ins, 'align_chkpt')

    impeller_p50 = [int(row['p50']) for row in impeller_tps]
    impeller_p99 = [int(row['p99']) for row in impeller_tps]
    twopc_p50 = [int(row['p50']) for row in twopc_tps]
    twopc_p99 = [int(row['p99']) for row in twopc_tps]
    align_chkpt_p50 = [int(row['p50']) for row in align_chkpt_tps]
    align_chkpt_p99 = [int(row['p99']) for row in align_chkpt_tps]
    print(f'impeller p50: {impeller_p50}')
    print(f'impeller p99: {impeller_p99}')
    print(f'2pc p50: {twopc_p50}')
    print(f'2pc p99: {twopc_p99}')
    print(f'align_chkpt p50: {align_chkpt_p50}')
    print(f'align_chkpt p99: {align_chkpt_p99}')

    l1, = ax1.plot(ins, impeller_p50, label='Impeller p50', marker='o', color=colors[0])
    l2, = ax1.plot(ins, impeller_p99, label='Impeller p99', ls='--', marker='o', color=colors[0])
    l3, = ax1.plot(ins, twopc_p50, label='2pc on Impeller p50', marker='s', color=colors[1])
    l4, = ax1.plot(ins, twopc_p99, label='2pc on Impeller p99', ls='--', marker='s', color=colors[1])
    l5, = ax1.plot(ins, align_chkpt_p50, label='Align chkpt on Impeller p50', marker='p', color=colors[4])
    l6, = ax1.plot(ins, align_chkpt_p99, label='Align chkpt on Impeller p99', ls='--', marker='p', color=colors[4])
    handles = [l1, l2, l3, l4, l5, l6]

    ax1.tick_params(labelsize=16)
    ax1.set_xlabel('Input throughput(events/s)', fontsize=16)
    ax1.set_ylabel('Event time latency(ms)', fontsize=16)
    fig.legend(ncol=2, handles=handles, fontsize=16, loc='upper center', bbox_to_anchor=(0.5, 1.4))
    plt.savefig('q8_4-16ins.pdf', bbox_inches='tight')


if __name__ == "__main__":
    main()
