"""
To generate the mortality plots,
Saves the outputs in the folder: 03_Plots/01_Mortality

Scroll to the state headers to adjust values if required
"""


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
mortality = pd.read_parquet("01_Data/02_Processed/03_Mortality_Final.parquet")

# ------------------------------#
# Global settings
# Mortality Multiplier
mort_mul = 100000
mortality["Mortality_mul"] = mortality["Mortality_Rate"] * mort_mul

# Global Setting for ylabels so that they are consistent across all plots
ylabels = f"Mortality per {mort_mul:_} Population"

# Path for Saving the plots
base_path = "03_Plots/01_Mortality/"

# ------------------------------#
# ------------------------------#
# Plotting functions


# Subset the dataset for the analysis
def prepare_data(
    dataset, test_state, control_states, policy_year, start_year, end_year
):
    # Filter states
    state_list = [test_state] + control_states
    sub_dataset = dataset[dataset["State_Code"].isin(state_list)]

    # Filter years
    sub_dataset = sub_dataset[
        (sub_dataset["Year"] >= start_year) & (sub_dataset["Year"] <= end_year)
    ]

    # Tagging for pre-post policy implementation and test-control
    sub_dataset["policy_implementation"] = sub_dataset["Year"] >= policy_year
    sub_dataset["State_Type"] = sub_dataset["State_Code"].apply(
        lambda x: "Test" if x == test_state else "Control"
    )

    return sub_dataset


# ------------------------------#


def plot_pre_post_policy_graph(dataset_in, test_state, policy_year, metric_column):
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))

    # Convert YEAR and metric_column to float64
    dataset = dataset_in.copy()  # Copy to avoid changing the original dataframe
    # dataset["YEAR"] = dataset["YEAR"].astype("float64")
    # dataset[metric_column] = dataset[metric_column].astype("float64")

    sns.regplot(
        data=dataset[
            (dataset["State_Code"] == test_state)
            & (dataset["policy_implementation"] == True)
        ],
        x="Year",
        y=metric_column,
        line_kws={"color": "red"},
        ax=ax,
        scatter=False,
    )

    sns.regplot(
        data=dataset[
            (dataset["State_Code"] == test_state)
            & (dataset["policy_implementation"] != True)
        ],
        x="Year",
        y=metric_column,
        line_kws={"color": "blue"},
        ax=ax,
        scatter=False,
    )

    ax.axvline(policy_year, ls="--", color="orange")

    plt.legend(
        handles=[
            mlines.Line2D([], [], color="blue", label="Pre-Policy"),
            mlines.Line2D([], [], color="red", label="Post-Policy"),
        ],
        loc="lower right",
    )

    plt.title(f"Pre-Post Policy Implementation Trend for Mortality: {test_state}")
    plt.ylabel(ylabels)

    plt.tight_layout()
    plt.savefig(base_path + f"pre_post_{test_state}.png")
    pass


# ------------------------------#


def plot_diff_in_diff_graph(dataset_in, test_state, policy_year, metric_column):
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))

    # Convert YEAR and metric_column to float64
    dataset = dataset_in.copy()  # Copy to avoid changing the original dataframe
    # dataset["YEAR"] = dataset["YEAR"].astype("float64")
    # dataset[metric_column] = dataset[metric_column].astype("float64")

    # Plotting for test state - pre-policy
    sns.regplot(
        data=dataset[
            (dataset["State_Type"] == "Test")
            & (dataset["policy_implementation"] != True)
        ],
        x="Year",
        y=metric_column,
        line_kws={"color": "blue"},
        ax=ax,
        scatter=False,
    )

    # Plotting for test state - post-policy
    sns.regplot(
        data=dataset[
            (dataset["State_Type"] == "Test")
            & (dataset["policy_implementation"] == True)
        ],
        x="Year",
        y=metric_column,
        line_kws={"color": "blue"},
        ax=ax,
        scatter=False,
    )

    # Plotting for control states - pre-policy
    sns.regplot(
        data=dataset[
            (dataset["State_Type"] == "Control")
            & (dataset["policy_implementation"] != True)
        ],
        x="Year",
        y=metric_column,
        line_kws={"color": "red"},
        ax=ax,
        scatter=False,
    )

    # Plotting for control states - post-policy
    sns.regplot(
        data=dataset[
            (dataset["State_Type"] == "Control")
            & (dataset["policy_implementation"] == True)
        ],
        x="Year",
        y=metric_column,
        line_kws={"color": "red"},
        ax=ax,
        scatter=False,
    )

    # Adding vertical line for policy year
    ax.axvline(policy_year, ls="--", color="orange")

    # Creating custom legend handles
    blue_line = mlines.Line2D([], [], color="blue", label="Test State")
    red_line = mlines.Line2D([], [], color="red", label="Control States")

    # Adding legends
    plt.legend(handles=[blue_line, red_line], loc="lower right")
    plt.title(f"Difference-in-Difference Analysis for Mortality: {test_state}")
    plt.ylabel(ylabels)

    plt.tight_layout()
    plt.savefig(base_path + f"diff_in_diff_{test_state}.png")
    pass


# ------------------------------#

# ------------------------------#
# plotting for states starts here

############# WA #############
# Enter the Test State Below
test_state = "WA"

# Enter list of states required below, Included the test state
control_states = ["OR", "WI", "NJ"]

# Year control variable
policy_year = 2012  # year the policy was implemented
start_year = 2008  # desired start year for analysis
end_year = 2015  # desired end year for analysis

mortality_plot = prepare_data(
    mortality, test_state, control_states, policy_year, start_year, end_year
)
plot_pre_post_policy_graph(mortality_plot, test_state, policy_year, "Mortality_mul")
plot_diff_in_diff_graph(mortality_plot, test_state, policy_year, "Mortality_mul")


############# FL #############
# Enter the Test State Below
test_state = "FL"

# Enter list of states required below, Included the test state
control_states = ["GA", "NC", "LA"]

# Year control variable
policy_year = 2010  # year the policy was implemented
start_year = 2007  # desired start year for analysis
end_year = 2013  # desired end year for analysis

mortality_plot = prepare_data(
    mortality, test_state, control_states, policy_year, start_year, end_year
)
plot_pre_post_policy_graph(mortality_plot, test_state, policy_year, "Mortality_mul")
plot_diff_in_diff_graph(mortality_plot, test_state, policy_year, "Mortality_mul")


############# TX #############
# Enter the Test State Below
test_state = "TX"

# Enter list of states required below, Included the test state
control_states = ["LA", "AR", "OK", "MS", "AL", "AZ", "NM"]

# Year control variable
policy_year = 2007  # year the policy was implemented
start_year = 2003  # desired start year for analysis
end_year = 2011  # desired end year for analysis

mortality_plot = prepare_data(
    mortality, test_state, control_states, policy_year, start_year, end_year
)
plot_pre_post_policy_graph(mortality_plot, test_state, policy_year, "Mortality_mul")
plot_diff_in_diff_graph(mortality_plot, test_state, policy_year, "Mortality_mul")
