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

df = pd.read_excel("data_figures.xlsx", sheet_name="data_figure_6", engine="openpyxl")

def plot_figure_6(df):

    # Introduce line breaks for cleaner formatting
    df = df.rename(columns={'Distribution (ICD-10 chapter)': 'ICD-10\nchapter'})

    # Drop columsn not required
    df = df.drop(["ICD-10 chapter", "Count (ICD-10 chapter)"], axis=1)

    # Set index
    df = df.set_index("Name (ICD-10 chapter)")

    # transpose
    df = df.T
    print(tabulate(df, headers='keys', tablefmt='psql'))

    # Create a colormap from 'Pastel2'
    colormap = mpl.colormaps['Pastel2']
    # Map your categories to colors from the colormap
    colors= [colormap(i) for i in range(len(df.columns.tolist()))]
    colors[-1]= colormap(8)

    # plot
    ax = df.plot.barh(stacked=True, figsize=(10, 1), color=colors, edgecolor = "black", linewidth = 1)
    ax.set_xlim([-2, 102])
    ax.set_xticks(range(0, 101, 10))
    ax.set_xlabel("Distribution [%]", size=10)
    ax.invert_yaxis()  # labels read top-to-bottom

    # annotations:
    for c in ax.containers:
        # format the number of decimal places and replace 0 with an empty string
        labels_big = [f'{w:.1f}' if (w := v.get_width()) >= 3.5 else '' for v in c]
        ax.bar_label(c, labels=labels_big, label_type='center')

    plt.legend(loc='lower center', ncols = 2, bbox_to_anchor=(0.5, 1))
    plt.savefig("figure_output/figure_6.svg", bbox_inches='tight')
    plt.savefig("figure_output/figure_6.png", bbox_inches='tight')
    plt.show()
    plt.close()

plot_figure_6(df)