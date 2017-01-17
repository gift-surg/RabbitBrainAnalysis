"""
Functional for the creation of the template.

Pipeline to process the data for each subject ex_vivo subject in the pilot study.
The processing will orient in histological coordinate all the subjects in the appropriate
places for the folder structure.
Modalities to be processed and oriented:

> T1
> ADC
> FA
> V1 (DTI main eigenvector)
> b0

(MSME_T2 not reasonably usable in histological coordinates without a super resolution approach.)
Dlways process T1 before DWI.

"""

from pipelines_pilot.A_template_atlas_ex_vivo.pre_process_T1 import process_T1

subjects = ['1201', '1203', '1305', '1404', '1505', '1507', '1510', '1702', '1805', '2002']
# subjects = ['1201']

for sj in subjects:
    process_T1(sj, delete_intermediate_steps=False)

