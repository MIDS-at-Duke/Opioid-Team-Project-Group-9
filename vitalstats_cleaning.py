import pandas as pd
import numpy as np

# Initiate an empty list
keeper_list = []

# URL paths for each dataset
url_dict = {
    "url_03": "/Users/robintitus/Desktop/PDS/Final Project/vitalstats_files/US_VitalStatistics/Underlying Cause of Death, 2003.txt",
    "url_04": "/Users/robintitus/Desktop/PDS/Final Project/vitalstats_files/US_VitalStatistics/Underlying Cause of Death, 2004.txt",
    "url_05": "/Users/robintitus/Desktop/PDS/Final Project/vitalstats_files/US_VitalStatistics/Underlying Cause of Death, 2005.txt",
    "url_06": "/Users/robintitus/Desktop/PDS/Final Project/vitalstats_files/US_VitalStatistics/Underlying Cause of Death, 2006.txt",
    "url_07": "/Users/robintitus/Desktop/PDS/Final Project/vitalstats_files/US_VitalStatistics/Underlying Cause of Death, 2007.txt",
    "url_08": "/Users/robintitus/Desktop/PDS/Final Project/vitalstats_files/US_VitalStatistics/Underlying Cause of Death, 2008.txt",
    "url_09": "/Users/robintitus/Desktop/PDS/Final Project/vitalstats_files/US_VitalStatistics/Underlying Cause of Death, 2009.txt",
    "url_10": "/Users/robintitus/Desktop/PDS/Final Project/vitalstats_files/US_VitalStatistics/Underlying Cause of Death, 2010.txt",
    "url_11": "/Users/robintitus/Desktop/PDS/Final Project/vitalstats_files/US_VitalStatistics/Underlying Cause of Death, 2011.txt",
    "url_12": "/Users/robintitus/Desktop/PDS/Final Project/vitalstats_files/US_VitalStatistics/Underlying Cause of Death, 2012.txt",
    "url_13": "/Users/robintitus/Desktop/PDS/Final Project/vitalstats_files/US_VitalStatistics/Underlying Cause of Death, 2013.txt",
    "url_14": "/Users/robintitus/Desktop/PDS/Final Project/vitalstats_files/US_VitalStatistics/Underlying Cause of Death, 2014.txt",
    "url_15": "/Users/robintitus/Desktop/PDS/Final Project/vitalstats_files/US_VitalStatistics/Underlying Cause of Death, 2015.txt",
}

# Check format and structure in dataset
# pd.set_option('display.max_columns', None)

# vitalstats_03 = pd.read_csv(url_dict["url_03"], sep='\t')
# print(vitalstats_03.info())

# Loop and process all datasets into one dataframe
for key, value in url_dict.items():
    reader = pd.read_csv(value, sep="\t")
    # Dropping excess columns
    cols_to_drop = ["Notes", "Year Code"]
    reader_temp = reader.drop(columns=cols_to_drop)
    # Splitting County column into County and State
    reader_temp[["County", "State"]] = reader_temp["County"].str.split(
        ", ", expand=True
    )
    # Drop Alaska
    reader_temp = reader_temp[reader_temp["State"] != "AK"]
    # Fill NaN values in 'Year' with 1900 and convert to integer
    reader_temp["Year"] = reader_temp["Year"].fillna(1900).astype(int)
    # Convert 'Year' to datetime format and extract the year
    reader_temp["Year"] = pd.to_datetime(reader_temp["Year"], format="%Y").dt.year
    # Convert 'County Code' column to pandas nullable integer type
    reader_temp["County Code"] = reader_temp["County Code"].astype("Int64")

    keeper_list.append(reader_temp)
    print(f"Processed file: {key}")

# Concatenate and save dataframe file
vitalstats_temp = pd.concat(keeper_list)
vitalstats_temp.to_csv(
    "/Users/robintitus/Desktop/PDS/Final Project/vitalstats_temp.csv"
)

# Check format and structure of dataset
vitalstats_temp = pd.read_csv(
    "/Users/robintitus/Desktop/PDS/Final Project/vitalstats_temp.csv"
)

print(vitalstats_temp.info())
# print(len(vitalstats_temp[vitalstats_temp['State'] == 'AK']))
# vitalstats_temp_shape = vitalstats_temp.shape
# print(f"Dimensions of vitalstats_temp: {vitalstats_temp_shape}")
# Dimensions of vitalstats_temp: (57040, 8)

# print(vitalstats_temp['Year'].head(5))
print(vitalstats_temp["Year"].unique())
# vitalstats_temp['Year'] = vitalstats_temp['Year'].astype(int)

# Replace non-numeric 'Deaths' values with NaN, then convert to pandas nullable integer type
# reader_temp['Deaths'] = pd.to_numeric(reader_temp['Deaths'], errors='coerce').astype('Int64')