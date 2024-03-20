import pickle
import os
from parse_epoch_mark_time import parse_single_topdir

def main():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    epoch_stat = parse_single_topdir(os.path.join(script_dir, "./fanout_boki/4src_1/"), "epoch", "fanout")
    twopc_stat = parse_single_topdir(os.path.join(script_dir, "./fanout_boki/4src_1/"), "2pc", "fanout")
    out_dir = os.path.join(script_dir, "../pub_data/micro/fanout/")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "fanout_epoch_stats.pickle"), "wb") as f:
        pickle.dump(epoch_stat, f)
    with open(os.path.join(out_dir, "fanout_2pc_stats.pickle"), "wb") as f:
        pickle.dump(twopc_stat, f)


if __name__ == '__main__':
    main()
