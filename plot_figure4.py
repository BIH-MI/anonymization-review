import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch
import numpy as np

mpl.style.use("ggplot")
COLOR = 'black'
mpl.rcParams['text.color'] = COLOR
mpl.rcParams['axes.labelcolor'] = COLOR
mpl.rcParams['xtick.color'] = COLOR
mpl.rcParams['ytick.color'] = COLOR

df = pd.read_excel("data_figures.xlsx", sheet_name="data_figure_4", engine="openpyxl")

def plot_figure_4(df):

    # Setting colors for each country with the specified colors
    colors = df["Origin (Data source)"].map({"United States": "#ADDBC7", "United Kingdom": "#FDCDAC", "Australia": "#CBD5E8"})

    # Set font sizes
    font_size_label = 10
    font_size_ticks = 10
    font_size_legend = 10

    X = np.arange(len(df["Abbreviation (Data source)"]))

    # Plotting
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(X, df["Count (Data source)"], color=colors, edgecolor="black", linewidth=1, width=0.4,)
    ax.set_xlabel('Data source', fontsize=font_size_label)
    ax.set_ylabel('Number of articles', fontsize=font_size_label)
    ax.set_xticks(X, df["Abbreviation (Data source)"], rotation=45, ha="right", fontsize=font_size_ticks)
    ax.set_ylim(0, 100)

    # Grid
    ax.grid(axis='x')

    # Legend with specified colors and no border
    legend_elements = [
        Patch(facecolor='#ADDBC7', label='United States', edgecolor="black", linewidth=1),
        Patch(facecolor='#FDCDAC', label='United Kingdom', edgecolor="black", linewidth=1),
        Patch(facecolor='#CBD5E8', label='Australia', edgecolor="black", linewidth=1)
    ]
    plt.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=font_size_legend)

    plt.savefig("figure_output/figure_4.svg", bbox_inches='tight')
    plt.savefig("figure_output/figure_4.png", bbox_inches='tight')
    plt.show()
    plt.close()

plot_figure_4(df)
