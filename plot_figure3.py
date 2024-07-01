import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from tabulate import tabulate

mpl.style.use("ggplot")
COLOR = 'black'
mpl.rcParams['text.color'] = COLOR
mpl.rcParams['axes.labelcolor'] = COLOR
mpl.rcParams['xtick.color'] = COLOR
mpl.rcParams['ytick.color'] = COLOR

df = pd.read_excel("data_figures.xlsx", sheet_name="data_figure_3", engine="openpyxl")

def plot_figure_3(df):

    # Drop columns not required
    df = df.drop(["Region (Country)", "Country", "Count (First author)", "Count (Data origin)"], axis=1)

    # Set index
    df = df.set_index("Name (Country)")

    # transpose
    df = df.T
    print(tabulate(df, headers='keys', tablefmt='psql'))

    # Create a colormap from 'Pastel2'
    colormap = mpl.colormaps['Pastel2']
    # Map your categories to colors from the colormap
    colors= [colormap(i) for i in range(len(df.columns.tolist()))]
    colors[-1]= colormap(8)

    # plot
    ax = df.plot.barh(stacked=True, figsize=(10, 1.5), color=colors, edgecolor = "black", linewidth = 1)
    ax.set_xlim([-2, 102])
    ax.set_xticks(range(0, 101, 10))
    ax.set_xlabel("Geographical distribution [%]", size=10)
    ax.set_yticks([0, 1], ["First author", "Data"])
    ax.invert_yaxis()  # labels read top-to-bottom

    # annotations:
    for c in ax.containers:
        # format the number of decimal places and replace 0 with an empty string
        labels_big = [f'{w:.1f}' if (w := v.get_width()) >= 3.5 else '' for v in c]
        ax.bar_label(c, labels=labels_big, label_type='center')

    plt.legend(loc='lower center', ncols = len(df.columns), bbox_to_anchor=(0.5, 1))
    plt.savefig("figure_output/figure_3.svg", bbox_inches='tight')
    plt.savefig("figure_output/figure_3.png", bbox_inches='tight')
    plt.show()
    plt.close()

plot_figure_3(df)
