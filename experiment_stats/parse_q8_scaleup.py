import argparse
import os
import subprocess as sp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--top_dir', type=str)
    args = parser.parse_args()
    results_log = os.path.join(args.top_dir, 'results.log') 
    scaleAt = 0
    startTs = 0
    with open(results_log, 'r') as f:
        for line in f:
            if 'scale at' in line:
                l = line.strip().split()
                scaleAt = int(l[-1])
                break
    ret = sp.run(['grep', '-r', 'StartTs', os.path.join(args.top_dir, 'logs')], stdout=sp.PIPE)
    lines = ret.stdout.decode('utf-8').split('\n')
    for line in lines:
        l = line.strip().split()
        if l:
            ts = int(l[-1])
            if startTs == 0 or ts < startTs:
                startTs = ts
    print('scaleAt: {}, startTs: {}'.format(scaleAt, startTs))
    ret = sp.run(['grep', '-r', 'final mark, epoch', os.path.join(args.top_dir, 'logs')], stdout=sp.PIPE)
    lines = ret.stdout.decode('utf-8').split('\n')
    final_mark = []
    groupby_final_mark = []
    join_stream_final_mark = []
    for line in lines:
        content = line.strip().split(':')[-1]
        l = content.split(', ')
        if len(l) > 1:
            epoch_str = l[1]
            if 'epoch 1' in epoch_str:
                print(line)
                ts = int(l[2].split()[-1])
                final_mark.append(ts)
                if 'GroupBy' in l[0]:
                    groupby_final_mark.append(ts)
                if 'JoinStream' in l[0]:
                    join_stream_final_mark.append(ts)
    print()

    ret = sp.run(['grep', '-r', 'restore, epoch', os.path.join(args.top_dir, 'logs')], stdout=sp.PIPE)
    lines = ret.stdout.decode('utf-8').split('\n')
    restore_ts = []
    groupby_restore_ts = []
    join_stream_restore_ts = []
    for line in lines:
        content = line.strip().split(',')
        if len(content) > 1:
            epoch_str = content[1]
            if 'epoch: 2' in epoch_str:
                print(line)
                ts = int(epoch_str.split()[-1])
                restore_ts.append(ts)
                if 'GroupBy' in line:
                    groupby_restore_ts.append(ts)
                if 'JoinStream' in line:
                    join_stream_restore_ts.append(ts)

    last_mark = max(final_mark)
    first_restore = min(restore_ts)
    print('last_mark: {}, first_restore: {}, gap: {}'.format(last_mark, first_restore, first_restore - last_mark))
    last_groupby_mark = max(groupby_final_mark)
    last_join_stream_mark = max(join_stream_final_mark)
    first_groupby_restore = min(groupby_restore_ts)
    first_join_stream_restore = min(join_stream_restore_ts)
    print('last_groupby_mark: {}, first_groupby_restore: {}, gap: {}'.format(last_groupby_mark, first_groupby_restore, first_groupby_restore - last_groupby_mark))
    print('last_join_stream_mark: {}, first_join_stream_restore: {}, gap: {}'.format(last_join_stream_mark, first_join_stream_restore, first_join_stream_restore - last_join_stream_mark))

    
if __name__ == '__main__':
    main()
