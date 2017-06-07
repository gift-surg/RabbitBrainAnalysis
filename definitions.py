import os
from os.path import join as jph


root_dir = os.path.abspath(os.path.dirname(__file__))


if os.path.exists('/cluster/project0'):
    print('you are on the cluster:')
    root_main_cluster = '/cluster/project0/fetalsurgery/Data/MRI/KUL_preterm_rabbit_model/data'
    root_internal_template = jph(root_main_cluster, 'A_internal_template')
    root_utils = jph(root_main_cluster, 'A_data', 'Utils')
    root_study_rabbits = root_main_cluster
    bfc_corrector_cmd = '/share/apps/cmic/NiftyMIDAS/bin/niftkMTPDbc '


elif os.path.exists('/Volumes/LC/rabbits'):
    print('you are on the external hdd')
    root_main_hdd = '/Volumes/LC/rabbits'
    root_main_dropbox = '/Users/sebastiano/Dropbox/RabbitEOP-MRI'
    root_internal_template = jph(root_main_dropbox, 'study', 'A_internal_template')
    root_docs = jph(root_main_dropbox, 'docs')
    root_study_rabbits = jph(root_main_hdd, 'study')
    root_shared_records = jph(root_main_dropbox, 'study', 'C_records')
    bfc_corrector_cmd = '/Applications/niftk-16.1.0/NiftyView.app/Contents/MacOS/niftkMTPDbc '


elif os.path.exists('/Volumes/sebastianof/'):
    print('you are on pantopolium')
    root_main_pantopolium = '/Volumes/sebastianof/'
    root_main_dropbox = '/Users/sebastiano/Dropbox/RabbitEOP-MRI'
    root_internal_template = jph(root_main_dropbox, 'study', 'A_internal_template')
    root_study_rabbits = jph(root_main_pantopolium, 'rabbits')
    root_utils = jph(root_study_rabbits, 'A_data', 'Utils')
    root_shared_records = jph(root_main_dropbox, 'study', 'C_records')
    assert os.path.isdir(root_study_rabbits), 'Connect pantopolio'
    bfc_corrector_cmd = '/Applications/niftk-16.1.0/NiftyView.app/Contents/MacOS/niftkMTPDbc '

else:
    raise IOError('No source data!')

pfi_excel_table_all_data = jph(root_study_rabbits, 'A_data', 'DataSummary.xlsx')
