import os
import numpy as np
from os.path import join as jph
import pandas as pd
import pickle
from bokeh.plotting import figure, show, output_file

from tools.definitions import root_study_rabbits, pfo_local_output, pfo_subjects_parameters


def from_g_ratio_data_to_data_frame(list_subjects_names, list_regions_names, list_modality_names, g_ratio_array):
    """
    # what we want to get is something like:
    df = pd.DataFrame({'subject1': {('region1', 'dataset1'): 111,
                                    ('region1', 'dataset2'): 112,
                                    ('region1', 'dataset3'): 113,
                                    ('region1', 'dataset4'): 114,
                                    ('region1', 'dataset5'): 115,
                                    ('region2', 'dataset1'): 121,
                                    ('region2', 'dataset2'): 122},
                                    ...
                       'subject2': {('region1', 'dataset1'): 211,
                                    ('region1', 'dataset2'): 212,
                                    ('region1', 'dataset3'): 213,
                                    ('region1', 'dataset4'): 214,
                                    ('region1', 'dataset5'): 215,
                                    ('region2', 'dataset1'): 221,
                                    ('region2', 'dataset2'): 222,
                                    ...},} )

    """

    d = {}
    for subject_i, sub in enumerate(list_subjects_names):
        r_dic = {}
        for region_j, reg in enumerate(list_regions_names):
            for mod_k, mod in enumerate(list_modality_names):
                r_dic.update({(reg, mod): g_ratio_array[subject_i, region_j, mod_k]})
        d.update({sub: r_dic})
    dfg = pd.DataFrame(d)

    return dfg


def generate_dummy_data_frame(num_subjects=10, regions=None, modalities=None):

    subj = ['sj ' + str(k + 1) for k in range(num_subjects)]
    if regions is None:
        regions = ['region ' + str(k + 1) for k in range(8)]
    if modalities is None:
        modalities = ['modality ' + str(k + 1) for k in range(5)]

    g_ratio_dat = np.random.uniform(0.5, 0.99, [len(subj), len(regions), len(modalities)])  # regions x subjects

    return from_g_ratio_data_to_data_frame(subj, regions, modalities, g_ratio_dat)


def get_g_ratio_per_subjects_as_data_frame(input_subjects_list):
    """
    Each subject has to be provided with a record in the appropriate folder
    From the records of a range of subjects it extracts the data frame with the g-ratio, for the required modalities.

    NOTE: for the g-ratio, the data should be collected individually and not from the record, as
    there is an experimentation phase in progress...

    A record is a data structure as:

    record = {'Info'      : subject_info,
              'Regions'   : regions,
              'LabelsID'  : values_list,
              'NumVoxels' : voxels,
              'vols'      : vols,
              'FAs'       : FAs,
              'ADCs'      : ADCs,
              'g_ratios'  : g_ratios}

    :param input_subjects_list:
    :return: regions_over_g_ratio, a matrix num_regions x subjects having
        regions_over_g_ratio[reg_i, subj_j] = g_ratio per region reg_i of the subject subj_j
    """
    # -- fetch the path to record for each subject in a list:
    records = []

    for sj in input_subjects_list:

        sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

        study = sj_parameters['study']
        category = sj_parameters['category']

        pfi_record_sj = jph(root_study_rabbits, 'A_data', study, category, sj, 'records', sj + '_records.npy')
        assert os.path.exists(pfi_record_sj), 'Subject {} has no record available'.format(sj)
        records.append(np.load(pfi_record_sj).item())

    # --  check all the subjects have the regions label provided in the same order:
    regions_sj0 = records[0]['Regions']
    for rec in records[1:]:
        regions_sj = rec['Regions']
        assert regions_sj == regions_sj0

    # --  get the matrix:
    regions_over_g_ratio = np.zeros([len(regions_sj0), len(input_subjects_list)], dtype=np.float64)

    # TODO

    # --  create the table and the header:

    return regions_over_g_ratio, regions_sj0, input_subjects_list


def plot_histogram(df_g_ratio, regions=None, modalities=None):
    print regions
    print modalities
    pass


def plot_fancy_histogram(df_g_ratio, regions=None, modalities=None):

    # to plot dummy data:
    if regions is None:
        regions = ['region ' + str(k + 1) for k in range(8)]
    if modalities is None:
        modalities = ['modality ' + str(k + 1) for k in range(5)]

    # Dimensions
    width = 1200
    height = 1200
    font_size = "16pt"
    inner_radius = 136  # corresponds to 0.4
    outer_radius = 340  # corresponds to 1.0
    x_center, y_center = 0, 0

    # data:
    number_regions = len(regions)
    number_modalities = len(modalities)

    means = df_g_ratios.mean(axis=1)
    stdev = df_g_ratios.std(axis=1)

    # Colors
    sectors_color = '#BEBEBE'
    colors_modalities = ["#3DE06A", "#8AE0A5", "#4771E0", "#8B9BE0", "#E06072"]

    # FIGURE specs

    p = figure(plot_width=width, plot_height=height,
               x_axis_type=None, y_axis_type=None,
               x_range=(-420, 420), y_range=(-420, 420),
               min_border=0, outline_line_color="black",
               background_fill_color="#E9E7EC", border_fill_color="white",
               toolbar_sticky=False)

    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    alpha = 2.0 * np.pi / float(number_regions + 1)  # big angle
    beta = alpha / float(2*number_modalities + 1)  # small angle

    ending_angle_a = 0
    # Regions
    for a in range(number_regions):
        starting_angle_a = np.pi/2 - alpha/2 - a * alpha
        ending_angle_a = starting_angle_a - alpha
        color_a = sectors_color

        p.annular_wedge(x_center, y_center, inner_radius, outer_radius,
                        starting_angle_a, ending_angle_a, color=color_a, direction="clock")

        # Radial axis
        p.annular_wedge(0, 0, inner_radius, outer_radius,
                        starting_angle_a, starting_angle_a, color="black")

        # modalities and standard deviation
        for b in range(number_modalities):
            starting_angle_b = starting_angle_a - (2*b + 1) * beta
            ending_angle_b = starting_angle_b - beta
            mean_angle = (starting_angle_b + ending_angle_b) / 2
            color_b = colors_modalities[b]
            mu = outer_radius * means[regions[a]][modalities[b]]
            std  = outer_radius * stdev[regions[a]][modalities[b]]
            # wedge mean
            p.annular_wedge(x_center, y_center, inner_radius, mu,
                            starting_angle_b, ending_angle_b, color=color_b,  direction="clock")
            # wdge standard deviation: main bar
            p.annular_wedge(x_center, y_center, mu-std, mu+std, mean_angle, mean_angle, color="#838683",
                            direction="clock")
            # wdge standard deviation: sides
            p.annular_wedge(x_center, y_center, mu - std, mu - std, mean_angle + beta/4, mean_angle - beta/4,
                            color="#838683", direction="clock")
            p.annular_wedge(x_center, y_center, mu + std, mu + std, mean_angle + beta/4, mean_angle - beta/4,
                            color="#838683", direction="clock")
    # Radial axis, final one
    p.annular_wedge(0, 0, inner_radius, outer_radius, ending_angle_a, ending_angle_a, color="black")

    # Circle with the scale values:
    g_ratio_values = np.linspace(0.4, 1.1, 8)[:-1]
    radii = 340 * g_ratio_values
    p.circle(0, 0, radius=radii, fill_color=None, line_color="white")
    p.text(0, radii, [str(r) for r in g_ratio_values],
           text_font_size=font_size, text_align="center", text_baseline="middle")

    # text regions
    for a in range(number_regions):
        radius = 380
        half_angle_a = np.pi / 2 - alpha - a * alpha
        xr = radius * np.cos(half_angle_a)
        yr = radius * np.sin(half_angle_a)
        label_angle = half_angle_a

        if label_angle < -np.pi / 2:
            label_angle += np.pi

        p.text(xr, yr, pd.Series([regions[a]]), angle=label_angle,
               text_font_size=font_size, text_align="center", text_baseline="middle")

    # Legends below for the WM, gray matter regions classifications
    # p.circle([-40, -40], [-370, -390], color=[wm_color, gm_color], radius=5)

    # Central legends for each region
    p.rect([-50, -50, -50, -50, -50], [40, 20, 0, -20, -40], width=30, height=13, color=colors_modalities)
    p.text([-15, -15, -15, -15, -15], [40, 20, 0, -20, -40], text=modalities, text_font_size=font_size, text_align="left",
           text_baseline="middle")

    output_file(os.path.join(pfo_local_output, 'RegionsModalities.html'), title='regions_modalities')

    show(p)


def save_latex_tables(input_df, selected_regions=None, file_name='regions_data.tex'):
    # copy for safety reasons:
    df = input_df.copy(deep=True)
    if selected_regions is not None:
        df = df.loc[list(selected_regions), :]

    series_mean = df.mean(axis=1)
    series_stdev = df.std(axis=1)
    df_mean_stdev = pd.DataFrame({'mean': series_mean, 'std': series_stdev})
    df_mean_stdev = df_mean_stdev.T
    dat = df_mean_stdev.to_latex()
    f = open(jph(pfo_local_output, file_name), 'w+')
    f.write(dat)
    f.close()

# ---

if __name__ == '__main__':
    # ---- some initial examples: as taking information from 5 different resources:

    regions = ('Retrosplenium', 'Hippocampi', 'Putamen', 'Septum', 'Midbrain', 'Pons', 'Anterior commissure', 'Corpus callosum', 'Something')
    modalities = ('histo', 'histo+', 'dwi', 'dwi+', 'humans')

    df_g_ratios = generate_dummy_data_frame(num_subjects=4, modalities=modalities, regions=regions)

    # plot_histogram(df_g_ratios, regions=regions, modalities=modalities)
    plot_fancy_histogram(df_g_ratios, regions=regions, modalities=modalities)
    # save_latex_tables(df_g_ratios, selected_regions=('Retrosplenium'), file_name='regions_data_1.tex')
    # save_latex_tables(df_g_ratios, selected_regions=('Corpus callosum'),  file_name='regions_data_2.tex')
    # save_latex_tables(df_g_ratios, selected_regions=('Midbrain',), file_name='regions_data_3.tex')
    # save_latex_tables(df_g_ratios, selected_regions=('Something',), file_name='regions_data_4.tex')