"""
Measurements on labels.
"""
import numpy as np
import nibabel as nib
import copy
from tabulate import tabulate


class SegmentationAnalyzer(object):

    def __init__(self, pfi_segmentation, pfi_description=None, pfi_scalar_im=None, icv_factor=None, return_mm3=True):
        self.pfi_segmentation = pfi_segmentation
        self.return_mm3 = False
        self.pfi_description = pfi_description
        self.pfi_scalar_im = pfi_scalar_im
        self.icv_factor = icv_factor

        seg = nib.load(self.pfi_segmentation)
        seg_data = seg.get_data()
        self.seg_data = copy.deepcopy(seg_data)
        self.seg_affine = copy.deepcopy(seg.get_affine())
        self.list_labels = np.sort(list(set(seg_data.astype('uint64').flat)))

    def get_total_volume(self):
        """
        :param get_mm3: True, num voxel otherwise
        :return:
        """
        num_voxels = np.count_nonzero(self.seg_data)

        if self.return_mm3:
            mm_3 = num_voxels * np.abs(np.prod(np.diag(self.seg_affine)))
            return mm_3
        else:
            return num_voxels

    def get_volumes_per_zone(self):

        # get regions:
        if self.pfi_description is not None:
            regions = []
            f = open(self.pfi_description, 'r')
            for line in f:
                if not line.startswith('#'):
                    last = line.split('  ')
                    last = last[-1][1:-2]
                    regions.append(last)
        else:
            regions = ['label ' + str(j) for j in self.list_labels]

        # get tot volume
        tot_brain_volume = self.get_total_volume()

        # Get volumes per regions:
        vol = np.zeros(len(self.list_labels), dtype=np.uint64)

        for index_label_k, label_k in enumerate(self.list_labels):
            places = self.seg_data  == label_k
            vol[index_label_k] = np.count_nonzero(places)

        if self.return_mm3:
            vol = vol.astype(np.float64)
            vol = np.abs(np.prod(np.diag(self.seg_affine))) * vol

        np.testing.assert_almost_equal(np.sum(vol[1:]), tot_brain_volume,
                        err_msg='Data not normalised correctly! Debug!')

        # get volumes over total volue:
        vol_over_tot = vol / float(tot_brain_volume)

        # get volume over ICV estimates
        if self.icv_factor is not None:
            vol_over_icv = vol / float(self.icv_factor)
        else:
            vol_over_icv = np.zeros_like(vol)

        headers = ['Regions', 'Vol', 'Vol/totVol', 'Vol/ICV']
        table = [[r, v, v_t, v_icv] for r, v, v_t, v_icv in \
                 zip(regions, vol, vol_over_tot, vol_over_icv)]

        print(tabulate(table, headers=headers))

        return regions, vol, vol_over_tot, vol_over_icv

    def get_average_below_labels(self, selected_labels):
        """
        :param selected_label: list of labels where from extracting the average
            of the values in self.pfi_data
        :return : average for each region, and print to terminal the output.
        """
        if self.pfi_scalar_im is None:
            IOError('Input pfi_data missing')
        if isinstance(selected_labels, int):
            selected_labels = [selected_labels, ]

        im_seg = nib.load(self.pfi_segmentation)
        data_segmentation = im_seg.get_data()

        im_scalar = nib.load(self.pfi_scalar_im)
        data_scalar = im_scalar.get_data()

        assert data_scalar.shape == data_segmentation.shape

        all_places = np.zeros_like(data_segmentation ,dtype=np.bool)
        for sl in selected_labels:
            assert sl in self.list_labels
            all_places += data_segmentation == sl

        masked_scalar_data = all_places.astype(np.float64) * data_scalar.astype(np.float64)
        # remove zero elements from the array:
        non_zero_masked_scalar_data = [i for i in masked_scalar_data.flat if i > 0.00000000001]
        m = np.mean(non_zero_masked_scalar_data)

        print('Mean below the labels {0} : \n{1}'.format(selected_labels, m))

        return m
