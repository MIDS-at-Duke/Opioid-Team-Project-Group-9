# Import required packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import matplotlib.lines as mlines

# Set default option
pd.set_option("mode.copy_on_write", True)
warnings.simplefilter(action="ignore", category=FutureWarning)

# Load the Datasets
mortality = pd.read_parquet("/Users/robintitus/Desktop/PDS/Dec 12/Opioid-Team-Project-Group-9/Data/processed/mortality_corrected.parquet")
shipment = pd.read_parquet("/Users/robintitus/Desktop/PDS/Dec 12/Opioid-Team-Project-Group-9/Data/processed/shipment_corrected.parquet")

# Control vars state setup
test_state = 'FL'
control_states = ['GA', 'NC', 'LA']

# Control vars year setup
policy_year = 2012
start_year = 2008
end_year = 2015

# Subset datasets
def prepare_data(dataset, test_state, control_states, policy_year, start_year, end_year):
    # Filter states
    state_list = [test_state] + control_states
    dataset = dataset[dataset["BUYER_STATE"].isin(state_list)]

    # Filter years
    dataset = dataset[(dataset["YEAR"] >= start_year) & (dataset["YEAR"] <= end_year)]

    # Tag for pre-post policy implementation and test-control
    dataset["policy_implementation"] = dataset["YEAR"] >= policy_year
    dataset["State_Type"] = dataset["BUYER_STATE"].apply(lambda x: "Test" if x == test_state else "Control")

    return dataset

#Pre and Post Graphing func
def plot_pre_post_policy_graph(dataset, test_state, policy_year, metric_column):
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))

    # Convert YEAR and metric_column to float64
    dataset = dataset.copy()  # Copy to avoid changing the original dataframe
    dataset['YEAR'] = dataset['YEAR'].astype('float64')
    dataset[metric_column] = dataset[metric_column].astype('float64')

    sns.regplot(
        data=dataset[(dataset["BUYER_STATE"] == test_state) & (dataset["policy_implementation"] == True)],
        x="YEAR", y=metric_column, line_kws={"color": "red"}, ax=ax, scatter=False)

    sns.regplot(
        data=dataset[(dataset["BUYER_STATE"] == test_state) & (dataset["policy_implementation"] != True)],
        x="YEAR", y=metric_column, line_kws={"color": "blue"}, ax=ax, scatter=False)

    ax.axvline(policy_year, ls="--", color="orange")

    plt.legend(handles=[mlines.Line2D([], [], color="blue", label="Pre-Policy"),
                        mlines.Line2D([], [], color="red", label="Post-Policy")], loc="lower right")

    plt.title(f"Pre-Post Policy Implementation Shipment Trend for {test_state}")
    plt.ylabel(f"{metric_column} (Units)")

    plt.show()

#Diff in diff Graphing func
def plot_diff_in_diff_graph(dataset, test_state, policy_year, metric_column):
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))

    # Convert YEAR and metric_column to float64
    dataset = dataset.copy()  # Copy to avoid changing the original dataframe
    dataset['YEAR'] = dataset['YEAR'].astype('float64')
    dataset[metric_column] = dataset[metric_column].astype('float64')

    # Plotting for test state - pre-policy
    sns.regplot(
        data=dataset[(dataset["State_Type"] == "Test") & (dataset["policy_implementation"] != True)],
        x="YEAR", y=metric_column, line_kws={"color": "blue"}, ax=ax, scatter=False)

    # Plotting for test state - post-policy
    sns.regplot(
        data=dataset[(dataset["State_Type"] == "Test") & (dataset["policy_implementation"] == True)],
        x="YEAR", y=metric_column, line_kws={"color": "blue"}, ax=ax, scatter=False)

    # Plotting for control states - pre-policy
    sns.regplot(
        data=dataset[(dataset["State_Type"] == "Control") & (dataset["policy_implementation"] != True)],
        x="YEAR", y=metric_column, line_kws={"color": "red"}, ax=ax, scatter=False)

    # Plotting for control states - post-policy
    sns.regplot(
        data=dataset[(dataset["State_Type"] == "Control") & (dataset["policy_implementation"] == True)],
        x="YEAR", y=metric_column, line_kws={"color": "red"}, ax=ax, scatter=False)

    # Adding vertical line for policy year
    ax.axvline(policy_year, ls="--", color="orange")

    # Creating custom legend handles
    blue_line = mlines.Line2D([], [], color="blue", label="Test State")
    red_line = mlines.Line2D([], [], color="red", label="Control States")

    # Adding legends
    plt.legend(handles=[blue_line, red_line], loc="lower right")
    plt.title(f"Difference-in-Difference Analysis for {test_state}")
    plt.ylabel(f"{metric_column} (Units)")

    plt.show()

#Call functions
shipment = prepare_data(shipment, test_state, control_states, policy_year, start_year, end_year)
plot_pre_post_policy_graph(shipment, test_state, policy_year, 'MME')
plot_diff_in_diff_graph(shipment, test_state, policy_year, 'MME')
