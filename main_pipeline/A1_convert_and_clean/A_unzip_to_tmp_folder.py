import os
from os.path import join as jph
import pickle

from tools.definitions import pfo_subjects_parameters
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.definitions import root_study_rabbits
from LABelsToolkit.tools.aux_methods.utils import print_and_run


def unzipper_given_pfi_input_and_pfo_output(pfi_in, pfo_out, sj_name, controller):
    """
    Unzipper auxiliary function related to subject name and controller, with path established a priori.
    Externalised to avoid code repetitions, as called twice.
    :param pfi_in: path to .zip file input
    :param pfo_out: path to folder output where to unzip.
    :param sj_name: usual sj parameter
    :param controller: controller filetered from previous methods.
    :return:
    """
    # Create folder structure:
    if controller['create_tmp_folder_structure']:
        print_and_run('mkdir -p {}'.format(pfo_out))

    # Unzip:
    if controller['unzip']:
        cmd = 'tar -xvf {} -C {}'.format(pfi_in, pfo_out)
        print cmd
        print_and_run(cmd)

    # Rename:
    if controller['rename']:
        file_found = 0
        for p in os.listdir(pfo_out):

            if '_HVDM_{}_'.format(sj_name) in p or '_{}_'.format(sj_name) in p:
                file_found += 1
                pfi_unzipped_old_name = jph(pfo_out, p)
                pfi_unzipped_new_name = jph(pfo_out, sj_name)
                cmd = 'mv {} {}'.format(pfi_unzipped_old_name, pfi_unzipped_new_name)
                print_and_run(cmd)
            elif p == str(sj_name):
                # file is already in the correct format
                file_found += 1

        if file_found != 1:
            raise IOError(
                'Unzipped file was saved with a different naming convention. We found {} with string {} in it. '
                'Manual work required. (Probably two subjects with the same name? '
                'Probably different covention to save filenames?)'.format(file_found, '_HVDM_{}_'.format(sj_name)))


def unzip_single_sj(sj, controller):

    print('- Unzip subject {} '.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    pfi_input_sj_zip = jph(root_study_rabbits, '00_raw_data_zipped', study, category, '{}.zip'.format(sj))
    assert os.path.exists(pfi_input_sj_zip), 'Zipped file {} does not exists'.format(pfi_input_sj_zip)
    pfo_output = jph(root_study_rabbits, '01_raw_data_unzipped_TMP', study, category)

    unzipper_given_pfi_input_and_pfo_output(pfi_input_sj_zip, pfo_output, sj, controller)

    # Check for external files
    # |---> Secondary study to be merged. If any unzip it as well.
    sj_exts = sj_parameters['merge_with']
    if sj_exts is not None:
        print('\nExternal files related to subject {} found. Unzippin in started.'.format(sj))
        for sj_ext in sj_exts:
            print('Unzipping file {} for subject {}'.format(sj_ext, sj))
            pfi_input_sj_ext_zip = jph(root_study_rabbits, '00_raw_data_zipped', study, category, sj_ext + '.zip')

            if not os.path.exists(pfi_input_sj_ext_zip):
                raise IOError('Declared external study for subject {} in folder {} not found'.format(sj_ext, pfi_input_sj_ext_zip))
            pfo_output_sj_ext = jph(root_study_rabbits, '01_raw_data_unzipped_TMP', study, category, sj_ext)
            unzipper_given_pfi_input_and_pfo_output(pfi_input_sj_ext_zip, pfo_output_sj_ext, sj_ext, controller)
            print('\n\n')


def unzip_subjects_from_list(subj_list, controller):
    print('\n\n UNZIPPING SUBJECTS {} \n'.format(subj_list))
    for sj in subj_list:
        unzip_single_sj(sj, controller)


if __name__ == '__main__':

    controller_ = {'create_tmp_folder_structure' : True,
                   'unzip'                       : True,
                   'rename'                      : True
                   }

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo  = False
    lsm.execute_PTB_in_vivo  = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo  = False

    lsm.input_subjects = ['4303', ]
    lsm.update_ls()

    print lsm.ls

    unzip_subjects_from_list(lsm.ls, controller_)
