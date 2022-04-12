import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import base64

def plotGermline(df, title="no title", strain_name_list=["NO TITLE"],file_namelist_list=["None"]):
    v = 100 / len(df[0].average)
    fig = plt.figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title(f'{title}')
    for i, df in enumerate(df):
        axis.errorbar(df.index * v, df.average, df.stddev,
                      label=f'{strain_name_list[i]} n={len(file_namelist_list[i])}', linestyle=':', marker='^',
                      capsize=3,
                      elinewidth=0.7)
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

