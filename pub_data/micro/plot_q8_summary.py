import json
import os
import sys
import matplotlib.pyplot as plt
import pprint
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from fig_const import markers, colors, headers

tps_map = {
    "4":  28000,
    "8":  14000,
    "16": 7000,
    "28": 4000,
    "32": 3500,
    "40": 2800,
}

metric_dir = "q8_metrics_0extra_4xlarge"
metric_file = "./q8_multistream_stats_0extra_4xlarge.json"


def main():
    with open(metric_file, "r") as f:
        stats = json.load(f)
    ins = ["4", "8", "16", "28", "32"]
    plt.figure(figsize=(7, 3), layout="constrained")
    epoch_fa_p50 = [stats[i]['epoch']['progress_mark']['summary'][0][1]/1000 for i in ins]
    epoch_fa_p99 = [stats[i]['epoch']['progress_mark']['summary'][0][2]/1000 for i in ins]
    twopc_fa_p50 = [stats[i]['2pc']['txnCommitTime']['summary'][0][1]/1000 for i in ins]
    twopc_fa_p99 = [stats[i]['2pc']['txnCommitTime']['summary'][0][2]/1000 for i in ins]
    print(f'epoch p50(ms): {epoch_fa_p50}')
    print(f'epoch p99(ms): {epoch_fa_p99}')
    print(f'2pc p50(ms): {twopc_fa_p50}')
    print(f'2pc p99(ms): {twopc_fa_p99}')
    l1, = plt.plot(ins, epoch_fa_p50, label=f'progress mark p50', marker=markers[0], color=colors[0])
    l2, = plt.plot(ins, epoch_fa_p99, label=f'progress mark p99', marker=markers[0], ls='--', color=colors[0])
    l3, = plt.plot(ins, twopc_fa_p50, label=f'txn commit p50', marker=markers[3], color=colors[1])
    l4, = plt.plot(ins, twopc_fa_p99, label=f'txn commit p99', marker=markers[3], ls='--', color=colors[1])
    handles = [l1, l2, l3, l4]
    plt.xlabel("Number of substreams")
    plt.ylabel("Commit/mark time(ms)")
    plt.legend(handles=handles, ncol=2, loc='upper center', bbox_to_anchor=(0.5, 1.4))
    plt.savefig(f"{metric_dir}/q8_mark_cmt.pdf")


if __name__ == '__main__':
    main()
