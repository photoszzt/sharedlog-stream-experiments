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
    with open('./fanout/fanout_epoch.pickle', "rb") as f:
        fanout_epoch = pickle.load(f)
    with open('./fanout/fanout_2pc.pickle', "rb") as f:
        fanout_2pc = pickle.load(f)
    with open("./fanout/fanout_2pc_stats.pickle", "rb") as f:
        stats_2pc = pickle.load(f)
    with open("./fanout/fanout_epoch_stats.pickle", "rb") as f:
        stats_epoch = pickle.load(f)
    epoch_keys = sorted([k for k in fanout_epoch.keys() if k[1] != 128])
    twopc_keys = sorted([k for k in fanout_2pc.keys() if k[1] != 128])
    fanouts_epoch = [fanout for (tps, fanout) in epoch_keys]
    fanouts_2pc = [fanout for (tps, fanout) in twopc_keys]
    impeller_p50 = [fanout_epoch[k]['p50'] for k in epoch_keys]
    impeller_p99 = [fanout_epoch[k]['p99'] for k in epoch_keys]
    twopc_p50 = [fanout_2pc[k]['p50'] for k in twopc_keys]
    twopc_p99 = [fanout_2pc[k]['p99'] for k in twopc_keys]
    p50_ratio = np.array(twopc_p50) / np.array(impeller_p50)
    p99_ratio = np.array(twopc_p99) / np.array(impeller_p99)
    print(f'impeller p50: {impeller_p50}')
    print(f'impeller p99: {impeller_p99}')
    print(f'2pc p50: {twopc_p50}')
    print(f'2pc p99: {twopc_p99}')
    print(f'2pc/impeller p50: {p50_ratio}')
    print(f'2pc/impeller p99: {p99_ratio}')
    
    k_cmt, mark_twopc_p50, mark_twopc_p99 = get_kv_arr(stats_2pc['txnCommitTime']['summary'])
    k_mark, mark_impeller_p50, mark_impeller_p99 = get_kv_arr(stats_epoch['progress_mark']['summary'])
    print("mark/commit(ms)")
    print(f"{k_cmt}")
    print(f"twopc commit p50: {mark_twopc_p50}")
    print(f"twopc commit p99: {mark_twopc_p99}")
    print(f"{k_mark}")
    print(f"impeller commit p50: {mark_impeller_p50}")
    print(f"impeller commit p99: {mark_impeller_p99}")

    fig = plt.figure(figsize=(6, 3.2), layout='constrained')
    l1, = plt.plot(fanouts_epoch, impeller_p50, label='Impeller p50', marker=markers[0], color=colors[0])
    l2, = plt.plot(fanouts_epoch, impeller_p99, label='Impeller p99', ls='--', marker=markers[0], color=colors[0])
    l3, = plt.plot(fanouts_2pc, twopc_p50, label='2pc on Impeller p50', marker=markers[3], color=colors[3])
    l4, = plt.plot(fanouts_2pc, twopc_p99, label='2pc on Impeller p99', ls='--', marker=markers[3], color=colors[3])
    # axs[1].plot(k_mark, mark_impeller_p50, label='Impeller p50', marker=markers[0], color=colors[0])
    # axs[1].plot(k_mark, mark_impeller_p99, label='Impeller p99', ls='--', marker=markers[0], color=colors[0])
    # axs[1].plot(k_cmt, mark_twopc_p50, label='2pc on Impeller p50', marker=markers[3], color=colors[3])
    # axs[1].plot(k_cmt, mark_twopc_p99, label='2pc on Impeller p99', ls='--', marker=markers[3], color=colors[3])
    plt.xticks(fanouts_epoch)
    # axs[1].set_xticks(k_mark)

    handles = [l1, l2, l3, l4]
    plt.tick_params(labelsize=16)
    # axs[1].tick_params(labelsize=16)
    plt.xlabel('Number of sink substreams', fontsize=16)
    plt.ylabel('Event time latency(ms)', fontsize=16)
    # axs[1].set_ylabel('Mark/Commit latency(ms)', fontsize=16)
    plt.ylim(0, 300)
    fig.legend(ncol=2, handles=handles, fontsize=16, loc='upper center', bbox_to_anchor=(0.5, 1.3))
    plt.savefig("fanout.pdf", bbox_inches='tight')

if __name__ == '__main__':
    main()
