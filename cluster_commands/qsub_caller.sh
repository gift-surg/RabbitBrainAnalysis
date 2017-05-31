#!/bin/bash

# Signal to unleash hell
# nohup ./qsub_caller.sh &

qsub -l h_rt=49:00:00 -l tmem=15G -l h_vmem=15G  -cwd  -v FOLDER=job_pipeline_project.pbs
