**Integration Testing:** [![CircleCI](https://circleci.com/gh/ReproNim/simple_workflow.svg?style=svg)](https://circleci.com/gh/ReproNim/simple_workflow)

**Note:** This demo is intended to run on OS X and GNU/Linux environments.

#### Information queried from NITRC-IR and stored in a google spreadsheet
https://docs.google.com/spreadsheets/d/11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA

#### Within your current environment

##### Setup

1. Make sure FSL is available in your environment and accessible from the command line.

2. If you already have a `conda` environment, please follow the detailed steps below. 

3. If you do not have a conda environment, make sure you have `curl` and `unzip` commands available, and the following step will download and install a Python 2 conda environment with the appropriate Python packages:

```bash
curl -Ok https://raw.githubusercontent.com/ReproNim/simple_workflow/e4063fa95cb494da496565ec27c4ffe8a4901c45/Simple_Prep.sh
source Simple_Prep.sh
```

##### Run the demo

```bash
python run_demo_workflow.py --key 11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA
python check_output.py
```

To run on one subject you can do:
```bash
python run_demo_workflow.py --key 11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA -n 1
```

#### Detailed steps for setting up environment

Install miniconda if you do not have it.

For Linux:
```bash
curl -o miniconda.sh  http://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
```

For OS X:
```bash
curl -o miniconda.sh  http://repo.continuum.io/miniconda/Miniconda2-latest-MacOSX-x86_64.sh
```

Setup miniconda:
```bash
chmod +x miniconda.sh
./miniconda.sh -b
conda config --add channels conda-forge
```

If you did not add miniconda to your environment (`.bash_profile`), execute to add to your current environment:
```bash
export PATH=$HOME/miniconda2/bin:$PATH
```

#### Download the Simple Workflow repository and create the specific versioned Python environment for Nipype
```bash
curl -OsSL https://github.com/ReproNim/simple_workflow/archive/master.zip
unzip master.zip
cd simple_workflow-master
conda env create -f environment.yml
source activate bh_demo
pip install https://github.com/satra/prov/archive/enh/rdf-1.x.zip
```

### Within Docker

Using containerization solutions, such as docker, allows to create
multiple complete computation environments while varying versions of any
analysis pipeline components or inputs.  You could use [Simple_Prep_docker](Simple_Prep_docker)
script to generate environments based on previous [Debian](http://www.debian.org) or [Ubuntu](http://ubuntu.com) releases
for which [NeuroDebian](http://neuro.debian.net) builds of FSL [were available in the past](http://snapshot-neuro.debian.net:5002/package/fsl).

N.B.  ATM NeuroDebian snapshots repository is not widely open yet, so if
you would like to browse it, please "knock" first by running
`curl -s http://neuro.debian.net/_files/knock-snapshots` command in your shell.

#### Generate an environment

For an example we will generate an environment based on Debian jessie
release with FSL 5.0.8-3 as it was available in March of 2015:

```bash
./Simple_Prep_docker jessie 20150306T060524Z
```

which will generate a local docker image `repronim:simple_prep_${USER}_jessie_20150306T060524Z`
(`${USER}` will correspond to your user name), with all necessary for computation
components installed.

#### Run the demo

You can normally run a demo with only **one additional step** necessary -- setting up
environment variables (to point to FSL binaries and enable  conda environment):

```bash
docker run -it --rm repronim:simple_prep_${USER}_jessie_20150306T060524Z /bin/bash -c ' \
  . setup_environment; \
  cd simple_workflow-master \
  && python run_demo_workflow.py --key 11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA \
  && python check_output.py'
```

which would generate a new temporary container, perform analysis, run
the check, and quit.
