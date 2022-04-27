#!/bin/bash
set -euo pipefail

/mnt/efs/workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances
./1prod_1t_1par_100b.sh
./1prod_1t_1par_1kb.sh
./1prod_1t_1par_4kb.sh
./1prod_1t_1par_16kb.sh
/mnt/efs/workspace/research-helper-scripts/microservice_helper stop-machines
