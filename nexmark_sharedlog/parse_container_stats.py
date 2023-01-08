import argparse
import os
import json
from statistics import mean


def main():
    parser = argparse.ArgumentParser(description='Parse stage time')
    parser.add_argument('--dir', type=str, help='dir to parse', required=True)
    args = parser.parse_args()
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
            print(fname)
            for n in stats:
                print(f"{n},max cpu util: {max(stats[n]['cpuPer'])},mean cpu util: {mean(stats[n]['cpuPer'])}"
                      f"max mem usage(MB): {max(stats[n]['memUsg'])/1024.0/1024.0},"
                      f"mean mem usage(MB): {mean(stats[n]['memUsg'])/1024.0/1024.0}")
            print()


if __name__ == '__main__':
    main()
