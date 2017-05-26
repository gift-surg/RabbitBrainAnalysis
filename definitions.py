import os
from os.path import join as jph


root_dir = os.path.abspath(os.path.dirname(__file__))


root_study_dropbox = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/study'
root_docs_dropbox = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/docs'
pfi_excel_table_PTB = jph(root_docs_dropbox, 'REoP_PTB_MRI_Data.xlsx')
pfi_excel_table_ACS = jph(root_docs_dropbox, 'REoP_ACS_MRI_Data.xlsx')
# root_pilot_study_pantopolium = '/Volumes/sebastianof/rabbits'
root_study_pantopolium = '/Volumes/sebastianof/rabbits'
