import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import base64

#TODO: DPI SELECTOR, AND CHECK THAT BASE64 ENCODING DOESN'T CHANGE DPI
#TODO: Adjust Y lims depending of standarize method used
#TODO: X and Y labels?

def plotGermline(df, title="no title", strain_name_list=["NO TITLE"],file_namelist_list=["None"]):
    v = 100 / len(df[0].average)
    fig, axis = plt.subplots(2,constrained_layout = True, gridspec_kw={'height_ratios': [20, 2]})
    axis[0].set_title(f'{title}')
    for i, df in enumerate(df):
        axis[0].errorbar(df.index * v, df.average, df.stddev,
                      label=f'{strain_name_list[i]} n={len(file_namelist_list[i])}', linestyle=':', marker='^',
                      capsize=3,
                      elinewidth=0.7)

    axis[0].legend()
    #subplot 2  para mitotic zone, sin implementar, hace automaticamente prueba con estos datos,
    #en heigh ratios, el segundo dato debe ser igual al numero de strains para que salga
    #compensado el aspecto(en este caso 2)
    #TODO: make the function receive second subplot data
    strains = ['MES-4',"MES-4 falso"]
    mean_mitotic_percentage = [32,25]
    subplot_2_error = [2,3]
    axis[1].barh(strains, mean_mitotic_percentage,xerr=subplot_2_error)
    axis[1].set_title('Mitotic zone')
    axis[1].set_xlim(0, 100)
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

