"""
Plots the appendix figure for sample-specific availability.
"""

import matplotlib
import matplotlib.pyplot as plt


if __name__ == '__main__':
    # Set larger font size for plots
    matplotlib.rc('xtick', labelsize=18)
    matplotlib.rc('ytick', labelsize=18)
    matplotlib.rcParams.update({'font.size': 18})
    # set LaTeX font
    matplotlib.rcParams['mathtext.fontset'] = 'stix'
    matplotlib.rcParams['font.family'] = 'STIXGeneral'
    plt.rcParams['text.usetex'] = True

    # We have samples in 1 - 24 languages
    x = [i for i in range(1, 25)]

    # These are the scores from our rebuttal_additional_stats.py script
    # Additionally, the validation/test set have 375 samples in 24 languages.
    avs = [40, 6, 5, 94, 30, 0, 1, 1, 9, 1, 12, 4, 2, 11, 18, 1, 2, 6, 5, 15, 25, 141, 760, 375]

    y = [sum(avs) - sum(avs[:i]) for i in range(len(avs))]

    fig, ax = plt.subplots()
    ax.plot(x, y, color="#1b9e77")

    ax.set_xticks([1, 4, 8, 12, 16, 20, 24])
    ax.set_xlim(1, 24)
    ax.set_ylim(0, 1600)

    ax.set_xlabel("Availability in at least $k$ languages")
    ax.set_ylabel("Number of samples")

    plt.savefig("./Insights/sample_lang_dist.png", dpi=300, bbox_inches='tight')
    plt.show()