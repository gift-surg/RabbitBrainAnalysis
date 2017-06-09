date
hostname

#$ -l h_rt=00:2:00
#$ -l tmem=2G
#$ -l h_vmem=2G
#$ -N "SimpleTest"
#$ -S /bin/bash
#$ -cwd
#$ -t 1-2
#$ -e ../z_output/
#$ -o ../z_output/

SUBJECT=`sed -n ${SGE_TASK_ID}p subjects.txt`

./A2_run_python.sh $SUBJECT
