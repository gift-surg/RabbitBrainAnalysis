import os
import numpy as np
import nibabel as nib

from tools.auxiliary.utils import set_new_data


# deprecated after converter!
def corrector_MSME_T2_path(pfi_input, pfi_output, modality=None, swap_dim=None):
    """
    Remapping of the MSME T2 from paravision to a nifty format where
    (x,y,z,e) are the x,y,z, coordinates of the volume and e are the echo coordinates.
    --------
    ex_vivo:
    --------
    The input files presents with 2 consecutive slices with echoes in the same z slice.

    As it is       | as we like it to be
    ----------------------------------
    (x,y,0:15,0)   | (x,y,0,0:15)
    (x,y,16:32,0)  | (x,y,1,0:15)
    (x,y,0:15,1)   | (x,y,2,0:15)
    (x,y,16:32,1)  | (x,y,3,0:15)
    (x,y,0:15,2)   | (x,y,4,0:15)
    (x,y,16:32,2)  | (x,y,5,0:15)
      ...            ...
    (x,y,0:15,t)   | (x,y,2*t,0:15)
    (x,y,16:32,t)  | (x,y,2*t+1,0:15)

    In addition, it will reorient the image in a proper way!

    :param:
    :return:
    """
    im = nib.load(pfi_input)
    im_data = im.get_data()

    # Reslice:
    sh = im_data.shape

    stack_data = np.zeros((sh[0], sh[1], sh[2] * sh[3]), dtype=np.float64)
    new_data = np.zeros_like(im_data)

    for t in xrange(sh[3]):
        m = sh[2] * t
        M = sh[2] * t + sh[2]
        stack_data[:, :, m:M] = im_data[..., t]

    for z in xrange(sh[2]):
        m = sh[3] * z
        M = sh[3] * z + sh[3]
        new_data[:, :, z, :] = stack_data[:, :, m:M]

    im_new = set_new_data(im, new_data)
    nib.save(im_new, pfi_output)

    if modality == 'ex_vivo':
        swap_dim = 'x z -y'

    elif modality == 'in_vivo':
        swap_dim = 'x z -y'

    # swap dimension according to swap_dim or modality.
    if swap_dim is not None:

        print('Reorienting directions according to {} .'.format(swap_dim))

        cmd = 'fslorient -deleteorient {0}; ' \
              'fslswapdim {0} {1} {0}; ' \
              'fslorient -setqformcode 1 {0}; '.format(pfi_output, swap_dim)
        os.system(cmd)
