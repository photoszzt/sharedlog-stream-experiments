import csv
import subprocess

headers = [
    "del",
    "tps",
    "trials",
    "pts",
    "avg",
    "std",
    "min",
    "p25",
    "p50",
    "p75",
    "p90",
    "p99",
    "max",
]

kafkas = [
    "./curated/kafka/q1-kafka-180s-0swarm-10ms-src10ms",
    "./curated/kafka/q2-kafka-180s-0swarm-10ms-src10ms",
    "./curated/kafka/q3-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q4-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q5-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q6-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q7-3t-kafka-180s-0swarm-100ms-src100ms",
    "./curated/kafka/q8-kafka-180s-0swarm-100ms-src100ms",
]

syss = [
    "./pm_data/sys-boki/q1-boki-180s-0swarm-10ms-src10ms",
    "./pm_data/sys-boki/q2-boki-180s-0swarm-10ms-src10ms",
    "./q38_rerun/impeller/q3-180s-0swarm-100ms-src100ms",
    "./q38_rerun/impeller/q4-180s-0swarm-100ms-src100ms",
    "./q38_rerun/impeller/q5-180s-0swarm-100ms-src100ms",
    "./q38_rerun/impeller/q6-180s-0swarm-100ms-src100ms",
    "./q38_rerun/impeller/q7-180s-0swarm-100ms-src100ms",
    "./q38_rerun/impeller/q8-180s-0swarm-100ms-src100ms",
]

remote_2pc = [
    "./q38_rerun/remote_2pc/q1-180s-0swarm-100ms-src10ms",
    "./q38_rerun/remote_2pc/q2-180s-0swarm-100ms-src10ms",
    "./q38_rerun/remote_2pc/q3-180s-0swarm-100ms-src100ms",
    "./q38_rerun/remote_2pc/q4-180s-0swarm-100ms-src100ms",
    "./q38_rerun/remote_2pc/q5-180s-0swarm-100ms-src100ms",
    "./q38_rerun/remote_2pc/q6-180s-0swarm-100ms-src100ms",
    "./q38_rerun/remote_2pc/q7-180s-0swarm-100ms-src100ms",
    "./q38_rerun/remote_2pc/q8-180s-0swarm-100ms-src100ms",
]

nones = [
    "./none_data/sys-boki/q1-boki-180s-0swarm-100ms-src10ms",
    "./none_data/sys-boki/q2-boki-180s-0swarm-100ms-src10ms",
    "./none_data/sys-boki/q3-boki-180s-0swarm-100ms-src100ms",
    "./none_data/sys-boki/q4-boki-180s-0swarm-100ms-src100ms",
    "./none_data/sys-boki/q5-boki-180s-0swarm-100ms-src100ms",
    "./none_data/sys-boki/q6-boki-180s-0swarm-100ms-src100ms",
    "./none_data/sys-boki/q7-boki-180s-0swarm-100ms-src100ms",
    "./none_data/sys-boki/q8-boki-180s-0swarm-100ms-src100ms",
]

throughputs = [
    [4000, 16000, 32000, 48000, 64000, 80000, 88000],
    [4000, 16000, 32000, 48000, 64000, 80000, 88000],
    [8000, 16000, 32000, 48000, 64000, 80000, 96000, 112000, 128000],
    [250, 500, 750, 1000, 1250, 1500],
    [1000, 8000, 16000, 24000, 32000, 40000, 48000, 56000, 64000],
    # [1000, 8000, 16000, 24000, 32000, 40000, 48000, 56000],
    [250, 500, 750, 1000, 1250, 1500],
    [4000, 8000, 12000, 16000, 20000, 24000, 28000, 32000, 36000, 40000],
    [4000, 8000, 12000, 16000, 20000, 24000, 28000, 32000, 36000],
]


def load(system, experiment):
    rows = subprocess.run(
        ["./latency", "query", system[experiment]], stdout=subprocess.PIPE
    )
    rows = rows.stdout.decode("utf-8").strip().split("\n")
    rows = [
        row
        for row in csv.DictReader(rows, fieldnames=headers)
        if (
            row["del"] == "eo"
            or row["del"] == "2pc"
            or row["del"] == "align_chkpt"
            or row["del"] == "remote_2pc"
        )
        and int(row["tps"]) in throughputs[experiment]
    ]
    rows.sort(key=lambda row: int(row["tps"]))
    return rows


if __name__ == "__main__":
    experiment = 4
    kafka = load(kafkas, experiment)
    sys = load(syss, experiment)
    none = load(nones, experiment)
    r2pc = load(remote_2pc, experiment)

    sys_in_per_worker_tp = [int(row["tps"]) for row in sys]
    none_in_per_worker_tp = [int(row["tps"]) for row in none]
    kafka_in_per_worker_tp = [int(row["tps"]) for row in kafka]
    remote2pc_in_per_worker_tp = [int(row["tps"]) for row in r2pc]

    kafka_in_tp = [i * 4 for i in kafka_in_per_worker_tp]
    sys_in_tp = [i * 4 for i in sys_in_per_worker_tp]
    none_in_tp = [i * 4 for i in none_in_per_worker_tp]
    r2pc_in_tp = [i * 4 for i in remote2pc_in_per_worker_tp]

    sys_p50 = [int(row["p50"]) for row in sys]
    sys_p99 = [int(row["p99"]) for row in sys]
    kafka_p50 = [int(row["p50"]) for row in kafka]
    kafka_p99 = [int(row["p99"]) for row in kafka]
    r2pc_p50 = [int(row["p50"]) for row in r2pc]
    r2pc_p99 = [int(row["p99"]) for row in r2pc]
    none_p50 = [int(row["p50"]) for row in none]
    none_p99 = [int(row["p99"]) for row in none]

    with open(f"q{experiment+1}.csv", "w") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(sys_in_tp)
        csv_writer.writerow(sys_p50)
        csv_writer.writerow(sys_p99)

        csv_writer.writerow(kafka_in_tp)
        csv_writer.writerow(kafka_p50)
        csv_writer.writerow(kafka_p99)

        csv_writer.writerow(r2pc_in_tp)
        csv_writer.writerow(r2pc_p50)
        csv_writer.writerow(r2pc_p99)

        csv_writer.writerow(none_in_tp)
        csv_writer.writerow(none_p50)
        csv_writer.writerow(none_p99)
