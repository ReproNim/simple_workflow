#!/bin/bash

set -e

# Check if FSL is available
[ ! $(command -v bet) ] && echo "No bet: Make sure an FSL version is installed and available." && exit 1
echo "FSL bet is available"

# Check if curl is available
[ ! $(command -v curl) ] && echo "No curl: Make sure a version of curl is installed and available." && exit 1
echo "curl is available"

echo "Creating local directory simple_workflow to create and execute environment"
mkdir -p simple_workflow && cd simple_workflow

# Setup standalone python environment
echo "Setting up standalone conda Python environment"

if [ ! -e miniconda ]; then
    echo "Downloading miniconda"
    if [ `uname` == 'Darwin' ]; then
        curl -sSL -o miniconda.sh http://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
    else
        curl -sSL -o miniconda.sh http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
    fi

    echo "Setting up miniconda"
    chmod +x miniconda.sh
    ./miniconda.sh -b -p $PWD/miniconda
    rm miniconda.sh
fi
PATH=$PWD/miniconda/bin:$PATH

# Get the repo and Create the specific versioned python environment
if [ ! -e scripts/expected_output ]; then
    echo "Getting the analysis repo"
    if [ $(command -v git) ]; then
       git clone https://github.com/ReproNim/simple_workflow scripts
       # TODO: add git checkout of specific hash when finalized
    elif [ $(command -v unzip) ]; then
       curl -ssL -o workdir.zip https://github.com/ReproNim/simple_workflow/archive/master.zip
       # TODO: add download of specific commit hash when finalized
       unzip workdir.zip && rm workdir.zip
       mv simple_workflow-master scripts
    else
       echo "Neither git not unzip available. Cannot download scripts"
       exit 1
    fi
fi

echo "Creating and activating versioned Python environment"
if [ ! -e miniconda/envs/bh_demo ]; then
    conda env create -f scripts/environment.yml
    conda clean -tipsy
fi

if [ "$1" == "test" ]; then
    PATH=$PWD/miniconda/envs/bh_demo/bin:$PATH
    cd scripts
    python run_demo_workflow.py --key 11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA -n 1 && \
    python check_output.py
fi

export PATH
