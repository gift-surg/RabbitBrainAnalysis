"""
Bicommissural orientation
All based on ITK-snap screenshot and Keynote adjustment.
https://stackoverflow.com/questions/26935701/ploting-filled-polygons-in-python
https://stackoverflow.com/questions/31464345/fitting-a-closed-curve-to-a-set-of-points

https://matplotlib.org/1.3.1/examples/pylab_examples/line_styles.html

\begin{tabular}{ | c | c | c | c | c | c | c | }
    \hline
    ID Number & Days of  &  Sex    &   Full       &  Brain       & Date       & Date      \\
    & Gestation (d) &    &  Weight (g)  &  Weight (g)  & Harvest    & MRI       \\
    \hline
    1201      & 28.5   &  Male      &  47.5        & 1.70         & 19/08/16   & 22/08/16  \\
    1203      & 28.5   &  Male      &  54.4        & 1.80         & 19/08/16   & 24/08/16  \\
    1305      & 28.5   &  Female    &  36.8        & 1.68         & 19/08/16   & 01/09/16  \\
    1404      & 28.5   &  Female    &  36.7        & 1.38         & 19/08/16   & 26/08/16  \\
    \st{1505} & 28.5   &  Male      &  41.5        & 1.34         & 13/09/16   & 14/09/16  \\
    1507      & 28.5   &  Male      &  31.9        & 1.17         & 13/09/16   & 13/09/16  \\
    1510      & 28.5   &  Male      &  33.4        & 1.34         & 13/09/16   & 16/09/16  \\
    1702      & 31     &  Male      &  47.7        & 1.81         & 23/09/16   & 27/09/16  \\
    1805      & 31     &  Female    &  51.3        & 1.78         & 23/09/16   & 30/09/16  \\

    2002      & 28.5   &  Male      &  31.8        & 1.23         & 31/10/16   & 02/11/16  \\
    2502      & 31     &  Female    &  62.9        & 1.65         & 06/03/17   & 06/03/17  \\

    \st{2503} & 31     &  Female    &  66.8        & 1.79         & 07/03/17   & 07/03/17  \\
    \st{2608} & 31     &  Female    &  54.1        & 1.79         & 08/03/17   & 09/03/17  \\
    \st{2702} & 31     &  Male      &  54.6        & 1.64         & 09/03/17   & 09/03/17  \\

    3301 & U     &  U      &  54.6        & 1.64         & 09/03/17   & 09/03/17  \\
    \st{3303} & U    &  U      &  54.6        & 1.64         & 09/03/17   & 09/03/17  \\
    3404 & U    &  U      &  54.6        & 1.64         & 09/03/17   & 09/03/17  \\
    \hline
\end{tabular}

dictionary {id : [term, sex, (full weight, brain weight), in/out]}

"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


from collections import OrderedDict

data_set = OrderedDict(
           {1201: ['Preterm', 'Male',   (47.5, 1.70), 'in'],
            1203: ['Preterm', 'Male',   (54.4, 1.80), 'in'],
            1305: ['Preterm', 'Female', (36.8, 1.68), 'in'],
            1404: ['Preterm', 'Female', (36.7, 1.38), 'in'],
            1505: ['Preterm', 'Male',   (41.5, 1.34), 'out'],
            1507: ['Preterm', 'Male',   (31.9, 1.17), 'in'],
            1510: ['Preterm', 'Male',   (33.4, 1.34), 'in'],
            1702: ['Term',    'Male',   (47.7, 1.81), 'in'],
            1805: ['Term',    'Female', (51.3, 1.78), 'in'],
            2002: ['Preterm', 'Male',   (31.8, 1.23), 'in'],
            2502: ['Term',    'Female', (62.9, 1.65), 'in'],
            2503: ['Term',    'Female', (66.8, 1.79), 'out'],
            2608: ['Term',    'Female', (54.1, 1.79), 'out'],
            3301: ['Preterm', 'Female', (47.4, 1.59),      'in'],     # M/F DATA NOT GIVEN!
            3303: ['Preterm', 'Male',   (50.3, 1.78),   'out'],    # M/F DATA NOT GIVEN!
            3404: ['Term',    'Female', (34.3, 1.6),    'in'],     # M/F DATA NOT GIVEN!
            })


if __name__ == '__main__':

    add_id = True

    body_we  = [data_set[k][2][0] for k in data_set.keys()]
    brain_we = [data_set[k][2][1] for k in data_set.keys()]

    mu_body  = np.mean(body_we)
    mu_brain = np.mean(brain_we)

    perc_body  = [np.percentile(body_we, 25), np.percentile(body_we, 75)]
    perc_brain = [np.percentile(brain_we, 25), np.percentile(brain_we, 75)]

    std_body = np.std(body_we)
    std_brain = np.std(brain_we)

    # FIGURE:
    fig, ax = plt.subplots(figsize=(7, 6))

    # --------- horizontal vertical lines
    ax.axhline(y=mu_brain, color='grey', linestyle='--')
    ax.axvline(x=mu_body, color='grey', linestyle='--')

    # -------- patch squared
    rect = Rectangle((mu_body - std_body, mu_brain - std_brain), 2 * std_body, 2 * std_brain,
                     alpha=0.1, facecolor='grey',
                     # linewidth=1, edgecolor='grey', facecolor='none', linestyle='--'
                     )
    ax.add_patch(rect)

    # -----------  term m:
    data_term_m_id = [k for k in data_set.keys() if (data_set[k][0] == 'Term' and data_set[k][1] == 'Male')]
    data_term_m_x = [data_set[k][2][0] for k in data_term_m_id]
    data_term_m_y = [data_set[k][2][1] for k in data_term_m_id]
    term_m    = ax.plot(data_term_m_x, data_term_m_y,
                        color='royalblue', marker='o', fillstyle='full', label='Term Male', ls='None')

    if add_id:
        for ide, x, y in zip(data_term_m_id, data_term_m_x, data_term_m_y):
            plt.annotate(ide, xy=(x, y), xytext=(13, -14), # 30, -6
                textcoords='offset points', ha='right', va='bottom',
                # bbox=dict(fc='royalblue', alpha=0.5),
                # arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', fc='royalblue', alpha=0.5)
                         )

    # -----------  term f:
    data_term_f_id = [k for k in data_set.keys() if (data_set[k][0] == 'Term' and data_set[k][1] == 'Female')]
    data_term_f_x  = [data_set[k][2][0] for k in data_term_f_id]
    data_term_f_y  = [data_set[k][2][1] for k in data_term_f_id]
    term_f    = ax.plot(data_term_f_x, data_term_f_y,
                        color='royalblue', marker='o', fillstyle='none', label='Term Female', ls='None')
    if add_id:
        for ide, x, y in zip(data_term_f_id, data_term_f_x, data_term_f_y):
            plt.annotate(ide, xy=(x, y), xytext=(13, -14), # 30, -6
                textcoords='offset points', ha='right', va='bottom',
                # bbox=dict(fc='royalblue', alpha=0.5),
                # arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', fc='royalblue', alpha=0.5)
                         )

    # -----------  preterm m:
    data_preterm_m_id = [k for k in data_set.keys() if (data_set[k][0] == 'Preterm' and data_set[k][1] == 'Male')]
    data_preterm_m_x = [data_set[k][2][0] for k in data_preterm_m_id]
    data_preterm_m_y = [data_set[k][2][1] for k in data_preterm_m_id]
    pterm_m   = ax.plot(data_preterm_m_x, data_preterm_m_y,
                           color='darkred', marker='s', fillstyle='full', label='Preterm Male', ls='None')
    if add_id:
        for ide, x, y in zip(data_preterm_m_id, data_preterm_m_x, data_preterm_m_y):
            plt.annotate(ide, xy=(x, y), xytext=(13, 3),  # 30, -6,
                textcoords='offset points', ha='right', va='bottom',
                # bbox=dict(fc='royalblue', alpha=0.5),
                # arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', fc='royalblue', alpha=0.5)
                         )
    # -----------  preterm f:
    data_preterm_f_id = [k for k in data_set.keys() if (data_set[k][0] == 'Preterm' and data_set[k][1] == 'Female')]
    data_preterm_f_x = [data_set[k][2][0] for k in data_preterm_f_id]
    data_preterm_f_y = [data_set[k][2][1] for k in data_preterm_f_id]
    pterm_f   = ax.plot(data_preterm_f_x, data_preterm_f_y,
                           color='darkred', marker='s', fillstyle='none', label='Preterm Female', ls='None')
    if add_id:
        for ide, x, y in zip(data_preterm_f_id, data_preterm_f_x, data_preterm_f_y):
            plt.annotate(ide, xy=(x, y), xytext=(13, 3),  # 30, -6,
                textcoords='offset points', ha='right', va='bottom',
                # bbox=dict(fc='royalblue', alpha=0.5),
                # arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', fc='royalblue', alpha=0.5)
                         )
    # -----------  discarded:
    discarded = ax.plot([data_set[k][2][0] for k in data_set.keys() if data_set[k][3] == 'out'],
                           [data_set[k][2][1] for k in data_set.keys() if data_set[k][3] == 'out'],
                           color='red', marker='x', fillstyle='none', label='Discarded', ms=13, ls='None')

    ax.grid(True)
    ax.legend(loc='lower right')
    if add_id:
        ax.set_title('Dataset: id number, sex, gestational age, body versus brain weight')
    else:
        ax.set_title('Dataset: sex, gestational age, body versus brain weight')
    ax.set_xlabel('Body weight (g)')
    ax.set_ylabel('Brain weight (g)')

    ax.set_xlim([25, 75])
    ax.set_ylim([1.0, 1.9])

    pfo_resulting_images_folder = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/docs/Atlas_Paper/images/f2_dataset_presentation'
    if add_id:
        plt.savefig(os.path.join(pfo_resulting_images_folder, 'f2_dataset_presetation_id.pdf'), dpi=150)
    else:
        plt.savefig(os.path.join(pfo_resulting_images_folder, 'f2_dataset_presetation.pdf'), dpi=150)


    plt.show()

