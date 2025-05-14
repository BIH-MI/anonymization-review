'''
------------------------------------------------------------------------------
Copyright 2025, T. Meurers

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
------------------------------------------------------------------------------
'''

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

df = pd.read_csv("data_figure_6.csv", sep=";")

def plot_figure_6(df):

    # Setting colors for each country with the specified colors
    colors = df["Origin (Data source)"].map({"United States": "#ADDBC7", "United Kingdom": "#FDCDAC", "Australia": "#CBD5E8", "Germany": "#f4cae4"})

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
    ax.set_ylim(0, 120)

    # Grid
    ax.grid(axis='x')

    # Legend with specified colors and no border
    legend_elements = [
        Patch(facecolor='#ADDBC7', label='United States', edgecolor="black", linewidth=1),
        Patch(facecolor='#FDCDAC', label='United Kingdom', edgecolor="black", linewidth=1),
        Patch(facecolor='#f4cae4', label='Germany', edgecolor="black", linewidth=1),
        Patch(facecolor='#CBD5E8', label='Australia', edgecolor="black", linewidth=1),
    ]
    plt.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, 1.05), ncol=4, fontsize=font_size_legend)

    plt.savefig("figure_output/figure_6.svg", bbox_inches='tight')
    plt.savefig("figure_output/figure_6.png", bbox_inches='tight')
    plt.savefig("figure_output/figure_6.pdf", bbox_inches='tight')
    plt.show()
    plt.close()

plot_figure_6(df)
