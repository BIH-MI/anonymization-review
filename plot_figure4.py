import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.patches import Patch

# Uniform figure styling
mpl.style.use("ggplot")
COLOR = 'black'
mpl.rcParams['text.color'] = COLOR
mpl.rcParams['axes.labelcolor'] = COLOR
mpl.rcParams['xtick.color'] = COLOR
mpl.rcParams['ytick.color'] = COLOR

# File with data to plot
df = pd.read_excel("data_figures.xlsx", sheet_name="data_figure_4", engine="openpyxl")

# Define colors for each region
cmap = plt.get_cmap("Pastel2")
color_dict = {"Asia": cmap.colors[0], "Core Anglosphere": cmap.colors[1], "Eurasia": cmap.colors[2], "European Union": cmap.colors[3], 'South America': cmap.colors[4],  "other": "Grey"}

global_average = 0.094415295

def plot_figure_4(df):

    # Set font sizes and brake line dimensions
    font_size_label = 10
    font_size_ticks = 10
    font_size_legend = 10
    break_line_width = 0.2
    break_line_height = 0.003

    # Define break range and upper bound
    #break_lower, start_upper = 0.1375, 0.3125
    #y_lim = 0.3625
    break_lower, start_upper = 0.1375, 0.2875
    y_lim = 0.35

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 3), gridspec_kw={'height_ratios': [y_lim-start_upper, break_lower], 'hspace': 0.1})

    # Loop to plot bars in both subplots
    for posx, row in df.iterrows():
        color = color_dict[row["Region (Country)"]]
        value = row["Data origin per 1000 citable documents"]
        ax1.bar(posx, value, color=color, width=0.4, edgecolor="black", linewidth=1)
        ax2.bar(posx, value, color=color, width=0.4, edgecolor="black", linewidth=1)

        # Plot break lines
        if value > break_lower:
            ax1.plot((posx - break_line_width / 2, posx + break_line_width / 2), (start_upper - break_line_height / 2, start_upper + break_line_height / 2), color='k', clip_on=False)
            ax2.plot((posx - break_line_width/2, posx + break_line_width/2), (break_lower -break_line_height/2, break_lower + break_line_height/2), color='k', clip_on=False)

    # Draw global average
    ax2.plot((-0.5, 15.5), (global_average, global_average), color='grey', linewidth=1, linestyle="--")
    fig.text(0.74, 0.49, 'Global average', fontsize=font_size_ticks)

    # Set y-axis limits
    ax1.set_ylim(start_upper, y_lim)
    ax2.set_ylim(0, break_lower)

    # Hide the spines between subfigures
    ax1.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    # Set ticks and grid
    ax1.tick_params(axis='x', which='both', bottom=False)
    ax1.set_yticks([0.3, 0.325, 0.35])
    ax2.set_xticks(np.arange(len(df["Name (Country)"])), df["Name (Country)"], rotation=45, ha="right", fontsize=font_size_ticks)
    ax2.set_yticks(np.arange(0, break_lower, 0.025))
    ax1.grid(axis='x')
    ax2.grid(axis='x')

    # Label y axis
    fig.text(0.04, 0.5, 'Articles included per \n1,000 citable documents', va='center', rotation='vertical', fontsize=font_size_label, ha="center")

    # Legend with specified colors and no border
    regions = ["Asia", "Core Anglosphere", "Eurasia",  "European Union", "South America"]
    legend_elements = []
    for region in regions:
        legend_elements.append(Patch(facecolor=color_dict[region], label=region, edgecolor="black", linewidth=1),)
    plt.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, 1.55), ncol=5, fontsize=font_size_legend)

    plt.savefig("figure_output/figure_4.svg", bbox_inches='tight')
    plt.savefig("figure_output/figure_4.png", bbox_inches='tight')
    plt.show()
    plt.close()

plot_figure_4(df)