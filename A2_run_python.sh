#!/bin/bash

module load fsl/5.0.9
source $FSLDIR/etc/fslconf/fsl.sh

/home/ferraris/py_venvs/v2/bin/python cluster_commands/call_executer.py -i $SUBJECT
