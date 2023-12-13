"""
To generate the shipment plots,
Saves the outputs in the folder: 03_Plots/02_Shipment

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
shipment = pd.read_parquet("01_Data/02_Processed/05_Shipment_Final.parquet")

# ------------------------------#
# Global settings

# Shipement Multiplier
ship_mul = 100000  # <---------Adjust this if required
shipment["MME_mul"] = shipment["MME_Per_Capita"] * ship_mul

# Global Setting for ylabels so that they are consistent across all plots
ylabels = f"MME Shipped per {ship_mul:,} Population"

# Path for Saving the plots
base_path = "03_Plots/02_Shipment/"
# ------------------------------#


# ------------------------------#
# Plotting functions


# Subset the dataset for the analysis
def prepare_data(
    dataset, test_state, control_states, policy_year, start_year, end_year
):
    # Filter states
    state_list = [test_state] + control_states
    sub_dataset = dataset[dataset["BUYER_STATE"].isin(state_list)]

    # Filter years
    sub_dataset = sub_dataset[
        (sub_dataset["YEAR"] >= start_year) & (sub_dataset["YEAR"] <= end_year)
    ]

    # Tagging for pre-post policy implementation and test-control
    sub_dataset["policy_implementation"] = sub_dataset["YEAR"] >= policy_year
    sub_dataset["State_Type"] = sub_dataset["BUYER_STATE"].apply(
        lambda x: "Test" if x == test_state else "Control"
    )

    return sub_dataset


def plot_pre_post_policy_graph(dataset_in, test_state, policy_year, metric_column):
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))

    # Convert YEAR and metric_column to float64
    dataset = dataset_in.copy()  # Copy to avoid changing the original dataframe
    dataset["YEAR"] = dataset["YEAR"].astype("float64")
    dataset[metric_column] = dataset[metric_column].astype("float64")

    sns.regplot(
        data=dataset[
            (dataset["BUYER_STATE"] == test_state)
            & (dataset["policy_implementation"] == True)
        ],
        x="YEAR",
        y=metric_column,
        line_kws={"color": "red"},
        ax=ax,
        scatter=False,
    )

    sns.regplot(
        data=dataset[
            (dataset["BUYER_STATE"] == test_state)
            & (dataset["policy_implementation"] != True)
        ],
        x="YEAR",
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

    plt.title(f"Pre-Post Policy Implementation Trend for Shipment: {test_state}")
    plt.ylabel(ylabels)
    plt.tight_layout()
    plt.savefig(base_path + f"pre_post_{test_state}.png")
    pass


def plot_diff_in_diff_graph(dataset_in, test_state, policy_year, metric_column):
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))

    # Convert YEAR and metric_column to float64
    dataset = dataset_in.copy()  # Copy to avoid changing the original dataframe
    dataset["YEAR"] = dataset["YEAR"].astype("float64")
    dataset[metric_column] = dataset[metric_column].astype("float64")

    # Plotting for test state - pre-policy
    sns.regplot(
        data=dataset[
            (dataset["State_Type"] == "Test")
            & (dataset["policy_implementation"] != True)
        ],
        x="YEAR",
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
        x="YEAR",
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
        x="YEAR",
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
        x="YEAR",
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
    plt.title(f"Difference-in-Difference Analysis for Shipment: {test_state}")
    plt.ylabel(ylabels)

    plt.tight_layout()

    plt.savefig(base_path + f"diff_in_diff_{test_state}.png")
    pass


# ------------------------------#
# plotting for states starts here

############# WA #############
# Enter the Test State Below
test_state = "WA"

# Enter list of states required below, Included the test state
control_states = ["MN", "OR", "ID"]

# Year control variable
policy_year = 2012  # year the policy was implemented
start_year = 2008  # desired start year for analysis
end_year = 2015  # desired end year for analysis

# ---
shipment_plot = prepare_data(
    shipment, test_state, control_states, policy_year, start_year, end_year
)

plot_pre_post_policy_graph(shipment_plot, test_state, policy_year, "MME_mul")
plot_diff_in_diff_graph(shipment_plot, test_state, policy_year, "MME_mul")

# ------------------------------------------------------------------------------

############# FL #############

# Enter the Test State Below
test_state = "FL"

# Enter list of states required below, Included the test state
control_states = ["GA", "SC", "AL"]

# Year control variable
policy_year = 2010  # year the policy was implemented
start_year = 2006  # desired start year for analysis
end_year = 2013  # desired end year for analysis

# ---
shipment_plot = prepare_data(
    shipment, test_state, control_states, policy_year, start_year, end_year
)

plot_pre_post_policy_graph(shipment_plot, test_state, policy_year, "MME_mul")
plot_diff_in_diff_graph(shipment_plot, test_state, policy_year, "MME_mul")

# ------------------------------------------------------------------------------
