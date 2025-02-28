import pandas as pd
from tabulate import tabulate
import statsmodels.api as smApi
import statsmodels.regression.linear_model as smReg
import numpy as np
from collections import Counter

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
    # Create a new column 'Authors_list' by splitting the "Authors" string by " and "
    df['Authors_list'] = df['Authors'].apply(lambda x: [a.strip() for a in x.split(" and ")] if isinstance(x, str) else [])

    print("Loaded %d articles" % (len(df.index)))
    return df

df_charting = load_and_preprocess_charting()

def additional_statistics_figure_2():
    """
    Calculates the slope and p-value
    for the regressions shown in Figure 2
    """

    # load figure 2 data
    #df = pd.read_csv("data_figure_2.csv", sep = ";")
    df = pd.read_csv("data_figure_2_submission_year.csv", sep = ";")

    # Example years corresponding to your data
    years = list(range(len(df["Year"])))

    # Adding a column of ones to include an intercept in the model
    X = smApi.add_constant(years)

    model = smReg.OLS(df["Count (Non-COVID-19-related)"]+ df["Count (COVID-19-related)"], X).fit()
    print("Total all [2018-2021] | Slope: %.3f, p-value: %.5f" % (model.params.iloc[1], model.pvalues.iloc[1]))

    model = smReg.OLS(df["Count (Non-COVID-19-related)"], X).fit()
    print("Total non COVID [2018-2021] | Slope: %.3f, p-value: %.5f" % (model.params.iloc[1], model.pvalues.iloc[1]))

    model = smReg.OLS(df["Normalized (Non-COVID-19-related)"]+ df["Normalized (COVID-19-related)"], X).fit()
    print("Normalized all [2018-2022] | Slope: %.3f, p-value: %.5f" % (model.params.iloc[1], model.pvalues.iloc[1]))

    model = smReg.OLS(df["Normalized (Non-COVID-19-related)"], X).fit()
    print("Normalized non COVID [2018-2022] | Slope: %.3f, p-value: %.5f" % (model.params.iloc[1], model.pvalues.iloc[1]))

additional_statistics_figure_2()

def calculate_region_contribution(df):
    """
    Calculates contributions per country and the EUs contribution
    """
    def filter_only_single_data_origin(row):
        origin_list = row['Data origin_list']
        origin = origin_list[0]
        return len(origin_list) == 1 and origin != "various"

    # Remove records with more than one data origin
    df = df[df.apply(filter_only_single_data_origin, axis=1)]
    total_articles = len(df.index)

    # Count occurrences in each specific column
    first_author_counts = df['First author'].value_counts().reset_index()
    first_author_counts.columns = ['Country', 'Count (First author)']
    data_origin_counts = df['Data origin'].value_counts().reset_index()
    data_origin_counts.columns = ['Country', 'Count (Data origin)']

    # Merge the DataFrames on 'Country'
    df = pd.merge(first_author_counts, data_origin_counts, on='Country', how='outer')

    # Read external CSV with total number of articles published
    auxiliary_data = \
    pd.read_excel("auxiliary_data/Country_information.xlsx", sheet_name='Country_information', skiprows=0)[
        ["Country", "Name (Country)", "Region (Country)"]]
    df = pd.merge(df, auxiliary_data, on='Country', how='outer')

    # Fill missing values with 0
    df.fillna(0, inplace=True)

    # Convert float counts to integers
    df['Count (First author)'] = df['Count (First author)'].astype(int)
    df['Count (Data origin)'] = df['Count (Data origin)'].astype(int)

    # Calculate distribution
    df["Distribution (First author)"] = df["Count (First author)"] * 100 / df["Count (First author)"].sum()
    df["Distribution (Data origin)"] = df["Count (Data origin)"] * 100 / df["Count (Data origin)"].sum()

    print(tabulate(df, headers='keys', tablefmt='psql'))

    """ 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Continental Europe contribution
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    df = df[df["Region (Country)"] == 'Continental Europe']
    count_first_author = df["Count (First author)"].sum()
    count_data_origin = df["Count (Data origin)"].sum()
    relative_first_author = df["Distribution (First author)"].sum()
    relative_data_origin = df["Distribution (Data origin)"].sum()
    print(relative_data_origin)

    print("EU First author: %.2f (%d of %d), EU Data origin: %.2f (%d of %d)" % (relative_first_author, count_first_author, total_articles, relative_data_origin, count_data_origin, total_articles))

#calculate_region_contribution(df_charting)

def additional_statistics_figure_4():
    """
    Prints values to calculate the Data origin
    per 1000 citable documents for entire regions
    """
    df = pd.read_csv("data_figure_4.csv", sep=";")

    print(f"Global: Mean Score: {df['Data origin per 1000 citable documents'].mean():.3f}, Standard Deviation: {df['Data origin per 1000 citable documents'].std():.3f}")

    # Group by region and calculate the required statistics
    df_regions = df.groupby('Region (Country)')['Data origin per 1000 citable documents'].agg(['mean', 'std', list])

    # Print the results nicely formatted
    for index, row in df_regions.iterrows():
        print(f"Region: {index}\nMean Score: {row['mean']:.3f}, Standard Deviation: {row['std']:.3f}, Scores List: {row['list']}")

#additional_statistics_figure_4()

def calculate_first_and_senior_author_overlap(df):
    """
    Calculates fraction of articles where
    first and senior author are from same country
    """
    def filter_same_author_origin(row):
        first_author_origin = row['First author']
        senior_author_origin = row['Senior author']
        return first_author_origin == senior_author_origin or senior_author_origin == ""

    # Number of articles
    total_count = len(df.index)

    # Remove records with distinct first and senior author
    df = df[df.apply(filter_same_author_origin, axis=1)]

    # Number of articles with first and senior from same country
    same_author_origin_count = len(df.index)

    print("Articles with same author origin: %.2f (n=%d)" % ((same_author_origin_count * 100 / total_count), same_author_origin_count))

#calculate_first_and_senior_author_overlap(df_charting)

def author_and_data_origin(df):
    """
    Calculates:
    1) Number of articles with single data origin
    2) Number of different first author origins for 1)
    3) Number of different data origins for 1)
    4) Number of articles for which first author and data origin overlap for 1)
    """
    def filter_only_single_data_origin(row):
        origin_list = row['Data origin_list']
        origin = origin_list[0]
        return len(origin_list) == 1 and origin != "various"

    def filter_domestic_use(row):
        return row['Data origin'] == row["First author"]

    # Total numbers of articles
    total_count = len(df.index)

    # Filter single origin only
    df_single_origin = df[df.apply(filter_only_single_data_origin, axis=1)]

    # Count of articles with single origin
    single_origin_count = len(df_single_origin.index)

    # Unique origins:
    first_author_origin, data_origin = df_single_origin["First author"].unique(), df_single_origin["Data origin"].unique()

    print("Articles with single data origin: %.2f (n=%d)" % ((single_origin_count * 100 / total_count), single_origin_count))
    print("Unique first author origin %d" % len(first_author_origin))
    print("Unique data origin %d" % len(data_origin))

    # Filter articles where first author and data originate from the same country
    df_domestic = df_single_origin[df_single_origin.apply(filter_domestic_use, axis=1)]

    # Count of articles with same author and data origin
    same_author_data_origin_count = len(df_domestic.index)

    print("Articles with same author and data origin: %.1f (n=%d)" % ((same_author_data_origin_count * 100 / single_origin_count), same_author_data_origin_count))

    df_multiple_origin = df[~df.apply(filter_only_single_data_origin, axis=1)]
    first_author_counts = df_multiple_origin['First author'].value_counts().reset_index()
    first_author_counts.columns = ['Country', 'Count (First author)']

    df_multiple_origin = df_multiple_origin.explode("Data origin_list")
    data_counts = df_multiple_origin['Data origin_list'].value_counts().reset_index()
    data_counts.columns = ['Country', 'Count (Data origin)']

    df_multiple_origin_counts = pd.merge(first_author_counts, data_counts, on='Country', how='outer')

    print("Statistics for articles for which first authos and data origin do not overlap:")
    print(tabulate(df_multiple_origin_counts, headers='keys', tablefmt='psql'))

#author_and_data_origin(df_charting)

def authors_per_income_group(df):
    """
    Calculates the number of first authors
    for each World Bank income group
    """
    auxiliary_data = pd.read_excel("auxiliary_data/Country_information.xlsx", sheet_name='Country_information', skiprows=0)[["Country", "Name (Country)", "World Bank income group"]]
    df = pd.merge(df, auxiliary_data, left_on='First author', right_on="Country", how='outer')

    grouped_data = df.groupby("World Bank income group").count()['First author']
    print(grouped_data)

#authors_per_income_group(df_charting)

def crossborder_and_domestic_use(df):
    """
    Calculates number of articles assigned to
    domestic data usage as well as crossborder usage
    """
    def filter_crossborder_articles(row):
        origin_list = row['Data origin_list']
        origin = origin_list[0]
        return (len(origin_list) > 1 or origin == "various" or origin != row["First author"])

    # Provide stats on number of articles
    df_crossborder = df[df.apply(filter_crossborder_articles, axis=1)]
    df_domestic = df[~df.apply(filter_crossborder_articles, axis=1)]
    count_crossborder, count_domestic, count_total = len(df_crossborder.index), len(df_domestic.index), len(df.index)

    print("Crossborder articles: %.2f (n=%d); domestic only articles: %.2f (n=%d)" % (count_crossborder *100/count_total, count_crossborder, count_domestic*100/count_total, count_domestic))

#crossborder_and_domestic_use(df_charting)

def cross_border_flows(df):
    """
    Calculates crossborder data flows
    """
    def filter_crossborder_articles(row):
        return len(row['Data origin_list']) > 1 or row['Data origin_list'][0] != row["First author"] or row['Data origin_list'][0] == "various"

    def filter_various(row):
        return row['Data origin_list'] != "various"

    def filter_crossborder_origin(row):
        return row['Data origin_list'] != row["First author"]

    df_crossborder = df[df.apply(filter_crossborder_articles, axis=1)]

    df_crossborder = df_crossborder.explode('Data origin_list')
    df_crossborder = df_crossborder[df_crossborder.apply(filter_various, axis=1)]
    df_crossborder = df_crossborder[df_crossborder.apply(filter_crossborder_origin, axis=1)]

    print("Crossborder flows: %d" % len(df_crossborder.index))

#cross_border_flows(df_charting)

def custodian_usage(df):
    """
    Calculates fractions of article using
    common data sources and provides tables
    to also calculate this per year
    """
    def filter_used_custodian(row):
        # Check if any custodian in the row's list is in the common data sources
        return any(custodian in common_data_sources for custodian in row['Data source_list'])

    # Read external CSV with list of common sources
    auxiliary_data = pd.read_excel("auxiliary_data/Data_source_information.xlsx", sheet_name='Data_source_information', skiprows=0, dtype=str)
    common_data_sources = auxiliary_data["Data source"].unique()

    df_custodian = df[df.apply(filter_used_custodian, axis=1)]

    count_custodian = len(df_custodian.index)
    count_total = len(df.index)

    print("Articles using common data source: %.1f (n=%d)" % (count_custodian * 100 / count_total, count_custodian))

    count_source_per_year = df_custodian.groupby('Publishing year').count()
    count_total_per_year = df.groupby('Publishing year').count()

    print(count_source_per_year)
    print(count_total_per_year)

#custodian_usage(df_charting)

def articles_assigned_to_icd(df):
    """
    Calculates how many articles are assigned to a specific disease
    """
    def filter_only_assigned_ICD_chapter(row):
        return row['ICD-10 chapter'] != ""

    # Remove records not assigned to a chapter
    df_filtered = df[df.apply(filter_only_assigned_ICD_chapter, axis=1)]

    print("Paper assigned to an ICD-10 chapter: %.2f (n=%d)" % ((len(df_filtered.index)/len(df.index)), len(df_filtered.index)))

#articles_assigned_to_icd(df_charting)

def source_usage_for_specific_disease(df, disease, source):
    """
    Calculates how many articles resarching
    a given disease use data from a given source
    """
    def filter_source(row):
        # Check if any source in the row's list is in the common data sources
        return source in  row['Data source_list']

    df = df[df["ICD-10 chapter"] == disease]
    count_total = len(df.index)

    df = df[df.apply(filter_source, axis=1)]
    count_filtered = len(df.index)

    print("Articles on chapter %s using %s: %.1f (n=%d(/%d))" % (disease, source, count_filtered * 100 / count_total, count_filtered, count_total))

#source_usage_for_specific_disease(df_charting, "2", "Flatiron Health")
#source_usage_for_specific_disease(df_charting, "4", "Optum")
#source_usage_for_specific_disease(df_charting, "5", "South London and Maudsley NHS Foundation Trust")

def datatype_distribution(df):

    def filter_used_custodian(row):
        # Check if any custodian in the row's list is in the common data sources
        return any(custodian in common_data_sources for custodian in row['Data source_list'])

    def analyse_datatype_usage(df):
        total_articles = len(df.index)
        only_healthcare_data = len(df[(df["Research data"] == "No") & (df["Healthcare data"] == "Yes")].index)
        only_research_data = len(df[(df["Research data"] == "Yes") & (df["Healthcare data"] == "No")].index)
        both = len(df[(df["Research data"] == "Yes") & (df["Healthcare data"] == "Yes")].index)
        print("Articles only using healthcare data: %.1f (%d of %d)" % (only_healthcare_data*100/total_articles, only_healthcare_data, total_articles))
        print("Articles only using research data: %.1f (%d of %d)" % (only_research_data * 100 / total_articles, only_research_data, total_articles))
        print("Articles using both datatypes: %.1f (%d of %d)" % (both * 100 / total_articles, both, total_articles))

    # Read external CSV with list of common sources
    auxiliary_data = pd.read_excel("auxiliary_data/Data_source_information.xlsx", sheet_name='Data_source_information', skiprows=0, dtype=str)
    common_data_sources = auxiliary_data["Data source"].unique()
    df_custodian = df[df.apply(filter_used_custodian, axis=1)]
    df_no_custodian = df[~df.apply(filter_used_custodian, axis=1)]

    print("\n### For all articles: ###")
    analyse_datatype_usage(df)
    print("\n### For articles using common data source: ###")
    analyse_datatype_usage(df_custodian)
    print("\n### For articles NOT using common data source: ###")
    analyse_datatype_usage(df_no_custodian)

#datatype_distribution(df_charting)

def unique_author_fraction_per_source(df, other_threshold=10):
    def filter_only_specific_source(row):
        return row['Data source_list'] != "Multiple" and row['Data source_list'] != "Not precisely specified"


    # Explode the Data source_list column so that each row represents a single data source
    df = df.explode('Data source_list')

    # Remove records not assigned to a specific source
    df = df[df.apply(filter_only_specific_source, axis=1)]

    # Group by data source and compute:
    # - count: number of rows (papers) referencing the source
    # - Authors: total number of author mentions (summing the lengths of the authors list per row)
    # - Unique authors: count of unique author names across all rows for that source
    grouped = df.groupby('Data source_list').agg(
        count=('Data source_list', 'size'),
        Authors=('Authors_list', lambda series: sum(len(authors) for authors in series)),
        Unique_authors=('Authors_list', lambda series: len({author for authors in series for author in authors})),
    ).reset_index()
    grouped['Unique_author_fraction'] = grouped["Unique_authors"] / grouped["Authors"]

    # Filter out sources with fewer than other_threshold records
    grouped = grouped[grouped['count'] >= other_threshold]

    # Rename the grouping column to "Data source" for the final output
    grouped.rename(columns={'Data source_list': 'Data source'}, inplace=True)

    # Optionally, merge with external auxiliary data if needed.
    # The auxiliary file might contain additional info (e.g. total articles published).
    # If you only want the three columns ("Data source", "Authors", "Unique authors"),
    # the merge is optional.
    auxiliary_data = pd.read_excel(
        "auxiliary_data/Data_source_information.xlsx",
        sheet_name='Data_source_information',
        skiprows=0,
        dtype=str
    )
    grouped = pd.merge(grouped, auxiliary_data, on='Data source', how='left')

    # Select only the columns for output: "Data source", "Authors", and "Unique authors"
    output_columns = ['Data source', 'Unique_authors', 'Authors', 'Unique_author_fraction', 'Gini_index']
    # Save to xlsx
    with pd.ExcelWriter('stats_unique_authors.xlsx', engine="openpyxl", mode="a", if_sheet_exists='replace') as writer:
        grouped[output_columns].to_excel(writer, sheet_name='stats_unique_authors', index=False)

#unique_author_fraction_per_source(df_charting, 10)

def calculate_average_delay(df):

    def filter_has_complete_date_info(row):
        required_keys = [
            "Submission year",
            "Submission month",
            "Publishing year",
            "Publishing month",
        ]
        return all(str(row[key]).lower() not in ("na", "") for key in required_keys)

        # Apply the filter to keep only rows with complete date information.
    df = df[df.apply(filter_has_complete_date_info, axis=1)]
    print(f"Complete date information available for {len(df.index)} articles")

    def calculate_average_delay(sub_df):
        """
        Given a dataframe with the following columns:
            Submission_year, Submission_month, Publication_year, Publication_month,
        this function computes the delay in months for each row and returns the average delay.
        """
        # Convert the date columns to integers.
        sub_year = sub_df["Submission year"].astype(int)
        sub_month = sub_df["Submission month"].astype(int)
        pub_year = sub_df["Publishing year"].astype(int)
        pub_month = sub_df["Publishing month"].astype(int)

        # Calculate the delay in months:
        # (publication_year - submission_year) * 12 + (publication_month - submission_month)
        delays = (pub_year - sub_year) * 12 + (pub_month - sub_month)
        return delays.mean()

    # --- 5. Calculate and print the overall average delay ---
    overall_avg = calculate_average_delay(df)
    print(f"Overall average delay (months): {overall_avg:.2f}")

    # --- 6. Calculate and print the delay for COVID-19 research = "y" ---
    covid_y = df[df["COVID-19 research"].astype(str).str.lower() == "yes"]
    covid_y_avg = calculate_average_delay(covid_y)
    print(f"Average delay (months) for COVID-19 research (y): {covid_y_avg:.2f}")

    # --- 7. Calculate and print the delay for COVID-19 research = "n" ---
    covid_n = df[df["COVID-19 research"].astype(str).str.lower() == "no"]
    covid_n_avg = calculate_average_delay(covid_n)
    print(f"Average delay (months) for COVID-19 research (n): {covid_n_avg:.2f}")

calculate_average_delay(df_charting)

# DELETE ME - temporary!
def add_time_to_publication():
    # Define a helper function to filter rows with complete date information.
    def calc_delay(row):
        required_keys = [
            "Submission year",
            "Submission month",
            "Publishing year",
            "Publishing month",
        ]
        # Check if any required field is missing, empty, or marked as "na".
        for key in required_keys:
            if pd.isnull(row[key]) or str(row[key]).strip().lower() in ("na", ""):
                return np.nan  # Return NaN if incomplete info.

        try:
            # Convert date fields to integers.
            sub_year = int(row["Submission year"])
            sub_month = int(row["Submission month"])
            pub_year = int(row["Publishing year"])
            pub_month = int(row["Publishing month"])

            # Calculate delay in months.
            delay = (pub_year - sub_year) * 12 + (pub_month - sub_month)
            return delay
        except Exception as e:
            # In case of any conversion errors, leave the value as NaN.
            return np.nan

    # load data
    chart_file = "charting_results/results_20250214.csv"
    df = pd.read_csv(chart_file, dtype=str, sep=";")

    df["Time-to-Publication"] = df.apply(calc_delay, axis=1)

    df.to_csv("charting_results/results_20250214_with_TtP.csv", sep =";", index=False)

#add_time_to_publication()