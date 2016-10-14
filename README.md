**Integration Testing:** [![CircleCI](https://circleci.com/gh/ReproNim/simple_workflow.svg?style=svg)](https://circleci.com/gh/ReproNim/simple_workflow)

**Note:** This demo is intended to run on OS X and Linux environments.

#### Information queried from NITRC-IR and stored in a google spreadsheet
https://docs.google.com/spreadsheets/d/11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA

#### Setup your own environment
1. Make sure FSL is available in your environment and accessible from the command line.

2. If you already have a `conda` environment, please follow the detailed steps below. 

3. If you do not have a conda environment, the following step will download and install a Python 2 conda environment with the appropriate python packages. 

```bash
curl -Ok https://raw.githubusercontent.com/ReproNim/simple_workflow/master/Simple_Prep.sh
source Simple_Prep.sh
```

#### Run the demo

```bash
python run_demo_workflow.py --key 11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA
python check_output.py
```

To run on one subject you can do:
```bash
python run_demo_workflow.py --key 11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA -n 1
```

### Detailed steps for setting up environment

Install miniconda if you do not have it.

For Linux:
```bash
curl -o miniconda.sh  http://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
```

For OS X:
```bash
curl -o miniconda.sh  http://repo.continuum.io/miniconda/Miniconda2-latest-MacOSX-x86_64.sh
```

Setup miniconda.
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
