import argparse
import os
from statistics import mean
# from matplotlib import pyplot as plt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True)
    parser.add_argument('--target', required=True)
    args = parser.parse_args()
    dpaths = []
    for root, dirs, files in os.walk(args.dir):
        for dname in dirs:
            dpath = os.path.join(root, dname)
            dpaths.append(dpath)
    p50Stats = {}
    p99Stats = {}
    for dpath in dpaths:
        for root, dirs, files in os.walk(dpath):
            for fname in files:
                fpath = os.path.join(root, fname)
                p50Stats[fname] = []
                p99Stats[fname] = []
                with open(fpath, 'r') as f:
                    for line in f:
                        if args.target in line and 'p50' in line:
                            sp = line.strip().split(",")
                            p50 = sp[1].strip().split("=")[1]
                            p99 = sp[3].strip().split("=")[1]
                            p50Stats[fname].append(p50)
                            p99Stats[fname].append(p99)
    names = p50Stats.keys()
    for name in names:
        p50arr = p50Stats[name]
        p99arr = p99Stats[name]
        if p50arr:
            print(name, p50arr, p99arr)
            print(f"p50 avg: {mean(p50arr)}")
            print(f"p99 avg: {mean(p99arr)}")
            


if __name__ == '__main__':
    main()
