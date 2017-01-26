#!/bin/bash
# Setup standalone python environment

echo "Setting up standalone conda Python environment"

if [ `uname` == 'Darwin' ]; then
    curl -sSL -o miniconda.sh http://repo.continuum.io/miniconda/Miniconda2-latest-MacOSX-x86_64.sh
else
    curl -sSL -o miniconda.sh http://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
fi
chmod +x miniconda.sh
./miniconda.sh -b
export PATH=$HOME/miniconda2/bin:$PATH
conda config --add channels conda-forge

# Get the repo and Create the specific versioned python environment
echo "Getting the analysis repo"

curl -OksSL https://github.com/ReproNim/simple_workflow/archive/master.zip
unzip master.zip
cd simple_workflow-master

echo "Creating specificly versioned Python environment"
conda env create -f environment.yml
source activate bh_demo
pip install https://github.com/satra/prov/archive/enh/rdf-1.x.zip
