import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pysankey2 import Sankey

plt.rcParams['svg.fonttype'] = 'none'
mpl.style.use("ggplot")
COLOR = 'black'
mpl.rcParams['text.color'] = COLOR
mpl.rcParams['axes.labelcolor'] = COLOR
mpl.rcParams['xtick.color'] = COLOR
mpl.rcParams['ytick.color'] = COLOR

df_counts = pd.read_excel("data_figures.xlsx", sheet_name="data_figure_5a", engine="openpyxl")
df_flows = pd.read_excel("data_figures.xlsx", sheet_name="data_figure_5b", engine="openpyxl")

def plot_figure_5a(df):

    # Set font sizes
    font_size_label = 10
    font_size_ticks = 10
    font_size_legend = 10
    font_size_bar_label = 10
    distance_bar_label = 1.5
    y_lim = 70

    # Plot configuration
    fig, ax = plt.subplots(figsize=(5, 3.5))

    x = np.arange(len(df["Name (Country)"])) # the label locations
    width = 0.35  # the width of the bars

    bars_crossborder = ax.bar(x - width/2 -0.03, df["Distribution (Data origin crossborder)"], width, color='#B3E2CD', edgecolor="black", linewidth=1)
    bars_domestic = ax.bar(x + width/2 +0.03, df["Distribution (Data origin domestic)"], width, color='#FDCDAC', edgecolor="black", linewidth=1)

    # Adding value labels to each bar
    for idx, rect in enumerate(bars_crossborder):
        ax.text(rect.get_x() + rect.get_width() / 2.0, df["Distribution (Data origin crossborder)"][idx] + distance_bar_label, str(df["Count (Data origin crossborder)"][idx]),
                ha='center', va='bottom', fontsize=font_size_bar_label)

    for idx, rect in enumerate(bars_domestic):
        ax.text(rect.get_x() + rect.get_width() / 2.0, df["Distribution (Data origin domestic)"][idx] + distance_bar_label, str(df["Count (Data origin domestic)"][idx]),
                ha='center', va='bottom', fontsize=font_size_bar_label)

    # Grid
    ax.grid(axis='x')

    # Customizations with larger font sizes
    ax.set_ylabel('Fraction of data flows', fontsize=font_size_label)
    ax.set_xticks(x)
    ax.set_xticklabels(df["Name (Country)"], fontsize=font_size_ticks,  rotation=45, ha="center")
    ax.set_yticks(np.arange(0, y_lim+1, 10), np.arange(0, y_lim+1, 10).astype(int), fontsize=font_size_ticks)
    ax.tick_params(axis='y', labelsize=font_size_ticks)
    ax.set_ylim(0, y_lim)

    ax.set_title("A\n", loc="left")

    fig.tight_layout()

    plt.legend(handles=[bars_crossborder,  bars_domestic], labels=['Cross-border sharing', 'Domestic usage'], loc='lower center', ncols = 2, bbox_to_anchor=(0.5, 1), fontsize=font_size_legend)
    plt.savefig("figure_output/figure_5a.svg", bbox_inches='tight')
    plt.savefig("figure_output/figure_5a.png", bbox_inches='tight')
    plt.show()
    plt.close()


def plot_figure_5b(df):

    # Remove columns not required and rename to "layer1" and "layer2"
    df = df[["Name (Country data origin)", "Name (Country first author)"]]
    df.rename(columns={"Name (Country data origin)":"layer1", "Name (Country first author)": "layer2"}, inplace=True)

    # Assign colors
    cmap = plt.get_cmap("Pastel2")
    color_dict = {"layer1": {"United States": cmap.colors[0],
                    'United Kingdom': cmap.colors[1],
                    'Australia': cmap.colors[2],
                    'Spain': cmap.colors[5],
                    'Germany': cmap.colors[6],
                    'Taiwan': cmap.colors[3],
                    'France': cmap.colors[4]},
                  "layer2": {
                    "United States": cmap.colors[7],
                    "United Kingdom": cmap.colors[7],
                    "Netherlands": cmap.colors[7],
                    "Japan": cmap.colors[7],
                    "Germany": cmap.colors[7],
                    "Canada": cmap.colors[7],
                    "Switzerland": cmap.colors[7]}
                  }

    # Costum order
    layer_labels = {'layer1': ["United Kingdom", "Taiwan", "Germany", "France", "Spain", "Australia", "United States"],
                    'layer2':["United States", "United Kingdom",  "Netherlands",  "Japan", "Germany", "Canada", "Switzerland"]}

    # Plot sankey
    sky = Sankey(df,layerLabels = layer_labels,colorDict=color_dict,colorMode="layer", stripColor='left', )
    fig, ax = sky.plot(figSize=(5.5, 3), fontSize=10, boxInterv=0.05, boxWidth=0.5, stripLen=7)

    # Add label for "axes"
    ax.text(0, 47, 'Data origin', weight='bold', fontsize=10, ha="left", va="bottom")
    ax.text(8, 47, 'First author', weight='bold', fontsize=10, ha="right", va="bottom")

    # Add title for subfigure
    ax.set_title("B\n", loc="left")

    # Plot and save
    fig.tight_layout()
    plt.savefig("figure_output/figure_5b.svg", bbox_inches='tight')
    plt.savefig("figure_output/figure_5b.png", bbox_inches='tight')
    plt.show()
    plt.close()
    plt.show()

plot_figure_5a(df_counts)
plot_figure_5b(df_flows)