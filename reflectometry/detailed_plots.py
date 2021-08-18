if __name__ == '__main__':
    from matplotlib import rcParams

    FONTSIZE = 20
    NEARLY_BLACK = "#161616"
    LIGHT_GREY = "#F5F5F5"
    WHITE = "#ffffff"

    MASTER_FORMATTING = {
        "axes.formatter.limits": (-3, 3),
        "xtick.major.pad": 7,
        "ytick.major.pad": 7,
        "ytick.color": NEARLY_BLACK,
        "xtick.color": NEARLY_BLACK,
        "axes.labelcolor": NEARLY_BLACK,
        "axes.spines.bottom": True,
        "axes.spines.left": True,
        "axes.spines.right": True,
        "axes.spines.top": True,
        "axes.axisbelow": True,
        "legend.frameon": False,
        'axes.edgecolor': NEARLY_BLACK,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "mathtext.fontset": "custom",
        "font.size": FONTSIZE,
        "font.family": "sans-serif",
        "font.serif": "Helvetica",
        # "text.usetex": True,
        "savefig.bbox": "tight",
        "axes.facecolor": LIGHT_GREY,
        "axes.labelpad": 10.0,
        "axes.labelsize": FONTSIZE * 0.8,
        "axes.titlepad": 20,
        "axes.titlesize": FONTSIZE,
        "axes.grid": False,
        "grid.color": WHITE,
        "lines.markersize": 7.0,
        "lines.scale_dashes": False,
        "xtick.labelsize": FONTSIZE * 0.8,
        "ytick.labelsize": FONTSIZE * 0.8,
        "legend.fontsize": FONTSIZE * 0.8,
        "lines.linewidth": 2,
    }

    for k, v in MASTER_FORMATTING.items():
        rcParams[k] = v

    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.constants import g
    from scipy.special import erf
    # import _fig_params

    a = -g
    v = 20
    z1 = 4.2
    y0 = 0
    y1 = 1
    t = z1 / v

    def trace(z, z0):
        return y0 + ((z - z0) * (
            (-a * (z1 - z0)**2) /
            (2 * v**2) - y0 + y1)) * 1 / (z1 - z0) + (a *
                                                      (z - z0)**2) / (2 * v**2)

    def dtrace(z, z0):
        return ((-a * (z1 - z0)**2) /
                (2 * v**2) - y0 + y1) * 1 / (z1 - z0) + a * (z - z0) / (v**2)

    z = np.linspace(0.00001, z1 - 0.01, 1000)
    z_diff = np.linspace(0.4, z1 - 0.01, 1000)
    y = np.linspace(0.00001, y1 - 0.001, 1000)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(z, trace(z, 0))
    ax.plot(z, z * dtrace(0, 0))
    ax.plot(z, np.linspace(0.00001, trace(z, 0)[-1], 1000), ls='--')
    ax.set_xlim(-1, 4.8)
    ax.set_ylim(-0.3, 1.5)
    rectangle = plt.Rectangle((-0.75, -0.25),
                              1.5,
                              0.25,
                              ec='k',
                              fc=(1, 0, 0, 0))
    ax.add_patch(rectangle)
    rectangle = plt.Rectangle((z1, 0.3), 0.4, 1, ec='k', fc=(1, 0, 0, 0))
    ax.text(0,
            -0.125,
            'Sample',
            horizontalalignment='center',
            verticalalignment='center')
    ax.text(z1 + 0.2,
            0.8,
            'Detector',
            horizontalalignment='center',
            verticalalignment='center',
            rotation='vertical')
    ax.add_patch(rectangle)
    ax.set_xlabel('$z$/m')
    ax.set_ylabel('$y$/m')
    fig.savefig('gravity.png')
    plt.close(fig)

    beam_size = 0.01
    sample_size = 0.1
    theta = np.deg2rad(np.linspace(0.5, 1.5, 1000))

    beam_on_sample = beam_size / np.sin(theta)
    fwhm_to_std = 2 * np.sqrt(2 * np.log(2))
    scale_factor = erf((sample_size / beam_on_sample * fwhm_to_std))

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(np.rad2deg(theta), beam_on_sample)
    ax2 = ax.twinx()
    ax2.plot(np.rad2deg(theta), scale_factor, c='#ff7f0e')
    ax.set_ylabel('Beam size on sample/m')
    ax2.set_ylabel('Scale factor')
    ax.set_xlabel(r'$\theta$/deg')
    fig.savefig('beam_size.png')
    plt.close(fig)
