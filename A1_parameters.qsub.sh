date
hostname

#$ -l h_rt=12:00:00
#$ -l tmem=25G
#$ -l h_vmem=25G
#$ -N "ImgACS_1"
#$ -S /bin/bash
#$ -cwd
#$ -t 1
#$ -e ../z_output/
#$ -o ../z_output/

SUBJECT=`sed -n ${SGE_TASK_ID}p subjects_ACS_ex_vivo.txt`


export PATH=/share/apps/fsl-5.0.8/bin/:${PATH}
export PATH=/home/ferraris/software_lib/NiftyFit2/niftyfit-build/fit-apps/:${PATH}
export LD_LIBRARY_PATH=/share/apps/cmic/NiftyMIDAS/bin/:${LD_LIBRARY_PATH}

EXEC=/home/ferraris/py_venvs/v2/bin/python
CALLER=cluster_commands/call_executer.py

echo $EXEC $CALLER -i $SUBJECT

$EXEC $CALLER -i $SUBJECT
