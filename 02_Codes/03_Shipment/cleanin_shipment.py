
# Importing required packages
import pandas as pd
import numpy as np
import warnings

# Set default option and suppress warnings
pd.set_option("mode.copy_on_write", True)
warnings.simplefilter(action="ignore", category=FutureWarning)

# Load datasets
shipment = pd.read_parquet("../../Data/processed/shipment_eda.parquet")
fips_codes = pd.read_csv("../../Data/raw/county_fips.csv")

# Load additional datasets for merging
population = pd.read_parquet("../../Data/processed/population.parquet")
state_codes = pd.read_csv("../../Data/raw/us_states-ab.csv")

# Merge operation for shipment data with FIPS codes
shipment_fips = pd.merge(
    shipment,
    fips_codes[["BUYER_COUNTY", "BUYER_STATE", "countyfips"]],
    on=["BUYER_COUNTY", "BUYER_STATE"],
    how="left",
)

# Fill NaN values in countyfips and adjust format
shipment_fips["countyfips"] = (
    shipment_fips["countyfips"].fillna(0).astype(int).astype(str).str.zfill(5)
)
shipment_fips["countyfips"] = shipment_fips["countyfips"].replace("00000", np.nan)

# Drop rows with 'BUYER_STATE' as 'AR' due to 'Montgomery' name change
shipment_fips = shipment_fips[shipment_fips['BUYER_COUNTY'] != 'MONTGOMERY']

# Checking and grouping NaNs in FIPS codes
nan_fips = shipment_fips[shipment_fips["countyfips"].isna()]
nan_counts = (
    nan_fips.groupby(["BUYER_STATE", "BUYER_COUNTY"])
    .size()
    .reset_index(name="NaN_count")
)

# Merge with population data
population_state_code = pd.merge(
    population, state_codes, left_on="State", right_on="state", how="left"
)
population_state_code = population_state_code.drop(
    columns=["state", "abbrev", "State_Code"]
)
population_state_code.rename(columns={"code": "State_Code"}, inplace=True)

# Preprocessing for merging
shipment_fips["YEAR"] = shipment_fips["YEAR"].astype("Int64")
shipment_fips["BUYER_COUNTY"] = shipment_fips["BUYER_COUNTY"].str.upper().str.strip()
population_state_code["County"] = population_state_code["County"].str.upper().str.strip()
population_state_code["Population"] = population_state_code["Population"].astype("Int64")

# Final merge with population data
shipment_with_population = pd.merge(
    shipment_fips,
    population_state_code,
    left_on=["BUYER_STATE", "BUYER_COUNTY", "YEAR"],
    right_on=["State_Code", "County", "Year"],
    how="left",
)

# Drop redundant columns post-merge
final_shipment_data = shipment_with_population.drop(
    columns=["State", "County", "County_Code", "Year", "State_Code"]
)

# Filter dataset for years up to 2015 and handle NaN or zero populations
shipment_data_up_to_2015 = final_shipment_data[final_shipment_data["YEAR"] <= 2015]
nan_or_zero_population_up_to_2015 = shipment_data_up_to_2015[
    (shipment_data_up_to_2015["Population"].isna()) | (shipment_data_up_to_2015["Population"] == 0)
]
unique_nan_or_zero_population_up_to_2015 = (
    nan_or_zero_population_up_to_2015.drop_duplicates(
        subset=["BUYER_STATE", "BUYER_COUNTY", "YEAR"]
    )
)

# Filter out states with NaN or zero population
states_to_drop = unique_nan_or_zero_population_up_to_2015['BUYER_STATE'].unique()
filtered_shipment_data = shipment_data_up_to_2015[~shipment_data_up_to_2015['BUYER_STATE'].isin(states_to_drop)]

# Check for NaN values in all columns of the filtered dataset
nan_columns_exist = filtered_shipment_data.isna().any()

# Save the final filtered dataset to a parquet file
file_path = '../../Data/processed/shipment_corrected.parquet'
filtered_shipment_data.to_parquet(file_path)
