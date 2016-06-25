
```
wget http://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O miniconda.sh
chmod +x miniconda.sh
./miniconda.sh -b
```

```
conda env create -f environment.yml
source activate bh_demo
pip install https://github.com/nipy/nipype/archive/master.zip
pip install https://github.com/satra/prov/archive/enh/rdf-1.x.zip
```

```
git clone https://github.com/satra/simple_workflow.git
cd simple_workflow
python run_demo_workflow.py --key 11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA
```