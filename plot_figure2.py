import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

plt.rcParams['svg.fonttype'] = 'none'
mpl.style.use("ggplot")
COLOR = 'black'
mpl.rcParams['text.color'] = COLOR
mpl.rcParams['axes.labelcolor'] = COLOR
mpl.rcParams['xtick.color'] = COLOR
mpl.rcParams['ytick.color'] = COLOR

df = pd.read_excel("data_figures.xlsx", sheet_name="data_figure_2", engine="openpyxl")

def plot_figure_2(df):

    # Set font sizes
    font_size_label = 10
    font_size_ticks = 10
    font_size_legend = 10
    font_size_text = 10
    distance_bar_label = 1.5

    # Creating x values
    years_index = list(range(len(df["Year"])))

    # Plotting
    fig, ax = plt.subplots(figsize=(4.5, 2.5))
    cmap = plt.get_cmap("Pastel2")
    bars_non_covid = ax.bar(years_index, df["Normalized (Non-COVID-19-related)"], label='Non-COVID-19-related', color=cmap.colors[0], width=0.4, edgecolor="black", linewidth=1)
    bars_covid = ax.bar(years_index, df["Normalized (COVID-19-related)"], bottom=df["Normalized (Non-COVID-19-related)"], label='COVID-19-related', color=cmap.colors[1], width=0.4, edgecolor="black", linewidth=1)

    # Adding text above the stacked bars
    total_heights = df["Normalized (Non-COVID-19-related)"] + df["Normalized (COVID-19-related)"] + distance_bar_label
    for idx, rect in enumerate(bars_non_covid):
        ax.text(rect.get_x() + rect.get_width() / 2.0, total_heights[idx], str(df["Count (Total)"][idx]),
                ha='center', va='bottom', fontsize=font_size_text)

    # Draw regression
    sns.regplot(x=years_index, y=df["Normalized (COVID-19-related)"] + df["Normalized (Non-COVID-19-related)"], scatter=False, line_kws={"color": "gray"})
    sns.regplot(x=years_index, y=df["Normalized (Non-COVID-19-related)"], scatter=False, line_kws={"color": "green"})

    # Grid
    ax.grid(axis='x')

    # Axis labels and ticks
    ax.set_ylim(0, 14)
    ax.set_xlabel('Year of publication', size=font_size_label)
    ax.set_ylabel('Articles included per \n 100,000 published articles', size=font_size_label)
    ax.set_xticks(years_index, df["Year"], fontsize=font_size_ticks)
    ax.set_yticks(np.arange(0, 14.1, 2), np.arange(0, 14.1, 2).astype(int), fontsize=font_size_ticks)

    # Legend
    plt.legend(handles=[bars_non_covid, bars_covid], labels=['Other focus', 'COVID-19 related'], bbox_to_anchor=(0.5, 1.25), loc='upper center', ncol=2, fontsize=font_size_legend)

    plt.savefig("figure_output/figure_2.svg", bbox_inches='tight')
    plt.savefig("figure_output/figure_2.png", bbox_inches='tight')
    plt.show()
    plt.close()

plot_figure_2(df)

