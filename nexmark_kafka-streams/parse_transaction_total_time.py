import argparse
import os

stats = {
    "blocked-time-total",
    "txn-begin-time-ns-total",
    "txn-send-offsets-time-ns-total",
    "txn-commit-time-ns-total",
    "txn-abort-time-ns-total",
    "commited-time-ns-total",
    "commit-sync-time-ns-total",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True)
    args = parser.parse_args()
    stats = {}
    timeline = []
    for root, dirs, files in os.walk(args.dir):
        for fname in files:
            if "kstreams-test_nexmark" in fname and "stdout" in fname and fname not in stats:
                fpath = os.path.join(root, fname)
                stats[fname] = {}
                with open(fpath, "r") as f:
                    for line in f:
                        if "emit metrics at" in line:
                            t = int(line.strip().split(" ")[3])
                            timeline.append(t)
                        elif "metrics" in line and ";" in line:
                            l = line.strip().split(";")
                            sp = l[0].split(" ")
                            name = sp[1]
                            if name in stats:
                                latStr = l[2].split(":")[1]
                                if "NaN" not in latStr:
                                    if name not in stats[fname]:
                                        stats[fname][name] = []
                                    stats[fname][name].append(int(latStr))
    for fname, stat in stats.items():
        print(fname)
        for name, data in stat.items():
            last_time = 0
            last_data_time = 0
            print(f"{name}: ", end="")
            for i in range(len(timeline)):
                dur = timeline[i] - last_time
                dur_data = data[i] - last_data_time
                print(f"{dur_data}", end=" ")
                last_time = timeline[i]
                last_data_time = data[i]
            print()

                
if __name__ == '__main__':
    main()