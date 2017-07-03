import os
from os.path import join as jph


root_dir = os.path.abspath(os.path.dirname(__file__))
pfo_local_output = jph(os.path.dirname(root_dir), 'output')

if os.path.exists('/cluster/project0'):
    print('You are on the cluster')
    # call FSL
    # set up the roots
    root_main_cluster = '/cluster/project0/fetalsurgery/Data/MRI/KUL_preterm_rabbit_model/data'
    root_internal_template = jph(root_main_cluster, 'A_internal_template')
    root_utils = jph(root_main_cluster, 'A_data', 'Utils')
    root_study_rabbits = root_main_cluster
    bfc_corrector_cmd = '/share/apps/cmic/NiftyMIDAS/bin/niftkMTPDbc '
    root_shared_records = None
    root_fit_apps = '/home/ferraris/software_lib/NiftyFit2/niftyfit-build/fit-apps/'


elif os.path.exists('/Volumes/LC/sebastianof/rabbits/'):
    print('You are on the external hdd')
    root_main_hdd = '/Volumes/LC/sebastianof'
    root_main_dropbox = '/Users/sebastiano/Dropbox/RabbitEOP-MRI'
    root_internal_template = jph(root_main_dropbox, 'study', 'A_internal_template')
    root_docs = jph(root_main_dropbox, 'docs')
    root_study_rabbits = jph(root_main_hdd, 'rabbits')
    root_shared_records = jph(root_main_dropbox, 'study', 'C_records')
    bfc_corrector_cmd = '/Applications/niftk-16.1.0/NiftyView.app/Contents/MacOS/niftkMTPDbc '
    root_fit_apps = ''


elif os.path.exists('/Volumes/sebastianof/'):
    print('You are on pantopolium')
    root_main_pantopolium = '/Volumes/sebastianof/'
    root_main_dropbox = '/Users/sebastiano/Dropbox/RabbitEOP-MRI'
    root_internal_template = jph(root_main_dropbox, 'study', 'A_internal_template')
    root_study_rabbits = jph(root_main_pantopolium, 'rabbits')
    root_utils = jph(root_study_rabbits, 'A_data', 'Utils')
    root_shared_records = jph(root_main_dropbox, 'study', 'C_records')
    assert os.path.isdir(root_study_rabbits), 'Connect pantopolio'
    bfc_corrector_cmd = '/Applications/niftk-16.1.0/NiftyView.app/Contents/MacOS/niftkMTPDbc '
    root_fit_apps = ''

else:
    print('No source data! YOU ARE WORKING IN LOCAL!')
    root_study_rabbits = ''

pfi_excel_table_all_data = jph(root_study_rabbits, 'A_data', 'DataSummary.xlsx')
