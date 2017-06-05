#!/bin/bash

# Signal to unleash hell
# nohup ./qsub_caller.sh &

echo ${1}
qsub -l h_rt=12:00:00 -l tmem=15G -l h_vmem=15G  -cwd  -v SUBJECT=${1} job_pipeline_project.sh
