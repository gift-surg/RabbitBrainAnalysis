import numpy as np

from tools.label_management.patches import get_patch_values, get_shell_for_given_radius


def weighting_for_LNCC(point, target_image, stack_warped, morphological_mask):
    """
    We want to assess the lncc between a target and each of the image stack of images
    contained into a stack, on a patch shape.
    :param point: point in an image
    :param target_image: an image
    :param stack_warped: a stack of warped images
    :param morphological_patch: patch-like object
    :return:
    """
    num_timepoints = stack_warped.shape[3]

    patch_target = get_patch_values(point, target_image, morfo_mask=morphological_mask)
    versor_target = np.array(patch_target) / float(np.linalg.norm(np.array(patch_target)))

    ordered_measurements = []

    for t in range(num_timepoints):
        patch_t = get_patch_values(point, stack_warped[..., t], morfo_mask=morphological_mask)
        versor_t = np.array(patch_t) / float(np.linalg.norm(np.array(patch_t)))

        ordered_measurements.append(versor_target.dot(versor_t))

    return np.array(ordered_measurements)


def triangular_density_function(x, a, mu, b):

    if a <= x < mu:
        return 2 * (x - a) / float((b - a) * (mu - a))
    elif x == mu:
        return 2 / float(b - a)
    elif mu < x <= b:
        return 2 * (b - x) / float((b - a) * (b - mu))
    else:
        return 0


def weighting_for_whole_label_background(grayscale_value, covering_labels, intensities_distrib_matrix):
    """

    :param grayscale_value:
    :param covering_labels:
    :param intensities_distrib_matrix: output of selector.get_intensities_statistics_matrix()
    :return:
    """
    assert covering_labels == intensities_distrib_matrix.shape[2]
    ans = []
    for id_l, l in enumerate(covering_labels):
        quart_low, mu, quart_up = list(intensities_distrib_matrix[:, l, id_l])  # all stats, label l, slice of the stack id_l
        # value of the triangular distribution normalised for the mean of the distribution itself
        val_normalised = triangular_density_function(grayscale_value, quart_low, mu, quart_up) / float(mu)
        ans.append(val_normalised)
    return np.array(ans)


def weighting_for_distance_from_certain_label(point, stack_weights, stack_segmentations):
    """

    :param point:
    :param stack_weights:
    :param stack_segmentations:
    :return:
    """
    x, y, z = point
    list_candidates = list(stack_segmentations[x, y, z, :])
    # the closest to a stack weight with a 1.0 in the stack_weights, with the same value of the list candidates
    r = 1
    island_reached = False
    label_island = -1
    c = [0, 0, 0]
    while r < 1000 or island_reached:
        coord = get_shell_for_given_radius(r)
        for c in coord:
            if 1.0 in stack_weights[x + c[0], y + c[1], z + c[2], :]:
                index_label_island = stack_weights[x + c[0], y + c[1], z + c[2], :].index(1.0)
                label_island = stack_segmentations[x + c[0], y + c[1], z + c[2], index_label_island]
                if label_island in list_candidates:
                    island_reached = True
        r += 1

    pos_label_at_point = stack_segmentations[x + c[0], y + c[1], z + c[2], :].index(label_island)

    ans = [0.0] * len(list_candidates)
    ans[pos_label_at_point] = 1.0

    return np.array(ans)
