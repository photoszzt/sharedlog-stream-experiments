#!/bin/bash
/mnt/efs/workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances
DURATION=900
COUNT=12500000
COUNT_NAME=12.5M
# ./nexmark.sh --app q1 --exp_dir ./q1/4src/4_2xlarge_tran_${DURATION}_${COUNT_NAME}/ --nins 4 --nsrc 4 --serde msgp --duration $DURATION --nevents ${COUNT}
# ./nexmark.sh --app q2 --exp_dir ./q2/4src/4_2xlarge_tran_${DURATION}_${COUNT_NAME}/ --nins 4 --nsrc 4 --serde msgp --duration $DURATION --nevents ${COUNT}
./nexmark.sh --app q3 --exp_dir ./q3/4src/4_2xlarge_tran_${DURATION}_${COUNT_NAME}/ --nins 4 --nsrc 4 --serde msgp --duration $DURATION --nevents ${COUNT}
./nexmark.sh --app q5 --exp_dir ./q5/4src/4_2xlarge_tran_${DURATION}_${COUNT_NAME}/ --nins 4 --nsrc 4 --serde msgp --duration $DURATION --nevents ${COUNT}
./nexmark.sh --app q8 --exp_dir ./q8/4src/4_2xlarge_tran_${DURATION}_${COUNT_NAME}/ --nins 4 --nsrc 4 --serde msgp --duration $DURATION --nevents ${COUNT}

/mnt/efs/workspace/research-helper-scripts/microservice_helper stop-machines
