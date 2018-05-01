import numpy as np
import pandas as pa
import pickle
from os.path import join as jph

from LABelsToolkit.tools.descriptions.manipulate_descriptors import LabelsDescriptorManager as LdM

from tools.definitions import root_study_rabbits, pfo_subjects_parameters, pfi_labels_descriptor
from main_pipeline.A0_main.main_controller import ListSubjectsManager

from collections import OrderedDict


ptb_related_regions = OrderedDict()
ptb_related_regions['CerebellarHemisphere']        = [179, 180]
ptb_related_regions['Thalamus']                    = [83, 84]
ptb_related_regions['Hippocampus']                 = [31, 32]
ptb_related_regions['InternalCapsule']             = [223, 224]
ptb_related_regions['CaudateNucleus']              = [69, 70]
ptb_related_regions['CorpusCallosum']              = [218]
ptb_related_regions['MedialPrefrontalAndFrontal']  = [5, 6, 7, 8]


if __name__ == '__main__':

    ldm = LdM(pfi_labels_descriptor)
    label_descriptor_dict = ldm.get_dict()

    sj_list = ['12307', '12308', '12402', '12504', '12505', '12607', '12608', '12609', '12610']

    # total volumes original coordinates as histogram:

    tot_vols = np.zeros(len(sj_list), dtype=np.float64)

    for sj_index, sj_id in enumerate(sj_list):

        sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj_id), 'r'))
        study = sj_parameters['study']
        category = sj_parameters['category']
        root_subject_input = jph(root_study_rabbits, 'A_data', study, category, sj_id)

        pfi_report_vols = jph(root_subject_input, 'report', '{}_vol_regions.csv'.format(sj_id))

        df_volumes = pa.read_csv(pfi_report_vols)

        tot_vols[sj_index] = df_volumes.loc[df_volumes['Labels'] < 255].loc[df_volumes['Labels'] > 0]['Volume'].sum()

    root_subject_output = jph(root_study_rabbits, 'B_stats', 'general')



    print tot_vols


    # total volumes stereotaxic coordinates as histogram:

    #
