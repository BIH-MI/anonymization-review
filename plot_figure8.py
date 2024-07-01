import matplotlib.pyplot as plt
import pandas as pd
from pysankey2 import Sankey

plt.rcParams['svg.fonttype'] = 'none'

df = pd.read_excel("data_figures.xlsx", sheet_name="data_figure_8", engine="openpyxl")

def plot_figure_8(df):
    # Remove columns not required and rename to "layer1" and "layer2"
    df.rename(columns={"Abbreviation (Data source)":"layer1", "Name (ICD-10 chapter)": "layer2"}, inplace=True)

    print(df["layer1"].unique())
    print(df["layer2"].unique())

    # Assign colors
    cmap_p1 = plt.get_cmap("Pastel1")
    cmap_p2 = plt.get_cmap("Pastel2")
    cmap_a = plt.get_cmap("Dark2")
    color_dict = {"layer1": {
                    'Optum' : cmap_p2.colors[0],
                    'Flatiron': cmap_p2.colors[1],
                    'VUMC': cmap_p2.colors[2],
                    'SAIL' : cmap_p2.colors[3],
                    'CPRD': cmap_p1.colors[0],
                    'SLaM NHS' : cmap_p2.colors[5],

                    'WADLS' : cmap_a.colors[0],
                    'IBM' : cmap_a.colors[6],
                    'TriNetX': cmap_a.colors[3],
                    'Cerner' : cmap_a.colors[2],
                    'NPS': cmap_a.colors[4]},

                  "layer2": {
                    'IX) Diseases of the circulatory system': cmap_p2.colors[7],
                    'V) Mental and behavioural disorders': cmap_p2.colors[7],
                    'I) Certain infectious and parasitic diseases': cmap_p2.colors[7],
                    'II) Neoplasms': cmap_p2.colors[7],
                    'IV) Endocrine, nutritional and metabolic diseases': cmap_p2.colors[7],
                    'XXII) Codes for special purposes (COVID-19)': cmap_p2.colors[7],
                    'other': cmap_p2.colors[7]
                    }
                  }

    # Costum order
    layer_labels = {'layer1': ['Flatiron', 'TriNetX', 'Cerner', 'Optum', 'SAIL', 'WADLS', 'VUMC', 'IBM',  'NPS', 'CPRD', 'SLaM NHS'],
                    'layer2':['II) Neoplasms', 'XXII) Codes for special purposes (COVID-19)', 'IV) Endocrine, nutritional and metabolic diseases',
                              'IX) Diseases of the circulatory system', 'other',
                              'I) Certain infectious and parasitic diseases',
                               'V) Mental and behavioural disorders']}

    # Plot sankey
    sky = Sankey(df, layerLabels = layer_labels,  colorDict=color_dict, colorMode="layer", stripColor='left', )
    fig, ax = sky.plot(figSize=(7, 4), fontSize=10, boxInterv=0.05, boxWidth=0.5, stripLen=8)

    # Add label for "axes"
    ax.text(0, 490, 'Data source', weight='bold', fontsize=10, ha="left", va="bottom")
    ax.text(9, 490, 'ICD-10 chapter', weight='bold', fontsize=10, ha="right", va="bottom")

    # Plot and save
    fig.tight_layout()
    plt.savefig("figure_output/figure_8.svg", bbox_inches='tight')
    plt.savefig("figure_output/figure_8.png", bbox_inches='tight')
    plt.show()
    plt.close()
    plt.show()

plot_figure_8(df)