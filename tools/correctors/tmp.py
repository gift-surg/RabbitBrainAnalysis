import nibabel as nib
import numpy as np

from LABelsToolkit.tools.aux_methods.utils import print_and_run


def adjust_affine_header(pfi_input, pfi_output, theta, trasl=np.array([0, 0, 0])):

    if theta != 0:
        # transformations parameters
        rot_x = np.array([[1,            0,           0,      trasl[0]],
                         [0,  np.cos(theta),  -np.sin(theta), trasl[1]],
                         [0,  np.sin(theta), np.cos(theta),   trasl[2]],
                         [0,             0,          0,       1]])

        # Load input image:
        im_input = nib.load(pfi_input)

        # generate new affine transformation (from bicommissural to histological)
        new_transf = rot_x.dot(im_input.get_affine())

        # create output image on the input
        if im_input.header['sizeof_hdr'] == 348:
            new_image = nib.Nifti1Image(im_input.get_data(), new_transf, header=im_input.get_header())
        # if nifty2
        elif im_input.header['sizeof_hdr'] == 540:
            new_image = nib.Nifti2Image(im_input.get_data(), new_transf, header=im_input.get_header())
        else:
            raise IOError

        # print intermediate results
        print('Affine input image: \n')
        print(im_input.get_affine())
        print('Affine after transformation: \n')
        print(new_image.get_affine())

        # sanity check
        np.testing.assert_almost_equal(np.linalg.det(new_transf), np.linalg.det(im_input.get_affine()))

        # save output image
        nib.save(new_image, pfi_output)
    else:
        if not pfi_input == pfi_output:
            print_and_run('cp {0} {1}'.format(pfi_input, pfi_output))
