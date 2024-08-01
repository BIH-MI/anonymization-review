import pandas as pd
from tabulate import tabulate
import statsmodels.api as smApi
import statsmodels.regression.linear_model as smReg

def load_and_preprocess_charting():

    # load data
    chart_file = "charting_results/charting_results_20240620.csv"
    df = pd.read_csv(chart_file, dtype=str, sep=";")

    # Fill empty cells with empty string
    df = df.fillna('')

    # Remove excluded articles
    df = df[df['Include'] == 'Yes']

    # split 1:n fields
    df["Data source_list"] = df.apply(lambda row: [label.lstrip() for label in row["Data source"].split(",")], axis=1)
    df["Data origin_list"] = df.apply(lambda row: row["Data origin"].replace(" ", "").strip().split(","), axis=1)

    print("Loaded %d articles" % (len(df.index)))
    return df

df_charting = load_and_preprocess_charting()

def additional_statistics_figure_1():
    """
    Calculates the slope and p-value
    for the regressions shown in Figure 2
    """

    # load figure 2 data
    df = pd.read_excel("data_figures.xlsx", sheet_name="data_figure_1", engine="openpyxl")

    # Example years corresponding to your data
    years = list(range(len(df["Year"])))

    # Adding a column of ones to include an intercept in the model
    X = smApi.add_constant(years)

    model = smReg.OLS(df["Normalized (Non-COVID-19-related)"]+ df["Normalized (COVID-19-related)"], X).fit()
    print("Normalized all [2018-2022] | Slope: %.3f, p-value: %.5f" % (model.params[1], model.pvalues[1]))

    model = smReg.OLS(df["Normalized (Non-COVID-19-related)"], X).fit()
    print("Normalized non COVID [2018-2022] | Slope: %.3f, p-value: %.5f" % (model.params[1], model.pvalues[1]))

#additional_statistics_figure_2()

def calculate_EU_contribution(df):
    """
    Calculates contributions per country and the EUs contribution
    """
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
    EU contribution
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    df = df[df["Region (Country)"] == 'European Union']
    count_first_author = df["Count (First author)"].sum()
    count_data_origin = df["Count (Data origin)"].sum()
    relative_first_author = df["Distribution (First author)"].sum()
    relative_data_origin = df["Distribution (Data origin)"].sum()
    print(relative_data_origin)

    print("EU First author: %.2f (n=%d), EU Data origin: %.2f (n=%d)" % (relative_first_author, count_first_author,  relative_data_origin, count_data_origin))

#calculate_EU_contribution(df_charting)

def additional_statistics_figure_2():
    """
    Prints values to calculate the Data origin
    per 1000 citable documents for entire regions
    """
    df = pd.read_excel("data_figures.xlsx", sheet_name="data_figure_2", engine="openpyxl")

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

    print("Articles with same author and data origin: %.2f (n=%d)" % ((same_author_data_origin_count * 100 / single_origin_count), same_author_data_origin_count))

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
        return len(origin_list) > 1 or origin == "various" or origin != row["First author"]

    # Provide stats on number of articles
    df_crossborder = df[df.apply(filter_crossborder_articles, axis=1)]
    df_domestic = df[~df.apply(filter_crossborder_articles, axis=1)]
    count_crossborder, count_domestic, count_total = len(df_crossborder.index), len(df_domestic.index), len(df.index)

    print(count_total)
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

    # Read external CSV with total number of articles published
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