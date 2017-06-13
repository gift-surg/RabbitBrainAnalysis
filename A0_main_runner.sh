#!/bin/bash

export PATH=/share/apps/fsl-5.0.8/bin/:${PATH}
export PATH=/home/ferraris/software_lib/NiftyFit2/niftyfit-build/fit-apps/:${PATH}
export LD_LIBRARY_PATH=/share/apps/cmic/NiftyMIDAS/bin/:${LD_LIBRARY_PATH}

qsub A1_parameters.qsub.sh
