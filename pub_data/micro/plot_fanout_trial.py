import pickle
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from fig_const import markers, colors, headers
from plot_fanout_stats import get_kv_arr

def main():
    fanouts = [8, 16, 32, 64, 128]
    impeller_p50 = []
    impeller_p99 = []
    twopc_p50 = []
    twopc_p99 = []

    impeller_mark_p50 = []
    impeller_mark_p99 = []
    twopc_cmt_p50 = []
    twopc_cmt_p99 = []

    waitPrevTxnInCmt_p50 = []
    waitPrevTxnInCmt_p99 = []
    waitPrevTxnInPush_p50 = []
    waitPrevTxnInPush_p99 = []
    
    for fanout in fanouts:
        k = (64000, fanout)
        with open(f"./fanout/8/64000tps_2pc_fanout_{fanout}.pickle", "rb") as f:
            st = pickle.load(f)
            twopc_p50.append(st[k]["p50"])
            twopc_p99.append(st[k]["p99"])
        with open(f"./fanout/5/64000tps_epoch_fanout_{fanout}.pickle", "rb") as f:
            st = pickle.load(f)
            impeller_p50.append(st[k]["p50"])
            impeller_p99.append(st[k]["p99"])
        with open(f"./fanout/8/64000tps_2pc_fanout_{fanout}_stats.pickle", "rb") as f:
            st = pickle.load(f)
            twopc_cmt_p50.append(st["txnCommitTime"][k]["all"]["p50"]/1000)
            twopc_cmt_p99.append(st["txnCommitTime"][k]["all"]["p99"]/1000)
            waitPrevTxnInCmt_p50.append(st["waitPrevTxnInCmt"][k]["all"]["p50"]/1000)
            waitPrevTxnInCmt_p99.append(st["waitPrevTxnInCmt"][k]["all"]["p99"]/1000)
            if k in st["waitPrevTxnInPush"]:
                waitPrevTxnInPush_p50.append(st["waitPrevTxnInPush"][k]["all"]["p50"]/1000)
                waitPrevTxnInPush_p99.append(st["waitPrevTxnInPush"][k]["all"]["p99"]/1000)
        with open(f"./fanout/5/64000tps_epoch_fanout_{fanout}_stats.pickle", "rb") as f:
            st = pickle.load(f)
            impeller_mark_p50.append(st["progress_mark"][k]["all"]["p50"]/1000)
            impeller_mark_p99.append(st["progress_mark"][k]["all"]["p99"]/1000)

    p50_ratio = np.array(twopc_p50) / np.array(impeller_p50)
    p99_ratio = np.array(twopc_p99) / np.array(impeller_p99)
    print(f'impeller p50: {impeller_p50}')
    print(f'impeller p99: {impeller_p99}')
    print(f'2pc p50: {twopc_p50}')
    print(f'2pc p99: {twopc_p99}')
    print(f'2pc/impeller p50: {p50_ratio}')
    print(f'2pc/impeller p99: {p99_ratio}')
    fig = plt.figure(figsize=(6, 3.2), layout='constrained')
    l1, = plt.plot(fanouts, impeller_p50, label='Impeller p50', marker=markers[0], color=colors[0])
    l2, = plt.plot(fanouts, impeller_p99, label='Impeller p99', ls='--', marker=markers[0], color=colors[0])
    l3, = plt.plot(fanouts, twopc_p50, label='2pc on Impeller p50', marker=markers[3], color=colors[3])
    l4, = plt.plot(fanouts, twopc_p99, label='2pc on Impeller p99', ls='--', marker=markers[3], color=colors[3])
    plt.xticks(fanouts)
    handles = [l1, l2, l3, l4]
    plt.tick_params(labelsize=16)
    plt.xlabel('Number of sink substreams', fontsize=16)
    plt.ylabel('Event time latency(ms)', fontsize=16)
    plt.ylim(0, 300)
    fig.legend(ncol=2, handles=handles, fontsize=16, loc='upper center', bbox_to_anchor=(0.5, 1.3))
    plt.savefig("fanout.pdf", bbox_inches='tight')

    print()
    print("progress mark(ms)")
    print(f'impeller p50: {impeller_mark_p50}')
    print(f'impeller p99: {impeller_mark_p99}')
    print()

    print("txnCommitTime(ms)")
    print(f'2pc p50: {twopc_cmt_p50}')
    print(f'2pc p99: {twopc_cmt_p99}')

    mark_p50_ratio = np.array(twopc_cmt_p50) / np.array(impeller_mark_p50)
    mark_p99_ratio = np.array(twopc_cmt_p99) / np.array(impeller_mark_p99)
    print(f'2pc/impeller mark p50: {mark_p50_ratio}')
    print(f'2pc/impeller mark p99: {mark_p99_ratio}')

    print()
    print(f"waitPrevTxnInCmt p50: {waitPrevTxnInCmt_p50}")
    print(f"waitPrevTxnInCmt p99: {waitPrevTxnInCmt_p99}")

    print(f"waitPrevTxnInPush p50: {waitPrevTxnInPush_p50}")
    print(f"waitPrevTxnInPush p99: {waitPrevTxnInPush_p99}")


if __name__ == '__main__':
    main()
