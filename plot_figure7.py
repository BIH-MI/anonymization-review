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

import matplotlib.pyplot as plt
import pandas as pd
from pysankey2 import Sankey

plt.rcParams['svg.fonttype'] = 'none'

df = pd.read_csv("data_figure_7.csv", sep=";")

def plot_figure_7(df):
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

                    'IQVIA' : cmap_a.colors[1],
                    'InGef' : cmap_a.colors[0],
                    'IBM' : cmap_a.colors[6],
                    'TriNetX': cmap_a.colors[3],
                    'Cerner' : cmap_a.colors[2],
                    'NPS': cmap_a.colors[4]},

                  "layer2": {
                    'Diseases of the circulatory system': cmap_p2.colors[7],
                    'Mental and behavioural disorders': cmap_p2.colors[7],
                    'Certain infectious and parasitic diseases': cmap_p2.colors[7],
                    'Neoplasms': cmap_p2.colors[7],
                    'Endocrine, nutritional and metabolic diseases': cmap_p2.colors[7],
                    'Codes for special purposes (COVID-19)': cmap_p2.colors[7],
                    'other': cmap_p2.colors[7]
                    }
                  }

    # Costum order
    layer_labels = {'layer1': ['Flatiron', 'TriNetX', 'Cerner', 'Optum', 'SAIL', 'InGef', 'IQVIA', 'VUMC', 'IBM',  'NPS', 'CPRD', 'SLaM NHS'],
                    'layer2':['Neoplasms', 'Codes for special purposes (COVID-19)', 'Endocrine, nutritional and metabolic diseases',
                              'Diseases of the circulatory system', 'other',
                              'Certain infectious and parasitic diseases',
                               'Mental and behavioural disorders']}

    # Plot sankey
    sky = Sankey(df, layerLabels = layer_labels,  colorDict=color_dict, colorMode="layer", stripColor='left', )
    fig, ax = sky.plot(figSize=(7, 4), fontSize=10, boxInterv=0.05, boxWidth=0.5, stripLen=8)

    # Add label for "axes"
    ax.text(0, 690, 'Data source', weight='bold', fontsize=10, ha="left", va="bottom")
    ax.text(9, 690, 'ICD-10 chapter', weight='bold', fontsize=10, ha="right", va="bottom")

    # Plot and save
    fig.tight_layout()
    plt.savefig("figure_output/figure_7.svg", bbox_inches='tight')
    plt.savefig("figure_output/figure_7.png", bbox_inches='tight')
    plt.show()
    plt.close()
    plt.show()

plot_figure_7(df)