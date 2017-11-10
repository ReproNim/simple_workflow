**Integration Testing:** [![CircleCI](https://circleci.com/gh/ReproNim/simple_workflow.svg?style=svg)](https://circleci.com/gh/ReproNim/simple_workflow)

Note:** This demo is intended to run on OS X and GNU/Linux environments, but you can use the Docker container to run on any system you can run Docker or Singularity on.

### Notice for commercial use

The following non-free Debian packages are part of the Docker container:

non-free/science        fsl-5.0-core
non-free/science        fsl-atlases, fsl-first-data

If you are considering commercial use of the container please consult the [relevant license](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Licence).

### Information queried from NITRC-IR and stored in a google spreadsheet
https://docs.google.com/spreadsheets/d/11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA

### 1. To execute demo with Docker

First download the image
```bash
docker pull repronim/simple_workflow:latest
```

Now you can run the image as follows to test on 1 participant's data:

```bash
docker run -it --rm -v $PWD/output:/opt/repronim/simple_workflow/scripts/output \
   repronim/simple_workflow:latest run_demo_workflow.py \
   --key 11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA -n 1 
docker run -it --rm -v $PWD/output:/opt/repronim/simple_workflow/scripts/output \
   repronim/simple_workflow:latest check_output.py --ignoremissing
```

You can extend this to all participants as follows. 

```bash
docker run -it --rm -v $PWD/output:/opt/repronim/simple_workflow/scripts/output \
   repronim/simple_workflow:latest run_demo_workflow.py \
   --key 11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA
docker run -it --rm -v $PWD/output:/opt/repronim/simple_workflow/scripts/output \
   repronim/simple_workflow:latest check_output.py
```

### 2. To execute demo within your current environment

The script will check for availability of the following:

1. [FSL](https://fsl.fmrib.ox.ac.uk/)
2. curl
3. git or unzip

#### Download the script

```bash
curl -Ok https://raw.githubusercontent.com/ReproNim/simple_workflow/3a64f3ffdf174e7c8970de620aa62a9167e3134f/Simple_Prep.sh
```

#### Setup the environment. 

This will setup a complete environment within a directory
called simple_workflow. It will not add anything to your existing environment. 

Note: Because of some limitations with the underlying packages, it may determine 
that your current working directory path is too long and will ask you to move to 
a shorter directory path.

```bash
bash Simple_Prep.sh
```

#### Execute a single subject test.
```bash
bash Simple_Prep.sh test
```

#### Run the full demo on all subjects

Option 1:
```bash
bash Simple_Prep.sh replay
```

Option 2: To use the newly created environment
```bash
cd simple_workflow/scripts
export OLDPATH=$PATH
export PATH=$PWD/../miniconda/envs/bh_demo/bin:$PATH
```

Now you can run the demo script
```bash
python run_demo_workflow.py --key 11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA
python check_output.py
```

To run on one subject you can do:
```bash
python run_demo_workflow.py --key 11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA -n 1
```

To restore old environment do:
```bash
export PATH=$OLDPATH
unset OLDPATH
```

### 3. To build docker image with custom environment

Using containerization solutions, such as Docker, allows to create
multiple complete computation environments while varying versions of any
analysis pipeline components or inputs.  You could use [Simple_Prep_docker](Simple_Prep_docker)
script to generate environments based on previous [Debian](http://www.debian.org) or [Ubuntu](http://ubuntu.com) releases
for which [NeuroDebian](http://neuro.debian.net) builds of FSL [were available in the past](http://snapshot-neuro.debian.net:5002/package/fsl).

N.B.  ATM NeuroDebian snapshots repository is not widely open yet, so if
you would like to browse it, please "knock" first by running
`curl -s http://neuro.debian.net/_files/knock-snapshots` command in your shell.

#### Generate an environment

For the current test data, we generated an environment based on Debian jessie 
release with FSL 5.0.9 that was available in April 2017:

```bash
/Simple_Prep_docker jessie 20170410T000000Z
```
which will generate a local docker image `repronim:simple_prep_${USER}_jessie_20170410T000000Z`
(`${USER}` will correspond to your user name), with all necessary for computation
components installed.

You can then run the demo using the docker image run commands above by replacing 
`repronim/simple_workflow:latest` with `repronim:simple_prep_${USER}_jessie_20170410T000000Z`

##### Changing the FSL version

You can also generate an environment based on Debian jessie
release with FSL 5.0.8-3 as it was available in March of 2015 by 
simply changing the timestamp:

```bash
./Simple_Prep_docker jessie 20150306T060524Z
```

which will generate a local docker image `repronim:simple_prep_${USER}_jessie_20150306T060524Z`
(`${USER}` will correspond to your user name), with all necessary for computation
components installed.

You can then run the demo using the docker image run commands above by replacing 
`repronim/simple_workflow:latest` with `repronim:simple_prep_${USER}_jessie_20150306T060524Z`

### 4. Other containers

You can also use [Singularity](http://singularity.lbl.gov/) to run the docker 
image from DockerHub. The following commands require the development branch (post release 2.2)
or release 2.3.

```bash
singularity create -s 4000 repronim.img
singularity import repronim.img docker://repronim/simple_workflow:latest
singularity run -B $PWD/output:/opt/repronim/simple_workflow/scripts/output -c \
  --pwd /opt/repronim/simple_workflow/scripts/ repronim.img run_demo_workflow.py \
  --key 11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA -n 1
singularity run -B $PWD/output:/opt/repronim/simple_workflow/scripts/output -c \
  --pwd /opt/repronim/simple_workflow/scripts/ repronim.img check_output.py --ignoremissing
```
