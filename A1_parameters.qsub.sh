date
hostname

#$ -l h_rt=12:00:00
#$ -l tmem=8G
#$ -l h_vmem=8G
#$ -N "ImgBrainAnalysis"
#$ -S /bin/bash
#$ -cwd
#$ -t 6-6
#$ -e ../z_output/
#$ -o ../z_output/

SUBJECT=`sed -n ${SGE_TASK_ID}p subjects_all.txt`

echo $SUBJECT

./A2_run_python.sh $SUBJECT
