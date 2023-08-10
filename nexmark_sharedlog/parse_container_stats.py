import argparse
import os
import json
from statistics import mean

stages = {
        "q4": {"q46GroupBy", "q4Avg", "q4JoinTable", "q4MaxBid", "faas-engine"},
        "q5": {"bid-keyed-by-auction", "max-bid", "auc-bid", "faas-engine"},
        "q6": {"q46GroupBy", "q6Avg", "q6JoinTable", "q6JoinStream", "q6MaxBid", "faas-engine"},
        "q7": {"q7BidByPrice", "q7BidByWin", "q7JoinMaxBid", "q7MaxBid", "faas-engine"},
        "q8": {"q8GroupBy", "q8JoinStream", "faas-engine"},
}

def get_name(name, stages):
    for st in stages:
        if st in name:
            return st


def get_byte_from_human(num_str: str):
    if 'GiB' in num_str:
        return float(num_str.strip("GiB")) * 1024 * 1024 * 1024
    elif 'MiB' in num_str:
        return float(num_str.strip("MiB")) * 1024 * 1024
    elif 'kb' in num_str:
        return float(num_str.strip("kb")) * 1024
    elif 'kB' in num_str:
        return float(num_str.strip("kB")) * 1000
    elif 'MB' in num_str:
        return float(num_str.strip("MB")) * 1000 * 1000
    elif 'GB' in num_str:
        return float(num_str.strip("GB")) * 1000 * 1000 * 1000
    elif 'B' in num_str and 'GiB' not in num_str and 'MiB' not in num_str and 'MB' not in num_str and 'kB' not in num_str:
        return float(num_str.strip("B"))
    else:
        raise Exception(f"unrecognized unit in {memUsgStr}")



def main():
    parser = argparse.ArgumentParser(description='Parse stage time')
    parser.add_argument('--dir', type=str, help='dir to parse', required=True)
    parser.add_argument('--app', type=str, help='app', required=True)
    args = parser.parse_args()
    max_cpu = {}
    max_mem = {}
    max_totNet = {}
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
                netIOArr = stat["NetIO"].split('/')
                netRecStr = netIOArr[0].strip()
                netSntStr = netIOArr[1].strip()
                memUsg = get_byte_from_human(memUsgStr)
                netRec = get_byte_from_human(netRecStr)
                netSnt = get_byte_from_human(netSntStr)
                netSum = netRec + netSnt

                if 'cpuPer' not in stats[name]:
                    stats[name]['cpuPer'] = []
                if 'memUsg' not in stats[name]:
                    stats[name]['memUsg'] = []
                if 'netTot' not in stats[name]:
                    stats[name]['netTot'] = []
                stats[name]['cpuPer'].append(cpu_per)
                stats[name]['memUsg'].append(memUsg)
                stats[name]['netTot'].append(netSum)
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
                        max_mem[name] = 0
                        max_totNet[name] = 0
                    maxCpu = max(stats[n]['cpuPer'])
                    meanCpu = mean(stats[n]['cpuPer'])
                    if name is not None and maxCpu > max_cpu[name]:
                        max_cpu[name] = maxCpu
                    maxMem = max(stats[n]['memUsg'])/1024.0/1024.0
                    meanMem = mean(stats[n]['memUsg'])/1024.0/1024.0
                    if name is not None and maxMem > max_mem[name]:
                        max_mem[name] = maxMem
                    maxNetTot = max(stats[n]['netTot'])/1024.0/1024.0
                    if name is not None and maxNetTot > max_totNet[name]:
                        max_totNet[name] = maxNetTot

                    print(f"{n}, max cpu util: {maxCpu}, max mem usage(MB): {maxMem}, max net usage(MiB): {maxNetTot}, "
                          f"mean cpu util: {meanCpu}, mean mem usage(MB): {meanMem}")
                print()
        for n in max_cpu:
            print(f"{n},{max_cpu[n]/100.0},{max_mem[n]},{max_totNet[n]}")


if __name__ == '__main__':
    main()
