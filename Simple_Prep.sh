#!/bin/bash

set -e

# Check if FSL is available
if [ ! $(command -v bet) ]; then
    if [ -f /etc/fsl/fsl.sh ]; then
        source /etc/fsl/fsl.sh
    else
        echo "No bet: Make sure an FSL version - https://fsl.fmrib.ox.ac.uk/ - is installed and available." && kill -INT $$
    fi
fi
echo "FSL bet is available"

# Check if curl is available
[ ! $(command -v curl) ] && echo "No curl: Make sure a version of curl is installed and available." && kill -INT $$
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
       cd scripts
       git checkout a26e0c01227c8baa0756b9e95a0442d69e9c9e10
    elif [ $(command -v unzip) ]; then
       curl -ssL -o workdir.zip https://github.com/ReproNim/simple_workflow/archive/a26e0c01227c8baa0756b9e95a0442d69e9c9e10.zip
       unzip workdir.zip && rm workdir.zip
       mv simple_workflow-a26e0c01227c8baa0756b9e95a0442d69e9c9e10 scripts
    else
       echo "Neither git not unzip available. Cannot download scripts"
       exit 1
    fi
fi

echo "Creating and activating versioned Python environment"
if [ ! -e miniconda/envs/bh_demo/bin/nipype_display_crash ]; then
    if [ -e miniconda/envs/bh_demo/ ]; then
        rm -rf miniconda/envs/bh_demo
    fi
    if [ ${#PWD} -gt 36 ]; then
        echo "---- BEGIN SIMPLE_PREP SCRIPT WARNING ----

If you receive a PaddingError with the following command, your current
working directory path length ${#PWD} is longer than 36 chars. Move to
a working directory path that is at most 36 chars. Run:

echo \${#PWD}

to check.

---- END SIMPLE_PREP SCRIPT WARNING ----"
    fi
    conda env create -f scripts/environment.yml
    conda clean -tipsy
fi

if [ "$1" == "test" ]; then
    PATH=$PWD/miniconda/envs/bh_demo/bin:$PATH
    cd scripts
    python run_demo_workflow.py --key 11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA -n 1 && \
    python check_output.py --ignoremissing
fi
if [ "$1" == "replay" ]; then
    PATH=$PWD/miniconda/envs/bh_demo/bin:$PATH
    cd scripts
    python run_demo_workflow.py --key 11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA && \
    python check_output.py
fi

export PATH
