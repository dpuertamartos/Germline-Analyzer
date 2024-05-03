import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import base64


def extract_x_label(array):
    if array[0]:
        return "Pixels"
    elif array[1]:
        return "Microns"
    elif array[2]:
        return "Germline cell diameters (gcd)"
    else:
        return "Relative length (%)"

def extract_y_label(array):
    if array[0]:
        return "Relative intensity (%)"
    elif array[1]:
        return "Increase compared to " + array[2][0] + "-" + array[2][1] + "%"
    else:
        return "Absolute intensity (0-255)"


def calculate_x_axis_points(df, conversion, absolute_cut, average_length, middle_point=True):
    # place plot point in the midle of interval (for ex. for 10 intervals, first point will be at 5%)

    v = 100 / len(df[0].average)
    if middle_point:
        # position must be added v/2 if you want the middle of the interval
        transformer = lambda x: (x+(v/2))
        a = np.array([transformer(xi) for xi in df[0].index * v])
    else:
        a = np.array([xi for xi in df[0].index * v])

    if conversion:
        if absolute_cut:
            super_average = absolute_cut
        else:
            super_average = round(sum([a[1] for a in average_length])/len(average_length),1)

        super_average_converted = super_average * conversion
        #x axis values converted to new units
        a = np.array([round(e*super_average_converted/100,1) for e in a])

    return a


standard_colors = [[0, 0.4470, 0.7410],[0.8500, 0.3250, 0.0980],[0.4660, 0.6740, 0.1880],[0.6350, 0.0780, 0.1840],[0.4940, 0.1840, 0.5560],[0.3010, 0.7450, 0.9330],[0.9290, 0.6940, 0.1250]]


def plotGermline(df, title="", strain_name_list=["NO TITLE"],file_namelist_list=["None"], mitotic_mode = False, strains_mitotic_percentage=["32","25"], strains_error=["5","3"],
                 dpi=200, average_length=100, absolute_cut=None, conversion=None, x_label=[True, False, False],
                 y_label=[False, False]):

    a = calculate_x_axis_points(df, conversion, absolute_cut, average_length)

    if mitotic_mode and not absolute_cut:
        fig, axis = plt.subplots(2, constrained_layout=True,
                                 gridspec_kw={'height_ratios': [len(strain_name_list), 20]}, dpi=dpi)
        # axis[1].set_title(f'{title}')
        for i, df in enumerate(df):
            axis[1].errorbar(a, df.average, df.stddev,
                             label=f'{strain_name_list[i]} n={len(file_namelist_list[i])}', linestyle=':', marker='^',
                             capsize=3,
                             elinewidth=0.7)
        axis[1].set_xlim(0, a[-1]+1)
        axis[1].legend(prop={'size': 13, 'style': 'italic'})
        axis[1].set_xlabel(extract_x_label(x_label), fontsize=13)
        axis[1].set_ylabel(extract_y_label(y_label), fontsize=13)
        strains = strain_name_list
        mean_mitotic_percentage = [float(p) for p in strains_mitotic_percentage]
        subplot_2_error = [float(p) for p in strains_error]
        axis[0].barh(strains, mean_mitotic_percentage, xerr=subplot_2_error,
                     color=standard_colors[0:len(mean_mitotic_percentage)])
        axis[0].set_title(title)
        axis[0].invert_yaxis()
        axis[0].set_xlim(0, 100)
        axis[0].xaxis.set_visible(False)

    else:
        fig, axis = plt.subplots(1, constrained_layout=True, dpi=dpi)
        for i, df in enumerate(df):
            axis.errorbar(a, df.average, df.stddev,
                             label=f'{strain_name_list[i]} n={len(file_namelist_list[i])}', linestyle=':', marker='^',
                             capsize=3,
                             elinewidth=0.7)
        axis.set_xlim(0, a[-1]+1)
        axis.set_xlabel(extract_x_label(x_label), fontsize=13)
        axis.set_ylabel(extract_y_label(y_label), fontsize=13)
        axis.legend(prop={'size': 13, 'style': 'italic'})

    return fig

def convert_plot_to_png(fig):
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    return pngImage

def encode_png_to_base64(png):
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(png.getvalue()).decode('utf8')
    return pngImageB64String
