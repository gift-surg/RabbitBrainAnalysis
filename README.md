# Frau Bruker

Python code to manipulate MRI data from the "Encephalopaty of prematurity" project, in collaboration with KU Leuven.

Corresponding folder structure shared on Dropbox:

├── 0_original_data
│   ├── ex_skull
│   ├── ex_vivo
│   ├── ex_vivo_op_skull
│   ├── in_vivo
│   └── lab_notes.txt
├── A_template_atlas_ex_skull
│   ├── all_subjects
│   ├── input_images
│   ├── input_masks
│   ├── local_groupwise_niftyreg_params.sh
│   ├── local_groupwise_niftyreg_run.sh
│   └── results
├── A_template_atlas_ex_vivo
│   ├── 1201
│   ├── 1203
│   ├── 1305
│   ├── 1404
│   ├── 1505
│   ├── 1507
│   ├── 1510
│   ├── 1702
│   ├── 1805
│   ├── 2002
│   ├── Finals
│   ├── LabelsDescriptors
│   ├── Preliminary
│   ├── Pyramids
│   ├── Utils
│   ├── lab_notes.txt
│   └── z_Utils
├── A_template_atlas_in_vivo
│   ├── 0802_t1
│   ├── 0904_t1
│   ├── 1501_t1
│   ├── 1504_t1
│   ├── 1508_t1
│   ├── 1509_t1
│   ├── 1511_t1
│   ├── Preliminary
│   ├── Utils
│   └── z_test_in_vivo_template_propag
├── B_pilot_analysis_ex_vivo
│   ├── 1201
│   ├── 1203
│   ├── 1305
│   ├── 1404
│   ├── 1507
│   ├── 1510
│   ├── 1702
│   ├── 1802
│   ├── 2002
│   └── lab_notes.txt
├── B_pilot_analysis_in_vivo
│   ├── 0802_t1
│   ├── 0904_t1
│   ├── 1501_t1
│   ├── 1504_t1
│   ├── 1508_t1
│   ├── 1509_t1
│   └── 1511_t1
├── C_statistical_analysis_outcome_ex_vivo
├── C_statistical_analysis_outcome_in_vivo
├── D_in_vivo_intracranial_estimation
│   ├── T1
│   ├── masks
│   ├── statistics
│   └── templates
└── setbacks_solutions.txt



Other than the pipelines to manipulate data, a converter for raw bruker data is provided.
Based on a Matlab version provided by CABI for paravision 5, a python version is available both for python 5 and 6

To use parser_bruker_txt.py run (tested Python2.7.1):

    `$ python2 parser_bruker_txt.py 0104_DWI.txt` 

It saves the required files in the same folder of the input file.

The command

    `$ python2 parser_bruker_txt.py 0104_DWI.txt -o path_to_a_folder`

saves the required files in the specified folder if exists. 

WIP: testing PV 5 and 6 converter
next WIP: refactor to NiftyPipe.
