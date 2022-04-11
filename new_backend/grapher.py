import matplotlib.pyplot as plt

def plotGermline(df):
    v = 100 / len(df.average)
    strain = "PRUEBA"
    fig = plt.figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title(f'{strain}   (n = {len(df.columns)-2})')
    axis.errorbar(df.index * v, df.average, df.stddev, linestyle=':', marker='^', capsize=3,
                  elinewidth=0.7)
    plt.show()
