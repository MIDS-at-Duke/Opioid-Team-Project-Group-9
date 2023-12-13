"""
To impute the missing death data based on the state level mortality rate and population threshold.

Saves final dataset as mortality_corrected.parquet

refer to the mortality_correction_v2.ipynb for EDA and other details like how the population threshold was chosen.
"""

# importing libraries and setting default option
import pandas as pd

pd.set_option("mode.copy_on_write", True)

# reading the data files
df = pd.read_parquet("Data/processed/mortality.parquet")
population = pd.read_parquet("Data/processed/population.parquet")

# ------------------------------------------
# initial Cleaning
df = df[df["State"] != "AK"]  # dropping ALASKA since it is Out of Scope (OOS)
df = df[
    df["Cause"] != "Drug poisonings (overdose) Homicide (X85)"
]  # dropping this category since it has low counts
df = (
    df.dropna()
)  # dropping rows with missing values since they are very few and will be imputed later

# ------------------------------------------
# Merge with population data
combined = pd.merge(
    df,
    population,
    on=["County_Code", "Year"],
    how="left",
    validate="m:1",
    indicator=True,
)

# ------------------------------------------
# Clean the Merged Data
df2 = combined[
    [
        "State_y",
        "State_x",
        "County_x",
        "County_Code",
        "Year",
        "Cause",
        "Deaths",
        "Population",
    ]
]

df2 = df2.rename(
    columns={"State_y": "State", "State_x": "State_Code", "County_x": "County"}
)

# ------------------------------------------
# calculating Mortality Rate (County Level)
df3 = df2.copy()
df3["Mortality_Rate"] = df3["Deaths"] / df3["Population"]

# ------------------------------------------
# Mortality Rate (State Level)

# aggregate at state-cause level
df4 = (
    df3.groupby(["State", "State_Code", "Year", "Cause"])
    .agg({"Deaths": "sum", "Population": "sum"})
    .reset_index()
)

# dropping other categories due to low counts (refer to ipynb file for details)
df4 = df4[df4["Cause"] == "Drug poisonings (overdose) Unintentional (X40-X44)"]

# clacualting mortality rate
df4["State_Mortality_Rate"] = df4["Deaths"] / df4["Population"]

# ------------------------------------------
# Creating a list of State-Counties from the POPULATION dataset
st_county = population[["State", "County", "County_Code", "Year"]].drop_duplicates()

# ------------------------------------------
# Merging State Mortality Rate with State-County list
master = pd.merge(st_county, df4, on=["State", "Year"], how="left", indicator=True)

# dropping NA rows since we have no state level data for them
master = master[master["_merge"] == "both"]

# Cleaning the merged data
master_2 = master[
    [
        "State",
        "State_Code",
        "County",
        "County_Code",
        "Year",
        "Cause",
        "State_Mortality_Rate",
    ]
]

# ------------------------------------------
# merge with the county level data
df5 = pd.merge(
    master_2,
    df3,
    on=["State", "State_Code", "County", "County_Code", "Year", "Cause"],
    how="left",
    indicator=True,
    validate="1:1",
)

# ------------------------------------------
# Remap with population data to get county population
df6 = pd.merge(
    df5,
    population[["County_Code", "Year", "Population"]],
    on=["County_Code", "Year"],
    how="left",
    validate="m:1",
    indicator="merge2",
)


# ------------------------------------------
def new_death(row):
    """Function to Calcuate the deaths in county using the State Mortality Rate and County Population
    if the deaths are missing in the original dataset.
    Max value is limited to 9 since we know that it can't be 10 or more"""

    if pd.isna(row["Deaths"]):
        return min(int(row["Population_y"] * row["State_Mortality_Rate"]), 9)
    else:
        return row["Deaths"]


# ------------------------------------------
# filtering for Counties with population threshold to control level of missing data that will be imputed

population_threshold = 50000  # <-------------------Change this later if required

# dropping counties with population less than the threshold
df7 = df6[df6["Population_y"] >= population_threshold]

# ------------------------------------------
# calautating the Final Deaths by using the new_death function
df7["Deaths_2"] = df7.apply(new_death, axis=1)

# ------------------------------------------
# Cleaning the dataset
df8 = df7[
    [
        "State",
        "State_Code",
        "County",
        "County_Code",
        "Year",
        "Cause",
        "Deaths_2",
        "Population_y",
    ]
]

df8 = df8.rename(columns={"Population_y": "Population", "Deaths_2": "Deaths"})

# ------------------------------------------
# aggregate at County level
df9 = (
    df8.groupby(["State", "State_Code", "County", "County_Code", "Year"])
    .agg({"Deaths": "sum", "Population": "mean"})
    .reset_index()
)

# ------------------------------------------
# calculating Final Mortality Rate (County Level)
df9["Mortality_Rate"] = df9["Deaths"] / df9["Population"]

# ------------------------------------------
# Saving the Final Dataset
df9.to_parquet("Data/processed/mortality_corrected.parquet", index=False)
