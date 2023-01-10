import argparse
import os
import json
from statistics import mean

stages = {
        "q5": {"bid-keyed-by-auction", "max-bid", "auc-bid", "faas-engine"},
        "q7": {"q7BidByPrice", "q7BidByWin", "q7JoinMaxBid", "q7MaxBid", "faas-engine"},
        "q8": {"q8GroupBy", "q8JoinStream", "faas-engine"},
}

def get_name(name, stages):
    for st in stages:
        if st in name:
            return st


def main():
    parser = argparse.ArgumentParser(description='Parse stage time')
    parser.add_argument('--dir', type=str, help='dir to parse', required=True)
    parser.add_argument('--app', type=str, help='app', required=True)
    args = parser.parse_args()
    max_cpu = {}
    for root, dirs, files in os.walk(args.dir):
        for fname in files:
            stats = {}
            fpath = os.path.join(root, fname)
            with open(fpath, 'r') as f:
                data = json.load(f)
            for stat in data:
                name = stat['Name']
                if name not in stats:
                    stats[name] = {}
                cpu_per = float(stat['CPUPerc'].strip("%"))
                memUsgArr = stat['MemUsage'].split('/')
                memUsgStr = memUsgArr[0].strip()
                # memUsg in kb
                if 'GiB' in memUsgStr:
                    memUsg = float(memUsgStr.strip("GiB")) * 1024 * 1024 * 1024
                elif 'MiB' in memUsgStr:
                    memUsg = float(memUsgStr.strip("MiB")) * 1024 * 1024
                elif 'kb' in memUsgStr:
                    memUsg = float(memUsgStr.strip("kb")) * 1024
                elif 'B' in memUsgStr and 'GiB' not in memUsgStr and 'MiB' not in memUsgStr:
                    memUsg = float(memUsgStr.strip("B"))
                else:
                    raise Exception(f"unrecognized unit in {memUsgStr}")


                if 'cpuPer' not in stats[name]:
                    stats[name]['cpuPer'] = []
                if 'memUsg' not in stats[name]:
                    stats[name]['memUsg'] = []
                stats[name]['cpuPer'].append(cpu_per)
                stats[name]['memUsg'].append(memUsg)
            shouldPrint = True
            for n in stats:
                if "nexmark-source" in n:
                    maxCpu = max(stats[n]['cpuPer'])
                    if maxCpu != 0:
                        shouldPrint = False
            st = stages[args.app]
            if shouldPrint:
                print(fname)
                for n in stats:
                    name = get_name(n, st)
                    if name not in max_cpu and name is not None:
                        max_cpu[name] = 0
                    maxCpu = max(stats[n]['cpuPer'])
                    meanCpu = mean(stats[n]['cpuPer'])
                    if name is not None and maxCpu > max_cpu[name]:
                        max_cpu[name] = maxCpu
                    maxMem = max(stats[n]['memUsg'])/1024.0/1024.0
                    meanMem = mean(stats[n]['memUsg'])/1024.0/1024.0
                    print(f"{n}, max cpu util: {maxCpu}, max mem usage(MB): {maxMem}, "
                          f"mean cpu util: {meanCpu}, mean mem usage(MB): {meanMem}")
                print()
        print(max_cpu)


if __name__ == '__main__':
    main()
