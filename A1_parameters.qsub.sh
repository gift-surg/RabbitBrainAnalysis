date
hostname

#$ -l h_rt=12:00:00
#$ -l tmem=10G
#$ -l h_vmem=10G
#$ -N "ImgBrainAnalysis"
#$ -S /bin/bash
#$ -cwd
#$ -t 1-4
#$ -e ../z_output/
#$ -o ../z_output/

SUBJECT=`sed -n ${SGE_TASK_ID}p subjects.txt`

./A2_run_python.sh $SUBJECT