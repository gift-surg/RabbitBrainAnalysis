import time
import numpy as np
import nibabel as nib
import os

from tools.auxiliary.utils import print_and_run


def adjust_header_from_transformations(pfi_input, pfi_output, theta, trasl):
    # todo: simplify and test using pointers.
    # transformations parameters
    rot_x = np.array([[1,            0,           0,     trasl[0]],
                     [0,  np.cos(theta),  -np.sin(theta),     trasl[1]],
                     [0,  np.sin(theta), np.cos(theta),   trasl[2]],
                     [0,             0,          0,      1]])

    # Load input image:
    im_input = nib.load(pfi_input)

    # generate new affine transformation (from bicommissural to histological)
    new_transf = rot_x.dot(im_input.affine)

    # create output image on the input
    if im_input.header['sizeof_hdr'] == 348:
        new_image = nib.Nifti1Image(im_input.get_data(), new_transf, header=im_input.get_header())
    # if nifty2
    elif im_input.header['sizeof_hdr'] == 540:
        new_image = nib.Nifti2Image(im_input.get_data(), new_transf, header=im_input.get_header())
    else:
        raise IOError

    # print intermediate results
    print 'Affine input image: \n'
    print im_input.affine
    print 'Affine after transformation: \n'
    print new_image.affine

    # sanity check
    np.testing.assert_almost_equal(np.linalg.det(new_transf), np.linalg.det(im_input.affine))

    # save output image
    nib.save(new_image, pfi_output)


def set_translational_part_to_zero(pfi_input, pfi_output):
    # todo: simplify and test using pointers.
    # Load input image:
    im_input = nib.load(pfi_input)

    # generate new affine transformation (from bicommissural to histological)
    new_transf = np.copy(im_input.affine)
    new_transf[:, 3] = np.array([0, 0, 0, 1])

    # create output image on the input
    if im_input.header['sizeof_hdr'] == 348:
        new_image = nib.Nifti1Image(im_input.get_data(), new_transf, header=im_input.header)
        # time.sleep(5)  # very bad solution... Don't know how to make nibabel finishing to save an image on a file.
    # if nifty2
    elif im_input.header['sizeof_hdr'] == 540:
        new_image = nib.Nifti2Image(im_input.get_data(), new_transf, header=im_input.header)
        # time.sleep(5)  # very bad solution... Don't know how to make nibabel finishing to save an image on a file.
    else:
        raise IOError

    # print intermediate results
    print 'Affine input image: \n'
    print im_input.affine
    print 'Affine after transformation: \n'
    print new_image.affine

    # save output image
    nib.save(new_image, pfi_output)


def orient2std(pfi_in, pfi_out):
    """
    As different modalities are not oriented in the same space when converted and
    as fslorient2std affects only the s-form and not the q-form.
    1) apply fslorient2std
    2) set translational part to zero
    3) use nibabel to set the s-form as the q-form
    :param pfi_in:
    :param pfi_out:
    :return:
    """
    assert os.path.exists(pfi_in)
    pfi_intermediate = os.path.join(os.path.dirname(pfi_in), 'zz_tmp_' + os.path.basename(pfi_in))
    # 1 --
    cmd0 = 'fslreorient2std {0} {1}'.format(pfi_in, pfi_intermediate)
    print_and_run(cmd0)
    # 2 --
    set_translational_part_to_zero(pfi_intermediate, pfi_intermediate)
    # 3 --
    im = nib.load(pfi_intermediate)
    im.set_sform(im.get_qform())
    nib.save(im, pfi_out)
    os.system('rm {}'.format(pfi_intermediate))


def header_orientation_bicomm2histo(pfi_input, pfi_output):
    adjust_header_from_transformations(pfi_input, pfi_output, theta=-np.pi / float(5), trasl=(0, -15, -7))


def header_orientation_histo2bicomm(pfi_input, pfi_output):
    adjust_header_from_transformations(pfi_input, pfi_output, theta=np.pi / float(5), trasl=(0, 15, 7))


def reorient_bicomm2dwi(pfi_in, pfi_out):
    # from bicommissural to dwi
    _cmd = ''' cp {0} {1};
        fslorient -deleteorient {1};
        fslswapdim {1} z y -x {1};
        fslorient -setqformcode 1 {1};'''.format(pfi_in, pfi_out)

    print _cmd


def reorient_dwi2bicomm(pfi_in, pfi_out):
    # from dwi to bicommissural
    _cmd = ''' cp {0} {1};
        fslorient -deleteorient {1};
        fslswapdim {1} -z -y -x {1};
        fslorient -setqformcode 1 {1};'''.format(pfi_in, pfi_out)

    print _cmd
