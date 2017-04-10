#!/bin/bash

source /etc/fsl/fsl.sh
export PATH=/opt/repronim/simple_workflow/miniconda/envs/bh_demo/bin:$PATH

python $@
