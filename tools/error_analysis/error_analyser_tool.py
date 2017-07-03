"""
Notes on how to get SVFs from NiftyReg.

SVF are obtained from NiftyReg as follows reg_f3d with command -vel, returning the corresponding cpp grid as the
control point grid we are interested in.
The dense vector field that corresponds to the given gpp grid is then provided with -flow and it
is obtained in 'deformation coordinates' (Eulerian coordinate system).
To have it in displacement coordinate system (Lagrangian coordinate system) for our elaboration we need to
subtract them the identity with python (not with - disp in niftyReg, otherwise it will be exponentiated again).

Do it in Vector Field Manager!
"""


def get_dice_score(pfi_binary_automatic, pfi_binary_manual, pfo_intermediate_files):
    pass


def get_dispersion(pfi_binary_automatic, pfi_binary_manual, pfo_intermediate_files):
    pass


def get_preicision(pfi_binary_automatic, pfi_binary_manual, pfo_intermediate_files):
    pass


def get_errors_table(pfi_automatic_segm, pfi_manual_segm, pfo_intermediate_files, pfi_output_table=None,
                     pfi_label_descriptor=None, erase_intermediate=False):
    pass
