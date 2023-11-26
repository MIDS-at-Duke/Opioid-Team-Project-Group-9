# importing pandas and setting default option
import pandas as pd

pd.set_option("mode.copy_on_write", True)

# reading the csv files
df = pd.read_csv("Data/raw/raw_population.txt", sep="\t")
fips = pd.read_csv("Data/raw/county_fips.csv")

# ------------------------------------------
# dropping the unnecessary columns
df1 = df.drop(columns=["Notes"])

# Dropping unnecessary rows
# 1.  removing the rows with na values generated due to Notes, using state column for reference
df1 = df1.dropna(subset=["State"])

# 2. Removing Alaska
df1 = df1[df1["State"] != "Alaska"]


# ------------------------------------------
# Correcting Data Types for columns
df2 = df1.copy()

# 1. Saving state code as padded string
df2["State Code"] = df2["State Code"].astype(int).astype(str).str.zfill(2)

# 2. Saving county code as padded string
df2["County Code"] = df2["County Code"].astype(int).astype(str).str.zfill(5)

# padding fips to have consistency
fips["countyfips"] = fips["countyfips"].astype(str).str.zfill(5)

# 3. Converting Year to Integer
df2["Yearly July 1st Estimates"] = df2["Yearly July 1st Estimates"].astype(int)

# 4. Converting Population to Integer
# replacing the missing values with 0 for now <-------------------Change this later if required
df2["Population"] = df2["Population"].replace("Missing", 0)
df2["Population"] = df2["Population"].astype(int)

# ------------------------------------------

# creating subset of data for analysis
df3 = df2.copy()

# rename columns
df3 = df3.rename(
    columns={
        "Yearly July 1st Estimates": "Year",
        "State Code": "State_Code",
        "County Code": "County_Code",
    }
)

# reorder columns
df3 = df3[
    [
        "State",
        "State_Code",
        "County",
        "County_Code",
        "Year",
        "Population",
    ]
]

# ------------------------------------------

# mapping with fips for proper county names
df4 = pd.merge(
    df3,
    fips,
    how="left",
    left_on="County_Code",
    right_on="countyfips",
    validate="m:1",
    indicator=True,
)

# ------------------------------------------

# correcting the county names where fips mapping failed
df4.loc[df4["County"] == "Montgomery County, AR", "BUYER_COUNTY"] = "MONTGOMERY"
df4.loc[df4["County"] == "Kalawao County, HI", "BUYER_COUNTY"] = "KALAWAO"
df4.loc[df4["County"] == "Oglala Lakota County, SD", "BUYER_COUNTY"] = "OGLALA LAKOTA"

# ------------------------------------------

# creating final dataframe
# select required columns
df5 = df4[["State", "State_Code", "BUYER_COUNTY", "County_Code", "Year", "Population"]]

# rename columns
df5 = df5.rename(
    columns={
        "BUYER_COUNTY": "County",
    }
)

# ------------------------------------------

# Writing to Parquet
df5.to_parquet("Data/processed/population.parquet", index=False)
