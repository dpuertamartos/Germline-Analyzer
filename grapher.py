import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import base64

#TODO: Adjust Y lims depending of standarize method used
#TODO: X and Y labels?

standard_colors = [[0, 0.4470, 0.7410],[0.8500, 0.3250, 0.0980],[0.4660, 0.6740, 0.1880],[0.6350, 0.0780, 0.1840],[0.4940, 0.1840, 0.5560],[0.3010, 0.7450, 0.9330],[0.9290, 0.6940, 0.1250]]

def plotGermline(df, title="no title", strain_name_list=["NO TITLE"],file_namelist_list=["None"], mitotic_mode = False, strains_mitotic_percentage=["32","25"], strains_error=["5","3"],
                 dpi=200, average_length=100, absolute_cut=None):
    CONVERSION = 0.22/3.5
    print("absolute", absolute_cut)
    unit_conversion = True
    #place plot point in the midle of interval (for ex. for 10 intervals, first point will be at 5%)
    v = 100 / len(df[0].average)
    transformer = lambda x: (x+(v/2))
    a = np.array([transformer(xi) for xi in df[0].index * v])
    if unit_conversion:
        if absolute_cut:
            super_average = absolute_cut
            print("absolute super average", super_average)
        else:
            #super_average calculates average length of all strains
            print("average_length", average_length)
            super_average = round(sum([a[1] for a in average_length])/len(average_length),1)
            print("super_average", super_average)

        super_average_converted = super_average * CONVERSION
        #b is x axis values converted to new units
        b = np.array([round(e*super_average_converted/100,1) for e in a])
        print("inside plotGermline")
        print("a",a,"b",b)
        a = b

    if mitotic_mode:
        fig, axis = plt.subplots(2, constrained_layout=True,
                                 gridspec_kw={'height_ratios': [len(strain_name_list), 20]}, dpi=dpi)
        # axis[1].set_title(f'{title}')
        for i, df in enumerate(df):
            axis[1].errorbar(a, df.average, df.stddev,
                             label=f'{strain_name_list[i]} n={len(file_namelist_list[i])}', linestyle=':', marker='^',
                             capsize=3,
                             elinewidth=0.7)
        axis[1].set_xlim(0, a[-1]+1)
        axis[1].legend()
        strains = strain_name_list
        mean_mitotic_percentage = [float(p) for p in strains_mitotic_percentage]
        subplot_2_error = [float(p) for p in strains_error]
        axis[0].barh(strains, mean_mitotic_percentage, xerr=subplot_2_error,
                     color=standard_colors[0:len(mean_mitotic_percentage)])
        axis[0].set_title('PRUEBA')
        axis[0].invert_yaxis()
        axis[0].set_xlim(0, 100)
        axis[0].xaxis.set_visible(False)

    else:
        fig, axis = plt.subplots(1, constrained_layout = True, dpi=dpi)
        # fig = plt.figure(constrained_layout = True, dpi=dpi)
        # axis = fig.add_axes((0.1, 0.3, 0.8, 0.6))
        for i, df in enumerate(df):
            axis.errorbar(a, df.average, df.stddev,
                             label=f'{strain_name_list[i]} n={len(file_namelist_list[i])}', linestyle=':', marker='^',
                             capsize=3,
                             elinewidth=0.7)
        axis.set_xlim(0, a[-1]+1)
        # #UNCOMMENT FOR Y LIM
        # axis.set_ylim(30, 108)
        # ax2 = fig.add_axes((0.1, 0.1, 0.8, 0.0))
        # ax2.yaxis.set_visible(False)
        # new_tick_locations = np.array([0,0.2,0.4,0.6,0.8,1])
        # ax2.set_xticks(new_tick_locations)
        # b = np.array([round(e*super_average,1) for e in new_tick_locations])
        # ax2.set_xticklabels(b)
        # ax2.set_xlabel(average_length[0][3])
        axis.legend()

    plt.show()
    return fig

def convert_plot_to_png(fig):
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    return pngImage

def encode_png_to_base64(png):
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(png.getvalue()).decode('utf8')
    return pngImageB64String

