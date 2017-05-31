import os
from os.path import join as jph


root_dir = os.path.abspath(os.path.dirname(__file__))

print(root_dir)

if root_dir == '':
    # you are on the cluster:
    root_main_cluster = ''
    root_internal_template = jph(root_main_cluster, 'internal_template')
    root_docs = jph(root_main_cluster, 'docs')
    root_study_rabbits = jph(root_main_cluster, 'study')


elif root_dir == '':
    # you are on the external hdd
    root_main_hdd = '/Volumes/LC/rabbits'
    root_main_dropbox = '/Users/sebastiano/Dropbox/RabbitEOP-MRI'
    root_internal_template = jph(root_main_dropbox, 'study', 'A_internal_template')
    root_docs = jph(root_main_dropbox, 'docs')
    root_study_rabbits = jph(root_main_hdd, 'study')
    root_shared_records = jph(root_main_dropbox, 'study', 'C_records')


else:
    # you are on pantopolium
    root_main_pantopolium = '/Volumes/sebastianof/'
    root_main_dropbox = '/Users/sebastiano/Dropbox/RabbitEOP-MRI'
    root_internal_template = jph(root_main_dropbox, 'study', 'A_internal_template')
    root_docs = jph(root_main_dropbox, 'docs')
    root_study_rabbits = jph(root_main_pantopolium, 'rabbits')
    root_shared_records = jph(root_main_dropbox, 'study', 'C_recor'
                                                          'ds')
    assert os.path.isdir(root_study_rabbits), 'Connect pantopolio'

pfi_excel_table_PTB = jph(root_docs, 'REoP_PTB_MRI_Data.xlsx')
pfi_excel_table_ACS = jph(root_docs, 'REoP_ACS_MRI_Data.xlsx')
pfi_excel_table_PTB_templ = jph(root_docs, 'REoP_PTB_Template_MRI_Data.xlsx')
