# Impoting required packages
import pandas as pd
import numpy as np
import zipfile

# setting default option
pd.set_option("mode.copy_on_write", True)

# ------------------------------------------
# reading the files
z = zipfile.ZipFile("01_Data/01_Raw/raw_mortality.zip")
fips = pd.read_csv("01_Data/01_Raw/county_fips.csv")

# extracting list of files from Zip folder to read
# using files starting with "Underlying" so as to ignore system files
file_list = sorted([f for f in z.namelist() if f.startswith("Underlying")])


# ------------------------------------------
# read data selected files and append to list
df_list = []
for file in file_list:
    # read individual files
    df_temp = pd.read_csv(z.open(file), sep="\t")

    # drop the notes columns and remove rows with null values in County column
    df_temp.drop(columns=["Notes"], inplace=True)
    df_temp.dropna(subset=["County"], inplace=True)

    # add the cleaned temp Df to the main list
    df_list.append(df_temp)

# ------------------------------------------
# create the dataframe
df = pd.concat(df_list, ignore_index=True)

# ------------------------------------------
# Correcting Data Types for columns
df2 = df.copy()

# Pad county code with 0 for consistency with other data sets
df2["County Code"] = df2["County Code"].astype(int).astype(str).str.zfill(5)

# padding fips to have consistency
fips["countyfips"] = fips["countyfips"].astype(str).str.zfill(5)

# Convert Year to Int
df2["Year"] = df2["Year"].astype(int)

# Convert Deaths to Int
df2["Deaths"] = df2["Deaths"].replace("Missing", np.nan)
df2["Deaths"] = (
    df2["Deaths"].astype(float).astype("Int64")
)  # making it as int64 so that we retain null values for later analysis

# ------------------------------------------

# Store only the rows related drugs, modify this list later if required
required_causes = [
    "Drug poisonings (overdose) Unintentional (X40-X44)",
    "All other drug-induced causes",
    "Drug poisonings (overdose) Homicide (X85)",
    "Drug poisonings (overdose) Suicide (X60-X64)",
    "Drug poisonings (overdose) Undetermined (Y10-Y14)",
]

# ------------------------------------------------------
# create and optimize subset data
df3 = df2[df2["Drug/Alcohol Induced Cause"].isin(required_causes)]

# remove extra columns
df3.drop(columns=["Year Code", "Drug/Alcohol Induced Cause Code"], inplace=True)

# renaming columns
df3.rename(
    columns={"Drug/Alcohol Induced Cause": "Cause", "County Code": "County_Code"},
    inplace=True,
)

# ------------------------------------------------------
# mapping with fips for proper county names and state name
df4 = pd.merge(
    df3,
    fips,
    how="left",
    left_on="County_Code",
    right_on="countyfips",
    validate="m:1",
    indicator=True,
)

# --------------------------------------------------------
# Prepare final DF for saving
# select required colums
df5 = df4[["BUYER_STATE", "BUYER_COUNTY", "County_Code", "Year", "Cause", "Deaths"]]

# rename columns
df5 = df5.rename(columns={"BUYER_COUNTY": "County", "BUYER_STATE": "State"})

# ------------------------------------------
# Writing to Parquet
df5.to_parquet("01_Data/02_Processed/02_Mortality_Combined.parquet", index=False)
