import argparse
import matplotlib.pyplot as plt
import json
import numpy as np
from parse_epoch_mark_time import parse_single_topdir



dirs = {
    4: "./q8_boki/mem/4src_4node_4ins_0extra_kvrocks",  
    8: "./q8_boki/mem_4node_8ins/8src_4node_8ins_0extra_kvrocks/",
    16: "./q8_boki/mem_4node_16ins/16src_4node_16ins_0extra_kvrocks/",
    32: "./q8_boki/mem_4node_32ins/32src_4node_32ins_0extra_kvrocks/",
}

tps_map = {
    4: 28000,
    8: 14000,
    16: 7000,
    32: 3500,
}


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def main():
    stats = {}
    ins = [4, 8, 16, 32]
    for i in dirs:
        stats[i] = {}
    for i in ins:
        dir = dirs[i]
        epoch_stat = parse_single_topdir(dir, "epoch")
        twopc_stat = parse_single_topdir(dir, "2pc")
        stats[i]['epoch'] = epoch_stat
        stats[i]['2pc'] = twopc_stat
    print(stats)
    with open("q8_multistream_stats.json", "w") as f:
        json.dump(stats, f, cls=NpEncoder)
    # stages = stats[4]['epoch']['per_stage'].keys()
    # fig = plt.figure(figsize=(7, 3), layout="constrained")
    # for st in stages:
    #     epoch_fa_p50 = [stats[i]['epoch']['flush_all']['per_stage'][st][tps_map[i]]['p50'] for i in ins]
    #     epoch_fa_p99 = [stats[i]['epoch']['flush_all']['per_stage'][st][tps_map[i]]['p99'] for i in ins]
    #     fig.plot(ins, epoch_fa_p50, label=f'{st} p50')
    #     fig.plot(ins, epoch_fa_p99, label=f'{st} p99')
    # plt.save("q8_flush_all.pdf")


if __name__ == '__main__':
    main()
