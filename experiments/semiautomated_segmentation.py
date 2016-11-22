from tools.auxiliary.connected_components import filter_connected_components_by_volume_path
from tools.auxiliary.lesion_mask_extractor import lesion_masks_extractor_cc_based_path

sj = '1507'
image_path = '/Users/sebastiano/Documents/UCL/a_data/bunnies/pipelines/ex_vivo_template/zz_experiments/' + sj + '_3D.nii.gz'
ciccione_path = '/Users/sebastiano/Documents/UCL/a_data/bunnies/pipelines/ex_vivo_template/zz_experiments/ciccione_' + sj + '_3D.nii.gz'
res_path = '/Users/sebastiano/Documents/UCL/a_data/bunnies/pipelines/ex_vivo_template/zz_experiments/' + sj + 'auto_res.nii.gz'

lesion_masks_extractor_cc_based_path(image_path, res_path, ciccione_path, safety_on=False)

