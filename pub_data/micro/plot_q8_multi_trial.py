import matplotlib.pyplot as plt
import subprocess
import csv
import sys
import os
import pprint
import pickle

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from fig_const import markers, colors, headers
from plot import load


def main():
    d = "./multi_instances_0extra_kvrocks_4xlarge3"
    ins=[4, 8, 16, 28, 32]
    tps=[28000, 14000, 7000, 4000, 3500]
    twopc_p50 = []
    twopc_p99 = []
    impeller_p50 = []
    impeller_p99 = []
    for i in ins:
        name = f"{d}/{i}ins/q8-180s-0swarm-100ms-src100ms/2/"
        rows = load(name)
        for row in rows:
            if row['del'] == "2pc":
                twopc_p50.append(int(row['p50']))
                twopc_p99.append(int(row['p99']))
            elif row['del'] == "eo":
                impeller_p50.append(int(row['p50']))
                impeller_p99.append(int(row['p99']))

    print(f'{ins}')
    print(f'impeller p50: {impeller_p50}')
    print(f'impeller p99: {impeller_p99}')
    print(f'2PC p50: {twopc_p50}')
    print(f'2PC p99: {twopc_p99}')

    fig = plt.figure(figsize=(7, 3.2), layout='constrained')
    ax1 = plt.subplot(111)
    l1, = ax1.plot(ins, impeller_p50, label='Impeller p50', marker=markers[0], color=colors[0])
    l2, = ax1.plot(ins, impeller_p99, label='Impeller p99', ls='--', marker=markers[0], color=colors[0])
    l3, = ax1.plot(ins, twopc_p50, label='2PC on Impeller p50', marker=markers[3], color=colors[3])
    l4, = ax1.plot(ins, twopc_p99, label='2PC on Impeller p99', ls='--', marker=markers[3], color=colors[3])
    handles = [l1, l2, l3, l4]

    ax1.tick_params(labelsize=16)
    ax1.set_xticks(ins)
    ax1.set_xlabel('Number of streams', fontsize=16)
    ax1.set_ylabel('Event time latency(ms)', fontsize=16)
    fig.legend(ncol=2, handles=handles, fontsize=16, loc='upper center', bbox_to_anchor=(0.5, 1.3))
    plt.savefig("q8_4-32_0extra_4xlarge.pdf", bbox_inches='tight')

    stat_dir="./multi_instances_0extra_kvrocks_4xlarge3/q8_180s_0swarm_100ms_src100ms_stats/2"

    groupby_cmt_p50 = []
    groupby_cmt_p99 = []
    groupby_cmt_max = []
    groupby_mark_p50 = []
    groupby_mark_p99 = []
    groupby_mark_max = []

    join_cmt_p50 = []
    join_cmt_p99 = []
    join_cmt_max = []

    join_mark_p50 = []
    join_mark_p99 = []
    join_mark_max = []

    groupby_fa_2pc_p50 = []
    groupby_fa_2pc_p99 = []
    groupby_fa_2pc_max = []

    groupby_fa_epoch_p50 = []
    groupby_fa_epoch_p99 = []
    groupby_fa_epoch_max = []

    join_fa_2pc_p50 = []
    join_fa_2pc_p99 = []
    join_fa_2pc_max = []

    join_fa_epoch_p50 = []
    join_fa_epoch_p99 = []
    join_fa_epoch_max = []

    waitPrevCmt_p50 = []
    waitPrevCmt_p99 = []
    waitPrevCmt_max = []

    join_waitPrevCmt_p50 = []
    join_waitPrevCmt_p99 = []
    join_waitPrevCmt_max = []

    groupby_waitPrevCmt_p50 = []
    groupby_waitPrevCmt_p99 = []
    groupby_waitPrevCmt_max = []

    for tp in tps:
        with open(os.path.join(stat_dir, f"{tp}tps_2pc_stats.pickle"), "rb") as f:
            stat_2pc = pickle.load(f)
        with open(os.path.join(stat_dir, f"{tp}tps_epoch_stats.pickle"), "rb") as f:
            stat_epoch = pickle.load(f)
        groupby_cmt_p50.append(stat_2pc["txnCommitTime"][tp]['q8GroupBy']['p50']/1000)
        groupby_cmt_p99.append(stat_2pc["txnCommitTime"][tp]['q8GroupBy']['p99']/1000)
        groupby_cmt_max.append(stat_2pc["txnCommitTime"][tp]['q8GroupBy']['max']/1000)
        groupby_mark_p50.append(stat_epoch["progress_mark"][tp]['q8GroupBy']['p50']/1000)
        groupby_mark_p99.append(stat_epoch["progress_mark"][tp]['q8GroupBy']['p99']/1000)
        groupby_mark_max.append(stat_epoch["progress_mark"][tp]['q8GroupBy']['max']/1000)

        groupby_fa_2pc_p50.append(stat_2pc["flushStage"][tp]['q8GroupBy']['p50']/1000)
        groupby_fa_2pc_p99.append(stat_2pc["flushStage"][tp]['q8GroupBy']['p99']/1000)
        groupby_fa_2pc_max.append(stat_2pc["flushStage"][tp]['q8GroupBy']['max']/1000)
        groupby_fa_epoch_p50.append(stat_epoch["flushStage"][tp]['q8GroupBy']['p50']/1000)
        groupby_fa_epoch_p99.append(stat_epoch["flushStage"][tp]['q8GroupBy']['p99']/1000)
        groupby_fa_epoch_max.append(stat_epoch["flushStage"][tp]['q8GroupBy']['max']/1000)

        join_cmt_p50.append(stat_2pc["txnCommitTime"][tp]['q8JoinStream']['p50']/1000)
        join_cmt_p99.append(stat_2pc["txnCommitTime"][tp]['q8JoinStream']['p99']/1000)
        join_cmt_max.append(stat_2pc["txnCommitTime"][tp]['q8JoinStream']['max']/1000)
        join_mark_p50.append(stat_epoch["progress_mark"][tp]['q8JoinStream']['p50']/1000)
        join_mark_p99.append(stat_epoch["progress_mark"][tp]['q8JoinStream']['p99']/1000)
        join_mark_max.append(stat_epoch["progress_mark"][tp]['q8JoinStream']['max']/1000)

        join_fa_2pc_p50.append(stat_2pc["flushStage"][tp]['q8JoinStream']['p50']/1000)
        join_fa_2pc_p99.append(stat_2pc["flushStage"][tp]['q8JoinStream']['p99']/1000)
        join_fa_2pc_max.append(stat_2pc["flushStage"][tp]['q8JoinStream']['max']/1000)
        join_fa_epoch_p50.append(stat_epoch["flushStage"][tp]['q8JoinStream']['p50']/1000)
        join_fa_epoch_p99.append(stat_epoch["flushStage"][tp]['q8JoinStream']['p99']/1000)
        join_fa_epoch_max.append(stat_epoch["flushStage"][tp]['q8JoinStream']['max']/1000)

        waitPrevCmt_p50.append(stat_2pc['waitPrevTxnInCmt'][tp]["all"]['p50']/1000)
        waitPrevCmt_p99.append(stat_2pc['waitPrevTxnInCmt'][tp]["all"]['p99']/1000)
        waitPrevCmt_max.append(stat_2pc['waitPrevTxnInCmt'][tp]["all"]['max']/1000)

        join_waitPrevCmt_p50.append(stat_2pc['waitPrevTxnInCmt'][tp]["q8JoinStream"]['p50']/1000)
        join_waitPrevCmt_p99.append(stat_2pc['waitPrevTxnInCmt'][tp]["q8JoinStream"]['p99']/1000)
        join_waitPrevCmt_max.append(stat_2pc['waitPrevTxnInCmt'][tp]["q8JoinStream"]['max']/1000)

        groupby_waitPrevCmt_p50.append(stat_2pc['waitPrevTxnInCmt'][tp]["q8GroupBy"]['p50']/1000)
        groupby_waitPrevCmt_p99.append(stat_2pc['waitPrevTxnInCmt'][tp]["q8GroupBy"]['p99']/1000)
        groupby_waitPrevCmt_max.append(stat_2pc['waitPrevTxnInCmt'][tp]["q8GroupBy"]['max']/1000)

    print("mark/cmt (ms)")
    print(f"q8GroupBy 2pc p50: {groupby_cmt_p50}")
    print(f"q8GroupBy 2pc p99: {groupby_cmt_p99}")
    print(f"q8GroupBy 2pc max: {groupby_cmt_max}")

    print(f"q8GroupBy epoch p50: {groupby_mark_p50}")
    print(f"q8GroupBy epoch p99: {groupby_mark_p99}")
    print(f"q8GroupBy epoch max: {groupby_mark_max}")

    print(f"q8JoinStream 2pc p50: {join_cmt_p50}")
    print(f"q8JoinStream 2pc p99: {join_cmt_p99}")
    print(f"q8JoinStream 2pc max: {join_cmt_max}")
    print(f"q8JoinStream epoch p50: {join_mark_p50}")
    print(f"q8JoinStream epoch p99: {join_mark_p99}")
    print(f"q8JoinStream epoch max: {join_mark_max}")

    print("flush (ms)")
    print(f"q8GroupBy 2pc p50: {groupby_fa_2pc_p50}")
    print(f"q8GroupBy 2pc p99: {groupby_fa_2pc_p99}")
    print(f"q8GroupBy 2pc max: {groupby_fa_2pc_max}")
    print(f"q8GroupBy epoch p50: {groupby_fa_epoch_p50}")
    print(f"q8GroupBy epoch p99: {groupby_fa_epoch_p99}")
    print(f"q8GroupBy epoch max: {groupby_fa_epoch_max}")

    print(f"q8JoinStream 2pc p50: {join_fa_2pc_p50}")
    print(f"q8JoinStream 2pc p99: {join_fa_2pc_p99}")
    print(f"q8JoinStream 2pc max: {join_fa_2pc_p99}")
    print(f"q8JoinStream epoch p50: {join_fa_epoch_p50}")
    print(f"q8JoinStream epoch p99: {join_fa_epoch_p99}")
    print(f"q8JoinStream epoch max: {join_fa_epoch_p99}")

    print("waitPrevInCmt (ms)")
    print(f"2pc p50: {waitPrevCmt_p50}")
    print(f"2pc p99: {waitPrevCmt_p99}")
    print(f"2pc max: {waitPrevCmt_p99}")

    print("groupby waitPrevInCmt (ms)")
    print(f"2pc p50: {groupby_waitPrevCmt_p50}")
    print(f"2pc p99: {groupby_waitPrevCmt_p99}")
    print(f"2pc max: {groupby_waitPrevCmt_p99}")

    print("join waitPrevInCmt (ms)")
    print(f"2pc p50: {join_waitPrevCmt_p50}")
    print(f"2pc p99: {join_waitPrevCmt_p99}")
    print(f"2pc max: {join_waitPrevCmt_p99}")


if __name__ == "__main__":
    main()
