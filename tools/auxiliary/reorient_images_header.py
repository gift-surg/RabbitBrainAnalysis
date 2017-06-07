import time
import numpy as np
import nibabel as nib


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
    print 'Affine input image: \n'
    print im_input.get_affine()
    print 'Affine after transformation: \n'
    print new_image.get_affine()

    # sanity check
    np.testing.assert_almost_equal(np.linalg.det(new_transf), np.linalg.det(im_input.get_affine()))

    # save output image
    nib.save(new_image, pfi_output)


def set_translational_part_to_zero(pfi_input, pfi_output):
    # todo: simplify and test using pointers.
    # Load input image:
    im_input = nib.load(pfi_input)

    # generate new affine transformation (from bicommissural to histological)
    new_transf = np.copy(im_input.get_affine())
    new_transf[:, 3] = np.array([0, 0, 0, 1])

    # create output image on the input
    if im_input.header['sizeof_hdr'] == 348:
        new_image = nib.Nifti1Image(im_input.get_data(), new_transf, header=im_input.get_header())
        # time.sleep(5)  # very bad solution... Don't know how to make nibabel finishing to save an image on a file.
    # if nifty2
    elif im_input.header['sizeof_hdr'] == 540:
        new_image = nib.Nifti2Image(im_input.get_data(), new_transf, header=im_input.get_header())
        # time.sleep(5)  # very bad solution... Don't know how to make nibabel finishing to save an image on a file.
    else:
        raise IOError

    # print intermediate results
    print 'Affine input image: \n'
    print im_input.get_affine()
    print 'Affine after transformation: \n'
    print new_image.get_affine()

    # save output image
    nib.save(new_image, pfi_output)


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
