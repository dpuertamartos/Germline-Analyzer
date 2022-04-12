import matplotlib.pyplot as plt

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
