import os
from os.path import join as jph


root_dir = os.path.abspath(os.path.dirname(__file__))
pfo_local_output = jph(os.path.dirname(root_dir), 'output')

multi_atlas_subjects    = ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502', '3301', '3404']
multi_atlas_BT_subjects = ['2503', '2608', '2702', '4504', '4903', '4905', '5001', '5007']
multi_atlas_W8_subjects = ['12503']

if os.path.exists('/cluster/project0'):
    print('You are on the cluster')
    # call FSL
    # set up the roots
    root_main_cluster   = '/cluster/project0/fetalsurgery/Data/MRI/KUL_preterm_rabbit_model/data'
    root_atlas          = jph(root_main_cluster, 'A_MultiAtlas')
    root_atlas_BT       = jph(root_main_cluster, 'A_MultiAtlas_BT')
    root_atlas_W8       = jph(root_main_cluster, 'A_MultiAtlas_W8')
    root_utils          = jph(root_main_cluster, 'A_data', 'Utils')
    root_study_rabbits  = root_main_cluster
    bfc_corrector_cmd   = '/share/apps/cmic/NiftyMIDAS/bin/niftkMTPDbc'
    root_shared_records = ''
    root_fit_apps       = '/home/ferraris/software_lib/NiftyFit2/niftyfit-build/fit-apps/'
    num_cores_run       = 8

elif os.path.exists('/Volumes/SmartWare/'):
    print('You are on emporium')
    root_main_dropbox   = '/Users/sebastiano/Dropbox/RabbitEOP-MRI'
    assert os.path.isdir(root_main_dropbox), 'No dropbox available'
    root_main_emporium  = '/Volumes/SmartWare/'
    root_study_rabbits  = jph(root_main_emporium, 'rabbit')
    root_atlas          = jph(root_study_rabbits, 'A_MultiAtlas')
    root_atlas_BT       = jph(root_study_rabbits, 'A_MultiAtlas_BT')
    root_atlas_W8       = jph(root_study_rabbits, 'A_MultiAtlas_W8')
    root_utils          = jph(root_study_rabbits, 'A_data', 'Utils')
    root_utils          = jph(root_study_rabbits, 'A_data', 'Utils')
    root_shared_records = jph(root_main_dropbox, 'study', 'C_records')
    bfc_corrector_cmd   = '/Applications/niftk-16.1.0/NiftyView.app/Contents/MacOS/niftkMTPDbc'
    root_fit_apps       = ''
    num_cores_run       = 8

elif os.path.exists('/Volumes/sebastianof/'):
    print('You are on pantopolium')
    root_main_pantopolium = '/Volumes/sebastianof/'
    root_main_dropbox     = '/Users/sebastiano/Dropbox/RabbitEOP-MRI'
    root_atlas            = jph(root_main_pantopolium, 'rabbits', 'A_MultiAtlas')
    root_atlas_BT         = jph(root_main_pantopolium, 'rabbits', 'A_MultiAtlas_BT')
    root_atlas_W8         = jph(root_main_pantopolium, 'rabbits', 'A_MultiAtlas_W8')
    root_study_rabbits    = jph(root_main_pantopolium, 'rabbits')
    root_utils            = jph(root_study_rabbits, 'A_data', 'Utils')
    root_shared_records   = jph(root_main_dropbox, 'study', 'C_records')
    bfc_corrector_cmd     = '/Applications/niftk-16.1.0/NiftyView.app/Contents/MacOS/niftkMTPDbc'
    root_fit_apps         = ''
    num_cores_run         = 8


elif os.path.exists('/Volumes/LC/sebastianof/rabbits/'):
    print('You are on the external hdd')
    root_main_hdd       = '/Volumes/LC/sebastianof'
    root_main_dropbox   = '/Users/sebastiano/Dropbox/RabbitEOP-MRI'
    root_atlas          = jph(root_main_hdd, 'rabbits', 'A_MultiAtlas')
    root_atlas_BT       = jph(root_main_hdd, 'rabbits', 'A_MultiAtlas_BT')
    root_atlas_W8       = jph(root_main_hdd, 'rabbits', 'A_MultiAtlas_W8')
    root_docs           = jph(root_main_dropbox, 'docs')
    root_study_rabbits  = jph(root_main_hdd, 'rabbits')
    root_shared_records = jph(root_main_dropbox, 'study', 'C_records')
    bfc_corrector_cmd   = '/Applications/niftk-16.1.0/NiftyView.app/Contents/MacOS/niftkMTPDbc'
    root_fit_apps       = ''
    num_cores_run       = 8

else:
    print('NO SOURCE DATA! YOU ARE WORKING IN LOCAL! - connect pantopolium or emporium to access the main data set.')
    root_study_rabbits = ''
    root_utils         = ''
    root_main_dropbox  = '/Users/sebastiano/Dropbox/RabbitEOP-MRI'
    root_atlas_BT      = ''
    root_atlas         = jph(root_main_dropbox, 'study', 'A_MultiAtlas')
    bfc_corrector_cmd  = '/Applications/niftk-16.1.0/NiftyView.app/Contents/MacOS/niftkMTPDbc'
    num_cores_run      = 8

pfi_excel_table_all_data = jph(root_study_rabbits, 'A_data', 'DataSummary.xlsx')
pfo_subjects_parameters = jph(root_study_rabbits, 'A_data', 'Utils', 'subjects_parameters')
pfi_labels_descriptor = jph(root_atlas, 'labels_descriptor.txt')
