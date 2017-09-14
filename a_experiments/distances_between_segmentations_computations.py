from os.path import join as jph
from labels_manager.main import LabelsManager as LM

from labels_manager.tools.caliber.distances import dice_score, dispersion, covariance_distance, hausdorff_distance
from a_experiments.distances_between_segmentations_paths import pfo_manual, pfo_study, pfo_automatic, pfo_output, \
    modalities, pfo_intermediate_files


if __name__ == '__main__':

    m = LM()

    for mod in modalities:
        print '\n\n\n---------------'
        print mod
        print '---------------\n'

        # take MV automatic with the manual original
        pfi_automatic_MV = jph(pfo_automatic, 'target1111_T1_segm_{}.nii.gz'.format(mod))
        pfi_manual_1 = jph(pfo_manual, '1111_approved.nii.gz')

        where_to_save = jph(pfo_output, 'distances_approved_{}.pickle'.format(mod))

        m.measure.dist(pfi_automatic_MV, pfi_manual_1, metrics=(dice_score, dispersion, covariance_distance,
                                                                hausdorff_distance),
                       intermediate_files_folder_name=pfo_intermediate_files, where_to_save=where_to_save)
