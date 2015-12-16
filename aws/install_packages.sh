#!/usr/bin/env bash

sudo apt-update && sudo apt-get -y dist-upgrade

# https://github.com/yyuu/pyenv/wiki/Common-build-problems
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev
sudo apt-get install git
