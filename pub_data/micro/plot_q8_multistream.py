import json
import matplotlib.pyplot as plt

tps_map = {
    "4":  "28000",
    "8":  "14000",
    "16": "7000",
    "32": "3500",
}

def main():
    with open("./q8_multistream_stats.json", "r") as f:
        stats = json.load(f)
    ins = ["4", "8", "16", "32"]
    stages = stats["4"]['epoch']['flush_all']['per_stage'].keys()
    plt.figure(figsize=(7, 3), layout="constrained")
    for st in stages:
        epoch_fa_p50 = [stats[i]['epoch']['flush_all']['per_stage'][st][tps_map[i]]['p50'] for i in ins]
        epoch_fa_p99 = [stats[i]['epoch']['flush_all']['per_stage'][st][tps_map[i]]['p99'] for i in ins]
        twopc_fa_p50 = [stats[i]['2pc']['flush_all']['per_stage'][st][tps_map[i]]['p50'] for i in ins]
        twopc_fa_p99 = [stats[i]['2pc']['flush_all']['per_stage'][st][tps_map[i]]['p99'] for i in ins]
        plt.plot(ins, epoch_fa_p50, label=f'{st} epoch p50')
        plt.plot(ins, epoch_fa_p99, label=f'{st} epoch p99')
        plt.plot(ins, twopc_fa_p50, label=f'{st} 2pc p50')
        plt.plot(ins, twopc_fa_p99, label=f'{st} 2pc p99')
    plt.savefig("q8_flush_all.pdf")


if __name__ == '__main__':
    main()
