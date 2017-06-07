import os
import numpy as np
import nibabel as nib

from tools.auxiliary.utils import set_new_data, print_and_run


def squeeze_image_from_path(pfi_in, pfi_out, copy_anyway=False):
    """
    copy the image in a new one with the dimension of the data squeezed.
    :param path_input_image: 
    :param path_output_image:
    :param copy_anyway: if the image does not need to be squeezed, it is anyway copied in the
    path_output_image. Option that can be useful in some pipeline
    """
    im = nib.load(pfi_in)
    print('Input image dimensions: {0}.'.format(str(im.shape)))

    if 1 in list(im.shape):
        new_im = set_new_data(im, np.squeeze(im.get_data()[:]))
        nib.save(new_im, pfi_out)
        print('New image dimensions: {0}, saved in {1}'.format(str(new_im.shape), str(pfi_out)))
    else:
        print('No need to squeeze the input image.')
        if copy_anyway:
            cmd = 'cp {0} {1} '.format(pfi_in, pfi_out)
            print_and_run(cmd)
            return 'Already squeezed image copied in {0} '.format(pfi_out)


def sform_qform_cleaner(pfi_in, pfi_out):
    """
    import nibabel as nib
    import numpy as np
    im = nib.load('1201_MSME.nii.gz')
    qf = im.get_qform()
    qf
    qf[:, 3]
    qf[:, 3] =np.array([0,0,0,1])
    qf
    qf_new = np.diag(np.diag(qf))
    qf_new
    ?im.set_qform
    im.set_qform(qf_new)
    im.set_sform(qf_new)
    nib.save(im, '1201_MSME_new.nii.gz')
    """

    im = nib.load(pfi_in)
    if 0.0 in np.diag(im.get_qform()):
        print('WARNING: cannot clean q-form and s-form. Apply fslreorient2std first.')
        return

    qf_new = np.diag(np.diag(im.get_qform()))
    im.set_qform(qf_new)
    im.set_sform(qf_new)
    nib.save(im, pfi_out)
    print('New image with clean q-form: saved in {}'.format(pfi_out))
