#!/usr/bin/env bash

# echo "submitting the job ${1}"
qsub -l h_rt=12:00:00 -l tmem=30G -l h_vmem=30G -N "job_sj_${1}" -cwd -v SUBJECT=${1} A1_run_python.sh
