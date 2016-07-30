#!/bin/bash
# Setup standalone python environment
echo "Setup standalone python environment"

if [ `uname` == 'Darwin' ]; then
    wget http://repo.continuum.io/miniconda/Miniconda2-latest-MacOSX-x86_64.sh -O miniconda.sh
else
    wget http://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O miniconda.sh
fi
chmod +x miniconda.sh
./miniconda.sh -b
export PATH=$HOME/miniconda2/bin:$PATH
conda config --add channels conda-forge

# Get the repo and Create the specific versioned python environment
echo "Get the repo and Create the specific versioned python environment"

git clone https://github.com/satra/simple_workflow.git
cd simple_workflow
conda env create -f environment.yml
source activate bh_demo
pip install https://github.com/satra/prov/archive/enh/rdf-1.x.zip
