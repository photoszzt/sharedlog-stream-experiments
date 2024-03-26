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

    tp=850
    for mi in markIntr_10:
        with open(f"q4_varflush2/2pc/{mi}ms/1/{tp}tps_2pc_stats.pickle", "rb") as f:
            stats_2pc = pickle.load(f)
        with open(f"q4_varflush2/epoch/{mi}ms/0/{tp}tps_epoch_stats.pickle", "rb") as f:
            stats_epoch = pickle.load(f)
        pprint.pprint(stats_epoch)
        mark_p50.append(stats_epoch['progress_mark'][tp]["all"]['p50']/1000)
        mark_p99.append(stats_epoch['progress_mark'][tp]["all"]['p99']/1000)
        cmt_p50.append(stats_2pc['txnCommitTime'][tp]["all"]['p50']/1000)
        cmt_p99.append(stats_2pc['txnCommitTime'][tp]["all"]['p99']/1000)

        groupby_mark_p50.append(stats_epoch['progress_mark'][tp]["q46GroupBy"]['p50']/1000)
        groupby_mark_p99.append(stats_epoch['progress_mark'][tp]["q46GroupBy"]['p99']/1000)
        groupby_cmt_p50.append(stats_2pc['txnCommitTime'][tp]["q46GroupBy"]['p50']/1000)
        groupby_cmt_p99.append(stats_2pc['txnCommitTime'][tp]["q46GroupBy"]['p99']/1000)

        join_mark_p50.append(stats_epoch['progress_mark'][tp]["q4JoinStream"]['p50']/1000)
        join_mark_p99.append(stats_epoch['progress_mark'][tp]["q4JoinStream"]['p99']/1000)
        join_cmt_p50.append(stats_2pc['txnCommitTime'][tp]["q4JoinStream"]['p50']/1000)
        join_cmt_p99.append(stats_2pc['txnCommitTime'][tp]["q4JoinStream"]['p99']/1000)

        max_mark_p50.append(stats_epoch['progress_mark'][tp]["q4MaxBid"]['p50']/1000)
        max_mark_p99.append(stats_epoch['progress_mark'][tp]["q4MaxBid"]['p99']/1000)
        max_cmt_p50.append(stats_2pc['txnCommitTime'][tp]["q4MaxBid"]['p50']/1000)
        max_cmt_p99.append(stats_2pc['txnCommitTime'][tp]["q4MaxBid"]['p99']/1000)

        avg_mark_p50.append(stats_epoch['progress_mark'][tp]["q4Avg"]['p50']/1000)
        avg_mark_p99.append(stats_epoch['progress_mark'][tp]["q4Avg"]['p99']/1000)
        avg_cmt_p50.append(stats_2pc['txnCommitTime'][tp]["q4Avg"]['p50']/1000)
        avg_cmt_p99.append(stats_2pc['txnCommitTime'][tp]["q4Avg"]['p99']/1000)

        waitPrevCmt_p50.append(stats_2pc['waitPrevTxnInCmt'][tp]["all"]['p50']/1000)
        waitPrevCmt_p99.append(stats_2pc['waitPrevTxnInCmt'][tp]["all"]['p99']/1000)

        join_waitPrevCmt_p50.append(stats_2pc['waitPrevTxnInCmt'][tp]["q4JoinStream"]['p50']/1000)
        join_waitPrevCmt_p99.append(stats_2pc['waitPrevTxnInCmt'][tp]["q4JoinStream"]['p99']/1000)

        groupby_waitPrevCmt_p50.append(stats_2pc['waitPrevTxnInCmt'][tp]["q46GroupBy"]['p50']/1000)
        groupby_waitPrevCmt_p99.append(stats_2pc['waitPrevTxnInCmt'][tp]["q46GroupBy"]['p99']/1000)

        max_waitPrevCmt_p50.append(stats_2pc['waitPrevTxnInCmt'][tp]["q4MaxBid"]['p50']/1000)
        max_waitPrevCmt_p99.append(stats_2pc['waitPrevTxnInCmt'][tp]["q4MaxBid"]['p99']/1000)

        avg_waitPrevCmt_p50.append(stats_2pc['waitPrevTxnInCmt'][tp]["q4Avg"]['p50']/1000)
        avg_waitPrevCmt_p99.append(stats_2pc['waitPrevTxnInCmt'][tp]["q4Avg"]['p99']/1000)

    print("mark/cmt (ms)")
    print(f"{markIntr_10}")
    print(f"2pc p50: {cmt_p50}")
    print(f"2pc p99: {cmt_p99}")
    print(f"epoch p50: {mark_p50}")
    print(f"epoch p99: {mark_p99}")
    print()

    print("q46GroupBy mark/cmt (ms)")
    print(f"2pc p50: {groupby_cmt_p50}")
    print(f"2pc p99: {groupby_cmt_p99}")
    print(f"epoch p50: {groupby_mark_p50}")
    print(f"epoch p99: {groupby_mark_p99}")
    print()

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
