import argparse
import os
from re import T

PRODUCER_TAG = "producer-topic-metrics record-send-total"
CONSUMER_TAG = "consumer-fetch-manager-metrics records-consumed-total"

def parse_nexmark(filepath: str, produced: dict, consumed: dict, times: list):
    with open(filepath, "r") as f:
        for line in f:
            if "topic=" in line and (PRODUCER_TAG in line or CONSUMER_TAG in line):
                l_arr = line.strip().split(", ")
                print(l_arr)
                assert "topic=" in l_arr[2]
                topic = l_arr[2][:-1].split("=")[1]
                val = int(float(l_arr[-1].split(" ")[-1]))
                if l_arr[0] == PRODUCER_TAG:    
                    if topic not in produced:
                        produced[topic] = []
                    produced[topic].append(val)
                elif l_arr[0] == CONSUMER_TAG:
                    if topic not in consumed:
                        consumed[topic] = []
                    consumed[topic].append(val)
            if "Duration" in line:
                duration = float(line.strip().split(" ")[-1])
                times.append(duration)

def parse_source(filepath: str):
    duration = 0.0
    produced = 0
    with open(filepath, "r") as f:
        for line in f:
            if "source processed" in line:
                l_arr = line.strip().split(", ")
                produced = int(l_arr[0].split(" ")[2])
                duration = float(l_arr[1].split(" ")[-1])
    return produced, duration


def summary(events: dict, max_time: float):
    for tp, val in events.items():
        total = sum(val)
        print(f"{tp} {total} events, throughput: {round(float(total)/max_time, 1)}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True, type=str, help="dir to lookat")
    args = parser.parse_args()
    nexmark_produced = {}
    nexmark_consumed = {}
    nexmark_time = []
    src_time = []
    src_prod = []
    for root, dirs, files in os.walk(args.dir):
        for name in files:
            if "nexmark" in name and "stdout" in name:
                filepath = os.path.join(root, name)
                parse_nexmark(filepath=filepath, produced=nexmark_produced, consumed=nexmark_consumed, times=nexmark_time)
            if "source" in name and "stderr" in name:
                filepath = os.path.join(root, name)
                src_gen, src_dur = parse_source(filepath)
                src_time.append(src_dur)
                src_prod.append(src_gen)

    print()
    src_max_time = max(src_time)
    src_total_prod = sum(src_prod)
    print(f"source produced: {src_total_prod}, time: {src_max_time}, throughput: {round(float(src_total_prod)/src_max_time, 1)}")
    print(f"consumed: {nexmark_consumed}, produced: {nexmark_produced}, time: {nexmark_time}")
    max_time = max(nexmark_time)
    print("consumed")
    summary(nexmark_consumed, max_time)
    print("produced")
    summary(nexmark_produced, max_time)




if __name__ == '__main__':
    main()
