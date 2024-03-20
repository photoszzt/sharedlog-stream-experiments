import json
import os
import sys
import matplotlib.pyplot as plt
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from fig_const import markers, colors, headers

tps_map = {
    "4":  "28000",
    "8":  "14000",
    "16": "7000",
    "28": "4000",
    "32": "3500",
    "40": "2800",
}

metric_dir = "q8_metrics_0extra_4xlarge"
metric_file = "../../nexmark_sharedlog/q8_multistream_stats_0extra_4xlarge.json"

def main():
    os.makedirs(metric_dir, exist_ok=True)
    with open(metric_file, "r") as f:
        stats = json.load(f)
    ins = ["4", "8", "16", "32"]
    metrics = ['flush_all', 'flush_at_least_one']
    for m in metrics:
        stages = stats["4"]['epoch'][m]['per_stage'].keys()
        for st in stages:
            plt.figure(figsize=(7, 3), layout="constrained")
            epoch_fa_p50 = [stats[i]['epoch'][m]['per_stage'][st][tps_map[i]]['p50']/1000 for i in ins]
            epoch_fa_p99 = [stats[i]['epoch'][m]['per_stage'][st][tps_map[i]]['p99']/1000 for i in ins]
            twopc_fa_p50 = [stats[i]['2pc'][m]['per_stage'][st][tps_map[i]]['p50']/1000 for i in ins]
            twopc_fa_p99 = [stats[i]['2pc'][m]['per_stage'][st][tps_map[i]]['p99']/1000 for i in ins]
            print(f'{st} epoch {m} p50(ms): {epoch_fa_p50}')
            print(f'{st} epoch {m} p99(ms): {epoch_fa_p99}')
            print(f'{st} 2pc {m} p50(ms): {twopc_fa_p50}')
            print(f'{st} 2pc {m} p99(ms): {twopc_fa_p99}')
            l1, = plt.plot(ins, epoch_fa_p50, label=f'{st} Impeller p50', marker=markers[0], color=colors[0])
            l2, = plt.plot(ins, epoch_fa_p99, label=f'{st} Impeller p99', marker=markers[0], ls='--', color=colors[0])
            l3, = plt.plot(ins, twopc_fa_p50, label=f'{st} 2pc on Impeller p50', marker=markers[3], color=colors[1])
            l4, = plt.plot(ins, twopc_fa_p99, label=f'{st} 2pc on Impeller p99', marker=markers[3], ls='--', color=colors[1])
            handles = [l1, l2, l3, l4]
            plt.xlabel("number of substreams")
            plt.ylabel("time(ms)")
            plt.title(f"{m}")
            plt.legend(handles=handles, ncol=2, loc='upper center', bbox_to_anchor=(0.5, 1.4))
            plt.savefig(f"{metric_dir}/q8_{m}_{st}.pdf")
            print()

    epoch_metrics = ['progress_mark', 'mark_part', 'append_mark', 'prepare_mark']
    for m in epoch_metrics:
        plt.figure(figsize=(7, 3), layout="constrained")
        stages = stats["4"]['epoch'][m]['per_stage'].keys()
        handles = []
        for idx, st in enumerate(stages):
            p50 = [stats[i]['epoch'][m]['per_stage'][st][tps_map[i]]['p50']/1000 for i in ins]
            p99 = [stats[i]['epoch'][m]['per_stage'][st][tps_map[i]]['p99']/1000 for i in ins]
            print(f'{st} {m} p50(ms): {p50}')
            print(f'{st} {m} p99(ms): {p99}')
            l1, = plt.plot(ins, p50, label=f'{st} p50', marker=markers[idx], color=colors[idx])
            l2, = plt.plot(ins, p99, label=f'{st} p99', marker=markers[idx], color=colors[idx], ls='--')
            handles.append(l1)
            handles.append(l2)
        plt.xlabel("number of substreams")
        plt.ylabel("time(ms)")
        plt.title(f"{m}")
        plt.legend(ncol=2, loc='upper center', bbox_to_anchor=(0.5, 1.4), handles=handles)
        plt.savefig(f"{metric_dir}/q8_{m}.pdf")
        print()

    twopc_metrics = ['commitTxnAPITime', 'txnCommitTime', 'sendOffsetTime', 'waitPrevTxn', 'waitPrevTxn2pc', 'appendTxnMeta2pc']
    for m in twopc_metrics:
        plt.figure(figsize=(7, 3), layout="constrained")
        stages = stats["4"]['2pc'][m]['per_stage'].keys()
        handles = []
        for idx, st in enumerate(stages):
            p50 = [stats[i]['2pc'][m]['per_stage'][st][tps_map[i]]['p50']/1000 for i in ins]
            p99 = [stats[i]['2pc'][m]['per_stage'][st][tps_map[i]]['p99']/1000 for i in ins]
            print(f'{st} {m} p50(ms): {p50}')
            print(f'{st} {m} p99(ms): {p99}')
            l1, = plt.plot(ins, p50, label=f'{st} p50', marker=markers[idx], color=colors[idx])
            l2, = plt.plot(ins, p99, label=f'{st} p99', marker=markers[idx], color=colors[idx], ls='--')
            handles.append(l1)
            handles.append(l2)
        plt.xlabel("number of substreams")
        plt.ylabel("time(ms)")
        plt.title(f"{m}")
        plt.legend(ncol=2, loc='upper center', bbox_to_anchor=(0.5, 1.4), handles=handles)
        plt.savefig(f"{metric_dir}/q8_{m}.pdf")
        print()

    m='marker_size'
    plt.figure(figsize=(7, 3), layout="constrained")
    stages = stats["4"]['epoch'][m]['per_stage'].keys()
    for idx, st in enumerate(stages):
        p50 = [stats[i]['epoch'][m]['per_stage'][st][tps_map[i]]['p50']/1024 for i in ins]
        p99 = [stats[i]['epoch'][m]['per_stage'][st][tps_map[i]]['p99']/1024 for i in ins]
        print(f'{st} {m} p50(KB): {p50}')
        print(f'{st} {m} p99(KB): {p99}')
        plt.plot(ins, p50, label=f'{st} p50', marker=markers[idx], color=colors[idx])
        plt.plot(ins, p99, label=f'{st} p99', marker=markers[idx], color=colors[idx], ls='--')
    plt.xlabel("number of substreams")
    plt.ylabel("size(KB)")
    plt.title(f"{m}")
    plt.legend(ncol=2, loc='upper center', bbox_to_anchor=(0.5, 1.4))
    plt.savefig(f"{metric_dir}/q8_{m}.pdf")
    print()

    metrics = ['q8_personsByID_out_flushBuf', 'q8_aucsBySellerID_out_flushBuf', 
               'q8_out_flushBuf', 'q8AuctionsBySellerIDWinTab-changelog_flushBuf',
               'q8PersonsByIDWinTab-changelog_flushBuf']
    methods=['epoch', '2pc']
    for m in metrics:
        if len(stats["4"]['epoch'][m]) > 0:
            stages = stats["4"]['epoch'][m]['0']['per_stage'].keys()
        elif len(stats["4"]['2pc'][m]) > 0:
            stages = stats["4"]['2pc'][m]['0']['per_stage'].keys()
        else:
            continue
        for i in ins:
            for idx, st in enumerate(stages):
                for mth in methods:
                    if len(stats[i][mth][m]) > 0:
                        for j in range(0, int(i)):
                            p50 = stats[i][mth][m][str(j)]['per_stage'][st][tps_map[i]]['p50']
                            p99 = stats[i][mth][m][str(j)]['per_stage'][st][tps_map[i]]['p99']
                            print(f'{st} {m}_{j} {mth}, p50: {p50}, p99: {p99}')
            print()



if __name__ == '__main__':
    main()
