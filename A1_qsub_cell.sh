#!/usr/bin/env bash

# echo "submitting the job ${1}"
#qsub -l h_rt=12:00:00 -l tmem=15G -l h_vmem=15G -N "Job${1}" -cwd -v SUBJECT=${1} A2_run_python.sh
qsub -l h_rt=00:10:00 -l tmem=5G -l h_vmem=5G -N "JobD${1}" -cwd -v SUBJECT=${1} A2_run_python.sh