import numpy as np


def reorient_b_vect(pfi_input, pfi_output, transform, fmt='%.14f'):
    """

    :param pfi_input:
    :param pfi_output:
    :param transform:
    :param fmt:
    :return:
    """
    transformed_vect = np.einsum('...kl,...l->...k', np.loadtxt(pfi_input), transform)
    np.savetxt(pfi_output, transformed_vect, fmt=fmt)


def rosetta_s3xz2_translator(in_transformation, out_language='fsl'):
    """
    Translates the various convention for the group S3 x Z2^3 (48 elements group of axial rotation and symmetry).
    matrix representation - > 3x3 premutation matrix with +/- signs for each of its element.
    Fsl convention -> e.g. '-x z y' : invert x sign and permute z with y axis
    Nifti convention -> RAS : right anterior superior. R-L, A-P, S-I
    :return:
    """
    # check input:
    if out_language not in ['fsl', 'nifti', 'matrix']:
        raise IOError("Input attribute out_language must be 'fsl', 'nifti' or 'matrix'. Default 'fsl'.")

    in_transformation_language = None

    # check is matrix

    # check is fsl

    # check is nifti

    if in_transformation_language == out_language:
        print("Warning, in_transformation, out_language")

    if in_transformation_language is None:
        raise IOError("Input in_transformation not match any of the known convention 'fsl', 'nifti' or 'matrix'.")


# transform_field_by_affine
def matrix_vector_field_product(j_input, v_input):
    """
    :param j_input: matrix m x n x (4 or 9) as for example a jacobian column major
    :param v_input: matrix m x n x (2 or 3) to be multiplied by the matrix point-wise.
    :return: m x n  x (2 or 3) whose each element is the result of the product of the
     matrix (i,j,:) multiplied by the corresponding element in the vector v (i,j,:).

    In tensor notation for n = 1: R_{i,j,k} = \sum_{l=0}^{2} M_{i,j,l+3k} v_{i,j,l}

    ### equivalent code in a more readable version:

    # dimensions of the problem:
    d = v_input.shape[-1]
    vol = list(v_input.shape[:-1])

    # repeat v input 3 times, one for each row of the input matrix 3x3 or 2x2 in corresponding position:
    v = np.tile(v_input, [1]*d + [d])

    # element-wise product:
    j_times_v = np.multiply(j_input, v)

    # Sum the three blocks in the third dimension:
    return np.sum(j_times_v.reshape(vol + [d, d]), axis=d+1).reshape(vol + [d])

    """
    assert len(j_input.shape) == len(v_input.shape)

    d = v_input.shape[-1]
    vol = list(v_input.shape[:d])
    extra_ones = len(v_input.shape) - (len(vol) + 1)

    temp = j_input.reshape(vol + [1] * extra_ones + [d, d])  # transform in squared block with additional ones
    return np.einsum('...kl,...l->...k', temp, v_input)
