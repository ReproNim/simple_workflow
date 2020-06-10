#!/bin/bash

source /etc/fsl/fsl.sh

set -eu

export PATH=/opt/repronim/simple_workflow/miniconda/envs/bh_demo/bin:$PATH

$@