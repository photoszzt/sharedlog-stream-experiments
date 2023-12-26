#!/bin/bash
set -xeuo pipefail
source /etc/lsb-release
echo $DISTRIB_RELEASE
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

sudo apt-get update
sudo apt-get install -y build-essential autoconf automake pkg-config libtool numactl \
  clang

go_tar=go1.21.5.linux-amd64.tar.gz
wget https://go.dev/dl/${go_tar} -O $HOME/${go_tar}
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf $HOME/${go_tar} || true
echo 'export PATH=$PATH:/usr/local/go/bin' >> $HOME/.profile
rm $HOME/${go_tar} || true

if [ ! -d $HOME/mambaforge ]; then
    wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh
    bash Mambaforge-Linux-x86_64.sh -b
    rm Mambaforge-Linux-x86_64.sh
    source $HOME/mambaforge/bin/activate && mamba init
fi

if ! which rustc; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y;
    source ~/.cargo/env
fi

source $HOME/.cargo/env

# install gotask
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b ~/.local/bin
