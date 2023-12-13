# Importing required packages
import pandas as pd
import numpy as np
import warnings

# Set default option and suppress warnings
pd.set_option("mode.copy_on_write", True)
warnings.simplefilter(action="ignore", category=FutureWarning)

# Load datasets
shipment = pd.read_parquet("01_Data/02_Processed/04_Shipment_Combined.parquet")
fips_codes = pd.read_csv("01_Data/01_Raw/county_fips.csv")

# Load additional datasets for merging
population = pd.read_parquet("01_Data/02_Processed/01_Population.parquet")
state_codes = pd.read_csv("01_Data/01_Raw/us_states-ab.csv")

# Merge operation for shipment data with FIPS codes
shipment_fips = pd.merge(
    shipment,
    fips_codes,
    on=["BUYER_COUNTY", "BUYER_STATE"],
    how="left",
)

# Fill NaN values in countyfips and adjust format
shipment_fips["countyfips"] = (
    shipment_fips["countyfips"].fillna(0).astype(int).astype(str).str.zfill(5)
)
shipment_fips["countyfips"] = shipment_fips["countyfips"].replace("00000", np.nan)

# Drop rows with NAs in countyfips
shipment_fips = shipment_fips.dropna(subset=["countyfips"])


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
population_state_code["County"] = (
    population_state_code["County"].str.upper().str.strip()
)
population_state_code["Population"] = population_state_code["Population"].astype(
    "Int64"
)

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

# Filter dataset for years up to 2015
final_shipment_data = final_shipment_data[final_shipment_data["YEAR"] <= 2015]

# Calculating the MME per capita
final_shipment_data["MME_Per_Capita"] = (
    final_shipment_data["MME"] / final_shipment_data["Population"]
)

# Save the final dataset to a parquet file
final_shipment_data.to_parquet("01_Data/02_Processed/05_Shipment_Final.parquet")
