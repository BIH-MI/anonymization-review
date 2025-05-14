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

import pandas as pd

def load_and_preprocess_charting():

    # load data
    chart_file = "charting_results/results_20250228.csv"
    df = pd.read_csv(chart_file, dtype=str, sep=";", encoding='unicode_escape')

    # Fill empty cells with empty string
    df = df.fillna('')

    # Remove excluded articles
    df = df[df['Include'] == 'Yes']

    # split 1:n fields
    df["Data source_list"] = df.apply(lambda row: [label.lstrip() for label in row["Data source"].split(",")], axis=1)
    df["Data origin_list"] = df.apply(lambda row: row["Data origin"].replace(" ", "").strip().split(","), axis=1)

    print("Loaded %d articles" % (len(df.index)))
    return df

def preprocess_scimagojr():

    years = ["2018", "2019", "2020", "2021", "2022"]

    df = pd.DataFrame()
    for year in years:
        # read csv
        df_temp = pd.read_csv(f"auxiliary_data/scimagojr/scimagojr country rank {year}.csv", sep=";")[["Country", "Citable documents"]]
        df_temp.rename(columns={"Citable documents": f"Citable documents_{year}"}, inplace=True)

        if year == years[0]:
            df = df_temp
        else:
            df = pd.merge(df, df_temp, how="outer", on="Country")

    df.rename(columns={"Country": "Name (Country)"}, inplace=True)
    df["Citable documents_total"] = df[[f'Citable documents_{year}' for year in years]].sum(axis=1)

    df.to_csv("auxiliary_data/Citable_documents_per_country.csv", sep=";", index=False)

def preprocess_figure_2(df):

    def filter_only_full_date_information(row):
        required_keys = [
            "Submission year",
            "Publishing year",
        ]
        # Check if any required field is missing, empty, or marked as "na".
        for key in required_keys:
             if str(row[key]).strip().lower() in ("na", ""):
                return False
        return True

    def filter_year_range(row):
        return row["Publishing year"]  != "2022"

    # Remove records without complete date information and recorded after 2021
    #df = df[df.apply(filter_only_full_date_information, axis=1)]
    #df = df[df.apply(filter_year_range, axis=1)]

    # Group by year and COVID-19 research status, and then count the entries
    df = df.groupby(['Publishing year', 'COVID-19 research']).size().unstack(fill_value=0)

    # Reset index to turn the multi-index into columns
    df.reset_index(inplace=True)

    # Rename the 'Publishing year Pubmed' column to 'Year'
    df.rename(columns={'Publishing year': 'Year', 'No': 'Count (Non-COVID-19-related)', 'Yes':'Count (COVID-19-related)'}, inplace=True)

    # Read auxiliary data
    auxiliary_data = pd.read_csv("auxiliary_data/PubMed_number_paper_published.csv", sep=";", dtype=str)

    # Merge the DataFrames
    df = pd.merge(df, auxiliary_data, on='Year')

    # Normalize paper count from review with total number of published papers
    df['Paper-published-total'] = df['Paper-published-total'].astype(int)
    df['Count (Non-COVID-19-related)'] = df['Count (Non-COVID-19-related)'].astype(int)
    df['Count (COVID-19-related)'] = df['Count (COVID-19-related)'].astype(int)
    df['Count (Total)'] = df['Count (Non-COVID-19-related)'] + df['Count (COVID-19-related)']
    scaling_factor = 100000
    df['Normalized (Non-COVID-19-related)'] = (df['Count (Non-COVID-19-related)'] / df['Paper-published-total']) * scaling_factor
    df['Normalized (COVID-19-related)'] = (df['Count (COVID-19-related)'] / df['Paper-published-total']) * scaling_factor

    # Save to xlsx
    df.to_csv('data_figure_2.csv', sep =";", index=False)

def preprocess_figure_3(df, other_threshold = 5):
    def filter_only_single_data_origin(row):
        origin_list = row['Data origin_list']
        origin = origin_list[0]
        return len(origin_list) == 1 and origin != "various"

    # Remove records with more than one data origin
    df = df[df.apply(filter_only_single_data_origin, axis=1)]

    # Count occurrences in each specific column
    first_author_counts = df['First author'].value_counts().reset_index()
    first_author_counts.columns = ['Country', 'Count (First author)']
    data_origin_counts = df['Data origin'].value_counts().reset_index()
    data_origin_counts.columns = ['Country', 'Count (Data origin)']

    # Merge the DataFrames on 'Country'
    df = pd.merge(first_author_counts, data_origin_counts, on='Country', how='outer')
    # Read external CSV with total number of articles published
    auxiliary_data = pd.read_csv("auxiliary_data/Country_information.csv", sep=";")[["Country", "Name (Country)", "Region (Country)"]]
    df = pd.merge(df, auxiliary_data, on='Country', how='outer')

    # Fill missing values with 0
    df.fillna(0, inplace=True)
    # Convert float counts to integers
    df['Count (First author)'] =df['Count (First author)'].astype(int)
    df['Count (Data origin)'] = df['Count (Data origin)'].astype(int)
    # Calculate distribution
    df["Distribution (First author)"] = df["Count (First author)"] * 100 / df["Count (First author)"].sum()
    df["Distribution (Data origin)"] = df["Count (Data origin)"] * 100 / df["Count (Data origin)"].sum()
    # Split country into countries commonly mentioned and "other" by given threshold
    df_countries_other = df[df["Distribution (First author)"] < other_threshold]
    df = df[df["Distribution (First author)"] >= other_threshold]
    # Sort
    df = df.sort_values("Count (First author)", ascending=False)
    # Create and append "other" row
    row_other = {"Country": "other", "Name (Country)": "other", "Region (Country)":"other",
                 "Count (First author)": df_countries_other["Count (First author)"].sum(),
                 "Count (Data origin)": df_countries_other["Count (Data origin)"].sum(),
                 "Distribution (First author)": df_countries_other["Distribution (First author)"].sum(),
                 "Distribution (Data origin)": df_countries_other["Distribution (Data origin)"].sum()}
    df = df._append(row_other, ignore_index=True)

    # Save to csv
    df.to_csv('data_figure_3.csv', sep =";", index=False)

def preprocess_figure_4(df):

    def filter_only_single_data_origin(row):
        origin_list = row['Data origin_list']
        origin = origin_list[0]
        return len(origin_list) == 1 and origin != "various"

    def filter_other(row):
        return row["Citable documents_total"] <= top_20_threshold or pd.isna(row["Count (Data origin)"])

    def filter_domestic_use(row):
        return row['Data origin'] == row["First author"]

    # Remove records with more than one data origin
    df = df[df.apply(filter_only_single_data_origin, axis=1)]
    # Filter articles where first author and data originate from the same country
    df = df[df.apply(filter_domestic_use, axis=1)]

    # Count occurrences of data origin
    data_origin_counts = df['Data origin'].value_counts().reset_index()
    data_origin_counts.columns = ['Country', 'Count (Data origin)']

    auxiliary_data_country_information = pd.read_csv("auxiliary_data/Country_information.csv", sep=";")[["Country", "Name (Country)", "Region (Country)"]]
    auxiliary_data_citable_documents = pd.read_csv("auxiliary_data/Citable_documents_per_country.csv", sep=";")[["Name (Country)", "Citable documents_total"]]
    df = pd.merge(data_origin_counts, auxiliary_data_country_information, how="outer", on="Country")
    df = pd.merge(df, auxiliary_data_citable_documents, on='Name (Country)', how='outer')

    # Calculate top-20 threshold
    citable_document_values = df["Citable documents_total"].unique()
    citable_document_values.sort()
    top_20_threshold = citable_document_values[-20]

    # Calculate data origin per 1000 citable documents
    df["Data origin per 1000 citable documents"] = df["Count (Data origin)"] * 1000 / df["Citable documents_total"]

    # Split countries into top-20 and "other"
    df_other = df[df.apply(filter_other, axis=1)]
    df = df[~df.apply(filter_other, axis=1)]

    # Sort
    df = df.sort_values(['Region (Country)', 'Data origin per 1000 citable documents'], ascending=[True, False])

    # Create and append "other" row
    row_other = {"Country": "other", "Name (Country)": "other", "Region (Country)": "other",
                 "Citable documents_total": df_other["Citable documents_total"].sum(),
                 "Count (Data origin)": df_other["Count (Data origin)"].sum(),
                 "Data origin per 1000 citable documents": df_other["Count (Data origin)"].sum() * 1000 / df_other["Citable documents_total"].sum()}
    df = df._append(row_other, ignore_index=True)

    # Save to csv
    df.to_csv('data_figure_4.csv', sep =";", index=False)

def preprocess_figure_5(df, other_threshold_5a=20, other_threshold_5b=3):

    def filter_crossborder_origin(row):
        return row['Data origin_list'] != row["First author"]

    def filter_various(row):
        return row['Data origin_list'] != "various"

    df = df.explode('Data origin_list')
    df = df[df.apply(filter_various, axis=1)]
    df_crossborder = df[df.apply(filter_crossborder_origin, axis=1)]
    df_domestic = df[~df.apply(filter_crossborder_origin, axis=1)]

    """ 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Calculate data for figure 5a
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Count occurrences in each specific column
    data_origin_counts_crossborder = df_crossborder['Data origin_list'].value_counts().reset_index()
    data_origin_counts_crossborder.columns = ['Country', 'Count (Data origin crossborder)']
    data_origin_counts_domestic = df_domestic['Data origin_list'].value_counts().reset_index()
    data_origin_counts_domestic.columns = ['Country', 'Count (Data origin domestic)']

    # Merge the DataFrames on 'Country'
    df_counts = pd.merge(data_origin_counts_crossborder, data_origin_counts_domestic, on='Country', how='outer')

    # Read external CSV to append the name of countries
    auxiliary_data = pd.read_csv("auxiliary_data/Country_information.csv", sep=";")[["Country", "Name (Country)"]]
    df_counts = pd.merge(df_counts, auxiliary_data, on='Country', how='left')

    # Fill missing values with 0
    df_counts.fillna(0, inplace=True)

    # Convert float counts to integers
    df_counts['Count (Data origin crossborder)'] = df_counts['Count (Data origin crossborder)'].astype(int)
    df_counts['Count (Data origin domestic)'] = df_counts['Count (Data origin domestic)'].astype(int)

    # Add total number of data flows
    df_counts['Count (Data origin)'] = df_counts['Count (Data origin crossborder)'] + df_counts['Count (Data origin domestic)']

    # Calculate relative distribution
    df_counts['Distribution (Data origin crossborder)'] = df_counts['Count (Data origin crossborder)'] * 100 / df_counts['Count (Data origin crossborder)'].sum()
    df_counts['Distribution (Data origin domestic)'] = df_counts['Count (Data origin domestic)'] * 100 / df_counts['Count (Data origin domestic)'].sum()

    # split country files into countries commonly mentioned and "other" by given threshold
    df_counts_other = df_counts[df_counts['Count (Data origin)'] < other_threshold_5a]
    df_counts = df_counts[df_counts['Count (Data origin)'] >= other_threshold_5a]

    # Introduce line breaks for cleaner formatting
    df_counts.loc[df_counts['Name (Country)'] == 'United States', 'Name (Country)'] = 'United\nStates'
    df_counts.loc[df_counts['Name (Country)'] == 'United Kingdom', 'Name (Country)'] = 'United\nKingdom'

    # Sort countries
    df_counts = df_counts.sort_values("Count (Data origin crossborder)", ascending=False)

    # Calculate and append "other" row
    row_other = {"Country": "other", "Name (Country)": "other",
                 "Count (Data origin crossborder)": df_counts_other["Count (Data origin crossborder)"].sum(),
                 "Count (Data origin domestic)": df_counts_other["Count (Data origin domestic)"].sum(),
                 "Distribution (Data origin crossborder)": df_counts_other["Distribution (Data origin crossborder)"].sum(),
                 "Distribution (Data origin domestic)": df_counts_other["Distribution (Data origin domestic)"].sum()}
    df_counts = df_counts._append(row_other, ignore_index=True)

    """ 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Calculate data for figure 5b
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Filter combinations that do occure less than "other_threshold_5b" times
    df_combinations = df_crossborder.groupby(['First author', 'Data origin_list']).filter(lambda x: len(x) >= other_threshold_5b)[['First author', 'Data origin_list']]

    # Append full country name
    df_combinations = pd.merge(df_combinations, auxiliary_data, left_on='First author', right_on='Country', how='left')
    df_combinations = df_combinations.rename(columns={"Name (Country)": "Name (Country first author)"})
    df_combinations = pd.merge(df_combinations, auxiliary_data, left_on='Data origin_list', right_on='Country', how='left')
    df_combinations = df_combinations.rename(columns={"Name (Country)": "Name (Country data origin)"})
    df_combinations = df_combinations[["First author", "Data origin_list",	"Name (Country first author)", "Name (Country data origin)"]]

    # Save to csv
    df_counts.to_csv('data_figure_5a.csv', sep =";", index=False)
    df_combinations.to_csv('data_figure_5b.csv', sep =";", index=False)

def preprocess_figure_6(df, other_threshold = 10):

    def filter_only_specific_source(row):
        return row['Data source_list'] != "Multiple" and row['Data source_list'] != "Multiple (IPD Meta)" and row['Data source_list'] != "Not precisely specified"

    df = df.explode('Data source_list')

    # Remove records not assigned to a specific source
    df = df[df.apply(filter_only_specific_source, axis=1)]

    # Count occurrences of sources
    df = df['Data source_list'].value_counts().reset_index()
    df.columns = ['Data source', 'Count (Data source)']

    # Read external CSV with total number of articles published
    auxiliary_data = pd.read_csv("auxiliary_data/Data_source_information.csv", sep=";")
    df = pd.merge(df, auxiliary_data, on='Data source', how='left')

    # Convert float counts to integers
    df['Count (Data source)'] = df['Count (Data source)'].astype(int)

    # Remove uncommon custodians
    df = df[df["Count (Data source)"] >= other_threshold]

    # Save to csv
    df.to_csv('data_figure_6.csv', sep=";", index=False)

def preprocess_figure_7(df, other_threshold_source=10, other_threshold_icd=25):

    def filter_only_specific_custodian(row):
        return row['Data source_list'] != "Multiple" and row['Data source_list'] != "Not precisely specified"

    def filter_only_assigned_ICD_chapter(row):
        return row['ICD-10 chapter'] != ""

    df = df.explode('Data source_list')

    # Remove records not assigned to a specific custodian
    df= df[df.apply(filter_only_specific_custodian, axis=1)]

    # Remove uncommon data sources
    df = df.groupby('Data source_list').filter(lambda x: len(x) >= other_threshold_source)

    # Remove records not assigned to a specific ICD-10 chapter
    df = df[df.apply(filter_only_assigned_ICD_chapter, axis=1)]

    # Replace uncommon ICD-10 chapters with "other"
    counts = df['ICD-10 chapter'].value_counts()
    mask = df['ICD-10 chapter'].map(counts)
    df['ICD-10 chapter'] = df['ICD-10 chapter'].where(mask >= other_threshold_icd, 'other')

    # Remove old, unprocessed "Data source" column and rename the exploded list to "Data source"
    df = df.drop('Data source', axis=1)
    df = df.rename(columns={"Data source_list":"Data source"})

    # Read external CSV to add name of ICD chapter and abbreviation of custodian
    auxiliary_data = pd.read_csv("auxiliary_data/Data_source_information.csv", sep=";")
    df = pd.merge(df, auxiliary_data, on='Data source', how='left')
    auxiliary_data = pd.read_csv("auxiliary_data/ICD-10_chapter_mapping.csv", sep=";")
    df = pd.merge(df, auxiliary_data, on='ICD-10 chapter', how='left')

    df = df[["Abbreviation (Data source)", "Name (ICD-10 chapter)"]]

    # Save to csv
    df.to_csv('data_figure_7.csv', sep=";", index=False)

def preprocess_figure_S1(df, other_threshold = 5):
    def filter_only_assigned_ICD_chapter(row):
        return row['ICD-10 chapter'] != ""

    # Remove records not assigned to a chapter
    df_filtered = df[df.apply(filter_only_assigned_ICD_chapter, axis=1)]

    # Count occurrences of chapters
    df = df_filtered['ICD-10 chapter'].value_counts().reset_index()
    df.columns = ['ICD-10 chapter', 'Count (ICD-10 chapter)']

    # Read external CSV with total number of articles published
    auxiliary_data = pd.read_csv("auxiliary_data/ICD-10_chapter_mapping.csv", sep=";", dtype=str)
    df = pd.merge(df, auxiliary_data, on='ICD-10 chapter', how='outer')

    # Fill missing values with 0
    df.fillna(0, inplace=True)

    # Convert float counts to integers
    df['Count (ICD-10 chapter)'] = df['Count (ICD-10 chapter)'].astype(int)

    # Calculate distribution
    df['Distribution (ICD-10 chapter)'] = df['Count (ICD-10 chapter)'] * 100 / df['Count (ICD-10 chapter)'].sum()

    # Split country files into countries commonly mentioned and "other" by given threshold
    df_other = df[df["Distribution (ICD-10 chapter)"] < other_threshold]
    df = df[df["Distribution (ICD-10 chapter)"] >= other_threshold]

    # Sort
    df = df.sort_values("Count (ICD-10 chapter)", ascending=False)

    # Create and append "other" column
    row_other = {"ICD-10 chapter": "other", "Name (ICD-10 chapter)": "other", "Count (ICD-10 chapter)": df_other["Count (ICD-10 chapter)"].sum(), "Distribution (ICD-10 chapter)": df_other["Distribution (ICD-10 chapter)"].sum()}
    df = df._append(row_other, ignore_index=True)

    # Save to csv
    df.to_csv('data_figure_S1.csv', sep=";", index=False)

df_raw = load_and_preprocess_charting()
#preprocess_scimagojr()
preprocess_figure_2(df_raw)
preprocess_figure_3(df_raw)
preprocess_figure_4(df_raw)
preprocess_figure_5(df_raw)
preprocess_figure_6(df_raw)
preprocess_figure_7(df_raw)
#preprocess_figure_S1(df_raw)