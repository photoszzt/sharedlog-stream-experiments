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
    "4":  '28000',
    "8":  '14000',
    "16": '7000',
    "28": '4000',
    "32": '3500',
    "40": '2800',
}

metric_dir = "q8_metrics_0extra_4xlarge"
metric_file = "./q8_multistream_stats_0extra_4xlarge2.json"


def main():
    os.makedirs(metric_dir, exist_ok=True)
    with open(metric_file, "r") as f:
        stats = json.load(f)
    ins = ["4", "8", "16", "28", "32"]
    # plt.figure(figsize=(7, 3), layout="constrained")
    epoch_groupby_p50 = [stats[i]['epoch']['progress_mark']['per_stage']['q8GroupBy'][tps_map[i]]['p50']/1000 for i in ins]
    epoch_groupby_p99 = [stats[i]['epoch']['progress_mark']['per_stage']['q8GroupBy'][tps_map[i]]['p99']/1000 for i in ins]
    twopc_groupby_p50 = [stats[i]['2pc']['txnCommitTime']['per_stage']['q8GroupBy'][tps_map[i]]['p50']/1000 for i in ins]
    twopc_groupby_p99 = [stats[i]['2pc']['txnCommitTime']['per_stage']['q8GroupBy'][tps_map[i]]['p99']/1000 for i in ins]

    epoch_joinstream_p50 = [stats[i]['epoch']['progress_mark']['per_stage']['q8JoinStream'][tps_map[i]]['p50']/1000 for i in ins]
    epoch_joinstream_p99 = [stats[i]['epoch']['progress_mark']['per_stage']['q8JoinStream'][tps_map[i]]['p99']/1000 for i in ins]
    twopc_joinstream_p50 = [stats[i]['2pc']['txnCommitTime']['per_stage']['q8JoinStream'][tps_map[i]]['p50']/1000 for i in ins]
    twopc_joinstream_p99 = [stats[i]['2pc']['txnCommitTime']['per_stage']['q8JoinStream'][tps_map[i]]['p99']/1000 for i in ins]
    print("q8GroupBy mark/commit(ms)")
    print(f'epoch p50(ms): {epoch_groupby_p50}')
    print(f'epoch p99(ms): {epoch_groupby_p99}')
    print(f'2pc p50(ms): {twopc_groupby_p50}')
    print(f'2pc p99(ms): {twopc_groupby_p99}')

    print("q8JoinStream mark/commit(ms)")
    print(f'epoch p50(ms): {epoch_joinstream_p50}')
    print(f'epoch p99(ms): {epoch_joinstream_p99}')
    print(f'2pc p50(ms): {twopc_joinstream_p50}')
    print(f'2pc p99(ms): {twopc_joinstream_p99}')

    metrics = ['flush_all', 'flush_at_least_one']
    stages = ['q8GroupBy', 'q8JoinStream']
    for m in metrics:
        for st in stages:
            epoch_p50 = [stats[i]['epoch'][m]['per_stage'][st][tps_map[i]]['p50']/1000 for i in ins]
            epoch_p99 = [stats[i]['epoch'][m]['per_stage'][st][tps_map[i]]['p99']/1000 for i in ins]
            twopc_p50 = [stats[i]['2pc'][m]['per_stage'][st][tps_map[i]]['p50']/1000 for i in ins]
            twopc_p99 = [stats[i]['2pc'][m]['per_stage'][st][tps_map[i]]['p99']/1000 for i in ins]
            print(f"{st} {m}(ms)")
            print(f'epoch p50(ms): {epoch_p50}')
            print(f'epoch p99(ms): {epoch_p99}')
            print(f'2pc p50(ms): {twopc_p50}')
            print(f'2pc p99(ms): {twopc_p99}')


    if 'waitPrevTxnInCmt' in stats["4"]['2pc']:
        groupby_waitPrev_p50 = [stats[i]['2pc']['waitPrevTxnInCmt']['per_stage']['q8GroupBy'][tps_map[i]]['p50']/1000 for i in ins]
        groupby_waitPrev_p99 = [stats[i]['2pc']['waitPrevTxnInCmt']['per_stage']['q8GroupBy'][tps_map[i]]['p99']/1000 for i in ins]
        joinstream_waitPrev_p50 = [stats[i]['2pc']['waitPrevTxnInCmt']['per_stage']['q8JoinStream'][tps_map[i]]['p50']/1000 for i in ins]
        joinstream_waitPrev_p99 = [stats[i]['2pc']['waitPrevTxnInCmt']['per_stage']['q8JoinStream'][tps_map[i]]['p99']/1000 for i in ins]
        print("q8GroupBy waitPrevTxnInCmt(ms)")
        print(f"2pc p50(ms): {groupby_waitPrev_p50}")
        print(f"2pc p99(ms): {groupby_waitPrev_p99}")
        print("q8JoinStream waitPrevTxnInCmt(ms)")
        print(f"2pc p50(ms): {joinstream_waitPrev_p50}")
        print(f"2pc p99(ms): {joinstream_waitPrev_p99}")

    if 'waitPrevTxnInPush' in stats["4"]['2pc']:
        # if 'q8GroupBy' in stats["4"]['2pc']['waitPrevTxnInPush']['per_stage']:
        #     groupby_waitPrev_p50 = [stats[i]['2pc']['waitPrevTxnInPush']['per_stage']['q8GroupBy'][tps_map[i]]['p50']/1000 for i in ins]
        #     groupby_waitPrev_p99 = [stats[i]['2pc']['waitPrevTxnInPush']['per_stage']['q8GroupBy'][tps_map[i]]['p99']/1000 for i in ins]
        #     print("q8GroupBy waitPrevTxnInPush(ms)")
        #     print(f"2pc p50(ms): {groupby_waitPrev_p50}")
        #     print(f"2pc p99(ms): {groupby_waitPrev_p99}")

        if 'q8JoinStream' in stats["4"]['2pc']['waitPrevTxnInPush']['per_stage']:
            joinstream_waitPrev_p50 = [stats[i]['2pc']['waitPrevTxnInPush']['per_stage']['q8JoinStream'][tps_map[i]]['p50']/1000 for i in ins]
            joinstream_waitPrev_p99 = [stats[i]['2pc']['waitPrevTxnInPush']['per_stage']['q8JoinStream'][tps_map[i]]['p99']/1000 for i in ins]
            print("q8JoinStream waitPrevTxnInPush(ms)")
            print(f"2pc p50(ms): {joinstream_waitPrev_p50}")
            print(f"2pc p99(ms): {joinstream_waitPrev_p99}")


    # l1, = plt.plot(ins, epoch_fa_p50, label=f'progress mark p50', marker=markers[0], color=colors[0])
    # l2, = plt.plot(ins, epoch_fa_p99, label=f'progress mark p99', marker=markers[0], ls='--', color=colors[0])
    # l3, = plt.plot(ins, twopc_fa_p50, label=f'txn commit p50', marker=markers[3], color=colors[1])
    # l4, = plt.plot(ins, twopc_fa_p99, label=f'txn commit p99', marker=markers[3], ls='--', color=colors[1])
    # handles = [l1, l2, l3, l4]
    # plt.xlabel("Number of substreams")
    # plt.ylabel("Commit/mark time(ms)")
    # plt.legend(handles=handles, ncol=2, loc='upper center', bbox_to_anchor=(0.5, 1.4))
    # plt.savefig(f"{metric_dir}/q8_mark_cmt.pdf")


if __name__ == '__main__':
    main()
