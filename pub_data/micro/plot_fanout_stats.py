import pickle
import pprint
import matplotlib.pyplot as plt
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from fig_const import markers, colors, headers


def get_kv_arr(arr):
    k = []
    p50_arr = []
    p99_arr = []
    for ((tps, fanout), p50, p99) in arr:
        k.append(fanout)
        p50_arr.append(p50/1000)
        p99_arr.append(p99/1000)
    return k, p50_arr, p99_arr


def plot_fig(impeller_x, impeller_p50, impeller_p99, twopc_x, twopc_p50, twopc_p99, fname):
    fig = plt.figure(figsize=(7, 3.2), layout='constrained')
    l1, = plt.plot(impeller_x, impeller_p50, label='Impeller p50', marker=markers[0], color=colors[0])
    l2, = plt.plot(impeller_x, impeller_p99, label='Impeller p99', ls='--', marker=markers[0], color=colors[0])
    l3, = plt.plot(twopc_x, twopc_p50, label='2pc on Impeller p50', marker=markers[3], color=colors[3])
    l4, = plt.plot(twopc_x, twopc_p99, label='2pc on Impeller p99', ls='--', marker=markers[3], color=colors[3])
    handles = [l1, l2, l3, l4]

    plt.tick_params(labelsize=16)
    plt.xlabel('Number of sink substreams', fontsize=16)
    plt.ylabel('Event time latency(ms)', fontsize=16)
    fig.legend(ncol=2, handles=handles, fontsize=16, loc='upper center', bbox_to_anchor=(0.5, 1.3))
    plt.savefig(fname, bbox_inches='tight')



def main():
    with open("./fanout/fanout_2pc_stats.pickle", "rb") as f:
        stats_2pc = pickle.load(f)
    with open("./fanout/fanout_epoch_stats.pickle", "rb") as f:
        stats_epoch = pickle.load(f)
    cmt_st = stats_2pc['txnCommitTime']['summary']
    mark_st = stats_epoch['progress_mark']['summary']

    k_cmt, twopc_p50, twopc_p99 = get_kv_arr(stats_2pc['txnCommitTime']['summary'])
    k_mark, impeller_p50, impeller_p99 = get_kv_arr(stats_epoch['progress_mark']['summary'])
    print("mark time(ms)")
    print(f"{k_cmt}")
    print(f"twopc commit p50: {twopc_p50}")
    print(f"twopc commit p99: {twopc_p99}")
    print(f"{k_mark}")
    print(f"impeller commit p50: {impeller_p50}")
    print(f"impeller commit p99: {impeller_p99}")
    plot_fig(k_mark, impeller_p50, impeller_p99, k_cmt, twopc_p50, twopc_p99, 'fanout_mark.pdf')

    k_cmt, twopc_p50, twopc_p99 = get_kv_arr(stats_2pc['flush_all']['summary'])
    k_mark, impeller_p50, impeller_p99 = get_kv_arr(stats_epoch['flush_all']['summary'])
    print("flush all(ms)")
    print(f"{k_cmt}")
    print(f"twopc commit p50: {twopc_p50}")
    print(f"twopc commit p99: {twopc_p99}")
    print(f"{k_mark}")
    print(f"impeller commit p50: {impeller_p50}")
    print(f"impeller commit p99: {impeller_p99}")
    plot_fig(k_mark, impeller_p50, impeller_p99, k_cmt, twopc_p50, twopc_p99, 'fanout_flush_all.pdf')

    k_cmt, twopc_p50, twopc_p99 = get_kv_arr(stats_2pc['flush_at_least_one']['summary'])
    k_mark, impeller_p50, impeller_p99 = get_kv_arr(stats_epoch['flush_at_least_one']['summary'])
    print("flush at least one(ms)")
    print(f"{k_cmt}")
    print(f"twopc commit p50: {twopc_p50}")
    print(f"twopc commit p99: {twopc_p99}")
    print(f"{k_mark}")
    print(f"impeller commit p50: {impeller_p50}")
    print(f"impeller commit p99: {impeller_p99}")
    plot_fig(k_mark, impeller_p50, impeller_p99, k_cmt, twopc_p50, twopc_p99, 'fanout_flush_at_least_one.pdf')


if __name__ == '__main__':
    main()
