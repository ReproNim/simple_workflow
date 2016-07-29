[![CircleCI](https://circleci.com/gh/satra/simple_workflow.svg?style=svg)](https://circleci.com/gh/satra/simple_workflow)

#### Information queried and stored in a google spreadsheet
https://docs.google.com/spreadsheets/d/11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA

#### Setup standalone python environment

At the end of the miniconda install it will ask you to add it to your bash profile. If you do not add it, then you will need to make sure the conda binary is in your path.
```
wget http://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O miniconda.sh
chmod +x miniconda.sh
./miniconda.sh -b
conda config --add channels conda-forge
```

If you did not add miniconda to your environment, execute:
```
export PATH=$HOME/miniconda2/bin:$PATH
```

#### get the repo and create the specific versioned python environment
```
git clone https://github.com/satra/simple_workflow.git
cd simple_workflow
conda env create -f environment.yml
source activate bh_demo
pip install https://github.com/satra/prov/archive/enh/rdf-1.x.zip
```

#### Run the demo

```
python run_demo_workflow.py --key 11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA
python check_output.py
```
