#!/bin/bash
set -xeuo pipefail
source /etc/lsb-release
echo $DISTRIB_RELEASE
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

sudo apt install gnupg ca-certificates curl
curl -s https://repos.azul.com/azul-repo.key | sudo gpg --dearmor -o /usr/share/keyrings/azul.gpg
echo "deb [signed-by=/usr/share/keyrings/azul.gpg] https://repos.azul.com/zulu/deb stable main" | sudo tee /etc/apt/sources.list.d/zulu.list

sudo apt-get update
sudo apt-get install -y build-essential autoconf automake pkg-config libtool numactl \
  clang
sudo apt install -y zulu21-jdk

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

for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
      sudo apt-get update

sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-compose
sudo usermod -aG docker $USER

curl -LO https://github.com/protocolbuffers/protobuf/releases/download/v26.1/protoc-26.1-linux-x86_64.zip
unzip protoc-26.1-linux-x86_64.zip -d $HOME/.local
rm protoc-26.1-linux-x86_64.zip
