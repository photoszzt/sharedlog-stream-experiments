import json
import os
import sys
import pickle
import pprint
import numpy as np
import matplotlib.pyplot as plt

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from fig_const import markers, colors, headers

markFreq = [10, 20, 40]
markIntr = [100, 50, 25]

markFreq_10 = [10, 20, 40, 100]
markIntr_10 = [100, 50, 25, 10]

throughputs = {4: "750", 6: "750", 7: "8000"}


def main():
    mark_p50 = []
    mark_p99 = []
    cmt_p50 = []
    cmt_p99 = []

    groupby_mark_p50 = []
    groupby_mark_p99 = []
    groupby_cmt_p50 = []
    groupby_cmt_p99 = []

    join_mark_p50 = []
    join_mark_p99 = []
    join_cmt_p50 = []
    join_cmt_p99 = []

    max_mark_p50 = []
    max_mark_p99 = []
    max_cmt_p50 = []
    max_cmt_p99 = []

    avg_mark_p50 = []
    avg_mark_p99 = []
    avg_cmt_p50 = []
    avg_cmt_p99 = []

    twopc_fa_p50 = []
    twopc_fa_p99 = []
    epoch_fa_p50 = []
    epoch_fa_p99 = []

    groupby_twopc_fa_p50 = []
    groupby_twopc_fa_p99 = []
    groupby_epoch_fa_p50 = []
    groupby_epoch_fa_p99 = []

    join_twopc_fa_p50 = []
    join_twopc_fa_p99 = []
    join_epoch_fa_p50 = []
    join_epoch_fa_p99 = []

    max_twopc_fa_p50 = []
    max_twopc_fa_p99 = []
    max_epoch_fa_p50 = []
    max_epoch_fa_p99 = []

    avg_twopc_fa_p50 = []
    avg_twopc_fa_p99 = []
    avg_epoch_fa_p50 = []
    avg_epoch_fa_p99 = []

    waitPrevCmt_p50 = []
    waitPrevCmt_p99 = []

    join_waitPrevCmt_p50 = []
    join_waitPrevCmt_p99 = []

    groupby_waitPrevCmt_p50 = []
    groupby_waitPrevCmt_p99 = []

    max_waitPrevCmt_p50 = []
    max_waitPrevCmt_p99 = []

    avg_waitPrevCmt_p50 = []
    avg_waitPrevCmt_p99 = []

    for mi in markIntr:
        with open(f"q6_varflush/2pc/{mi}ms/1/750tps_2pc_stats.pickle", "rb") as f:
            stats_2pc = pickle.load(f)
        pprint.pprint(stats_2pc)
        with open(f"q6_varflush/epoch/{mi}ms/2/750tps_epoch_stats.pickle", "rb") as f:
            stats_epoch = pickle.load(f)
        mark_p50.append(stats_epoch['progress_mark'][750]["all"]['p50']/1000)
        mark_p99.append(stats_epoch['progress_mark'][750]["all"]['p99']/1000)
        cmt_p50.append(stats_2pc['txnCommitTime'][750]["all"]['p50']/1000)
        cmt_p99.append(stats_2pc['txnCommitTime'][750]["all"]['p99']/1000)

        epoch_fa_p50.append(stats_epoch['flushStage'][750]["all"]['p50']/1000)
        epoch_fa_p99.append(stats_epoch['flushStage'][750]["all"]['p99']/1000)
        twopc_fa_p50.append(stats_2pc['flushStage'][750]["all"]['p50']/1000)
        twopc_fa_p99.append(stats_2pc['flushStage'][750]["all"]['p99']/1000)

        groupby_epoch_fa_p50.append(stats_epoch['flushStage'][750]["q46GroupBy"]['p50']/1000)
        groupby_epoch_fa_p99.append(stats_epoch['flushStage'][750]["q46GroupBy"]['p99']/1000)
        groupby_twopc_fa_p50.append(stats_2pc['flushStage'][750]["q46GroupBy"]['p50']/1000)
        groupby_twopc_fa_p99.append(stats_2pc['flushStage'][750]["q46GroupBy"]['p99']/1000)

        join_epoch_fa_p50.append(stats_epoch['flushStage'][750]["q6JoinStream"]['p50']/1000)
        join_epoch_fa_p99.append(stats_epoch['flushStage'][750]["q6JoinStream"]['p99']/1000)
        join_twopc_fa_p50.append(stats_2pc['flushStage'][750]["q6JoinStream"]['p50']/1000)
        join_twopc_fa_p99.append(stats_2pc['flushStage'][750]["q6JoinStream"]['p99']/1000)

        max_epoch_fa_p50.append(stats_epoch['flushStage'][750]["q6MaxBid"]['p50']/1000)
        max_epoch_fa_p99.append(stats_epoch['flushStage'][750]["q6MaxBid"]['p99']/1000)
        max_twopc_fa_p50.append(stats_2pc['flushStage'][750]["q6MaxBid"]['p50']/1000)
        max_twopc_fa_p99.append(stats_2pc['flushStage'][750]["q6MaxBid"]['p99']/1000)

        avg_epoch_fa_p50.append(stats_epoch['flushStage'][750]["q6Avg"]['p50']/1000)
        avg_epoch_fa_p99.append(stats_epoch['flushStage'][750]["q6Avg"]['p99']/1000)
        avg_twopc_fa_p50.append(stats_2pc['flushStage'][750]["q6Avg"]['p50']/1000)
        avg_twopc_fa_p99.append(stats_2pc['flushStage'][750]["q6Avg"]['p99']/1000)

        groupby_mark_p50.append(stats_epoch['progress_mark'][750]["q46GroupBy"]['p50']/1000)
        groupby_mark_p99.append(stats_epoch['progress_mark'][750]["q46GroupBy"]['p99']/1000)
        groupby_cmt_p50.append(stats_2pc['txnCommitTime'][750]["q46GroupBy"]['p50']/1000)
        groupby_cmt_p99.append(stats_2pc['txnCommitTime'][750]["q46GroupBy"]['p99']/1000)

        join_mark_p50.append(stats_epoch['progress_mark'][750]["q6JoinStream"]['p50']/1000)
        join_mark_p99.append(stats_epoch['progress_mark'][750]["q6JoinStream"]['p99']/1000)
        join_cmt_p50.append(stats_2pc['txnCommitTime'][750]["q6JoinStream"]['p50']/1000)
        join_cmt_p99.append(stats_2pc['txnCommitTime'][750]["q6JoinStream"]['p99']/1000)

        max_mark_p50.append(stats_epoch['progress_mark'][750]["q6MaxBid"]['p50']/1000)
        max_mark_p99.append(stats_epoch['progress_mark'][750]["q6MaxBid"]['p99']/1000)
        max_cmt_p50.append(stats_2pc['txnCommitTime'][750]["q6MaxBid"]['p50']/1000)
        max_cmt_p99.append(stats_2pc['txnCommitTime'][750]["q6MaxBid"]['p99']/1000)

        avg_mark_p50.append(stats_epoch['progress_mark'][750]["q6Avg"]['p50']/1000)
        avg_mark_p99.append(stats_epoch['progress_mark'][750]["q6Avg"]['p99']/1000)
        avg_cmt_p50.append(stats_2pc['txnCommitTime'][750]["q6Avg"]['p50']/1000)
        avg_cmt_p99.append(stats_2pc['txnCommitTime'][750]["q6Avg"]['p99']/1000)

        waitPrevCmt_p50.append(stats_2pc['waitPrevTxnInCmt'][750]["all"]['p50']/1000)
        waitPrevCmt_p99.append(stats_2pc['waitPrevTxnInCmt'][750]["all"]['p99']/1000)

        join_waitPrevCmt_p50.append(stats_2pc['waitPrevTxnInCmt'][750]["q6JoinStream"]['p50']/1000)
        join_waitPrevCmt_p99.append(stats_2pc['waitPrevTxnInCmt'][750]["q6JoinStream"]['p99']/1000)

        groupby_waitPrevCmt_p50.append(stats_2pc['waitPrevTxnInCmt'][750]["q46GroupBy"]['p50']/1000)
        groupby_waitPrevCmt_p99.append(stats_2pc['waitPrevTxnInCmt'][750]["q46GroupBy"]['p99']/1000)

        max_waitPrevCmt_p50.append(stats_2pc['waitPrevTxnInCmt'][750]["q6MaxBid"]['p50']/1000)
        max_waitPrevCmt_p99.append(stats_2pc['waitPrevTxnInCmt'][750]["q6MaxBid"]['p99']/1000)

        avg_waitPrevCmt_p50.append(stats_2pc['waitPrevTxnInCmt'][750]["q6Avg"]['p50']/1000)
        avg_waitPrevCmt_p99.append(stats_2pc['waitPrevTxnInCmt'][750]["q6Avg"]['p99']/1000)

    print("mark/cmt (ms)")
    print(f"{markIntr_10}")
    print(f"2pc p50: {cmt_p50}")
    print(f"2pc p99: {cmt_p99}")
    print(f"epoch p50: {mark_p50}")
    print(f"epoch p99: {mark_p99}")
    print()

    print("flush (ms)")
    print(f"2pc p50: {twopc_fa_p50}")
    print(f"2pc p99: {twopc_fa_p99}")
    print(f"epoch p50: {epoch_fa_p50}")
    print(f"epoch p99: {epoch_fa_p99}")
    print()

    print("join flush (ms)")
    print(f"2pc p50: {join_twopc_fa_p50}")
    print(f"2pc p99: {join_twopc_fa_p99}")
    print(f"epoch p50: {join_epoch_fa_p50}")
    print(f"epoch p99: {join_epoch_fa_p99}")

    print("max flush (ms)")
    print(f"2pc p50: {max_twopc_fa_p50}")
    print(f"2pc p99: {max_twopc_fa_p99}")
    print(f"epoch p50: {max_epoch_fa_p50}")
    print(f"epoch p99: {max_epoch_fa_p99}")

    print("avg flush (ms)")
    print(f"2pc p50: {avg_twopc_fa_p50}")
    print(f"2pc p99: {avg_twopc_fa_p99}")
    print(f"epoch p50: {avg_epoch_fa_p50}")
    print(f"epoch p99: {avg_epoch_fa_p99}")
    print()

    print("q46GroupBy mark/cmt (ms)")
    print(f"2pc p50: {groupby_cmt_p50}")
    print(f"2pc p99: {groupby_cmt_p99}")
    print(f"epoch p50: {groupby_mark_p50}")
    print(f"epoch p99: {groupby_mark_p99}")

    print("join mark/cmt (ms)")
    print(f"2pc p50: {join_cmt_p50}")
    print(f"2pc p99: {join_cmt_p99}")
    print(f"epoch p50: {join_mark_p50}")
    print(f"epoch p99: {join_mark_p99}")
    print()

    print("max mark/cmt (ms)")
    print(f"2pc p50: {max_cmt_p50}")
    print(f"2pc p99: {max_cmt_p99}")
    print(f"epoch p50: {max_mark_p50}")
    print(f"epoch p99: {max_mark_p99}")
    print()

    print("avg mark/cmt (ms)")
    print(f"2pc p50: {avg_cmt_p50}")
    print(f"2pc p99: {avg_cmt_p99}")
    print(f"epoch p50: {avg_mark_p50}")
    print(f"epoch p99: {avg_mark_p99}")
    print()

    print("waitPrevInCmt (ms)")
    print(f"2pc p50: {waitPrevCmt_p50}")
    print(f"2pc p99: {waitPrevCmt_p99}")

    print("groupby waitPrevInCmt (ms)")
    print(f"2pc p50: {groupby_waitPrevCmt_p50}")
    print(f"2pc p99: {groupby_waitPrevCmt_p99}")

    print("join waitPrevInCmt (ms)")
    print(f"2pc p50: {join_waitPrevCmt_p50}")
    print(f"2pc p99: {join_waitPrevCmt_p99}")

    print("max waitPrevInCmt (ms)")
    print(f"2pc p50: {max_waitPrevCmt_p50}")
    print(f"2pc p99: {max_waitPrevCmt_p99}")

    print("avg waitPrevInCmt (ms)")
    print(f"2pc p50: {avg_waitPrevCmt_p50}")
    print(f"2pc p99: {avg_waitPrevCmt_p99}")


if __name__ == '__main__':
    main()
