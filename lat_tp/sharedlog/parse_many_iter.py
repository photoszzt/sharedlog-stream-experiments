import argparse
import os
import json
from statistics import quantiles

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    args = parser.parse_args()
    all_time = []
    for i in range(args.num):
        dirpath = os.path.join(args.dir, str(i))
        fname = os.path.join(dirpath, '16Kb', 'results.log')
        with open(fname, 'r') as f:
            for line in f:
                if "ProdConsumeLatencies" in line:
                    st = json.loads(line)
                    all_time.extend(st['ProdConsumeLatencies'])
    p50 = quantiles(all_time, n=100)[49]
    p99 = quantiles(all_time, n=100)[98]
    print(f"p50: {p50} us, p99: {p99} us")



if __name__ == '__main__':
    main()
