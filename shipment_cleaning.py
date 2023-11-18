import pandas as pd
import numpy as np

#Initiate temporary list for data chunk
chunked_list = []
cols_of_interest = ['BUYER_STATE', 'BUYER_ZIP', 'BUYER_COUNTY', 'TRANSACTION_CODE', 'TRANSACTION_DATE', 'MME']
chunksize = 10 ** 7
file_path = '/Users/robintitus/Desktop/PDS/Final Project/arcos_all_washpost.zip'

reader = pd.read_csv(file_path, compression='zip', sep='\t', chunksize=chunksize, usecols=cols_of_interest)

#Chunk and process raw dataset
for i, chunk in enumerate(reader):
    print(f'processing chunk {i+1}')
    #Create and process for year column / assumption
    chunk['YEAR'] = pd.to_datetime(chunk['TRANSACTION_DATE']).dt.year
    #Drop Alaska
    chunk = chunk[chunk['BUYER_STATE'] != 'AK']
    chunked_list.append(chunk)

#load chunked_list into dataframe
chunked_shipment = pd.concat(chunked_list)
print(chunked_shipment.shape)

#Save chunked data to parquet
chunked_shipment.to_parquet('/Users/robintitus/Desktop/PDS/Final Project/chunked_shipment.parquet')

#Load chunked_shipment
chunked_shipment_df = pd.read_parquet('/Users/robintitus/Desktop/PDS/Final Project/chunked_shipment.parquet')

chunked_shipment_df_shape = chunked_shipment_df.shape
print(f'dataframe shape: {chunked_shipment_df_shape}')
#Shape: (329057090, 7)

chunked_shipment_df_cols = chunked_shipment_df.columns.tolist()
print(f'These are the list of columns: {chunked_shipment_df_cols}')
#Cols: ['BUYER_STATE', 'BUYER_ZIP', 'BUYER_COUNTY', 'TRANSACTION_CODE', 'TRANSACTION_DATE', 'MME', 'YEAR']

#Find nulls/na in each column
col_nulls = {}
for cols in chunked_shipment_df.columns:
    col_nulls[cols] = chunked_shipment_df[cols].isnull().sum()
    pass
print(f'columns with null values: {col_nulls}')
{'BUYER_STATE': 0, 'BUYER_ZIP': 0, 'BUYER_COUNTY': 191, 'TRANSACTION_CODE': 0, 'TRANSACTION_DATE': 0, 'MME': 0, 'YEAR': 0}

#Check unique State count in dataframe
buyer_state = pd.Series(chunked_shipment_df['BUYER_STATE'].unique())
print(f'Number of unique states in dataset: {buyer_state.nunique()}')
#Number of unique states in dataset: 56

# Looking for state discripancies
actual_us_states = pd.read_csv('/Users/robintitus/Desktop/PDS/Final Project/us_states-ab.csv')
actual_us_states_code = actual_us_states['code']
mismatch = buyer_state[~buyer_state.isin(actual_us_states_code)]
print(f'These are the states in our dataset that aren\'t actual US states: {mismatch}')
#These are territories of the United States but not states: PR, MP, VI, PW, GU, AE(army) 

# Final aggregate by state, county and year level
# staging_shipment = staging_shipment.groupby(['BUYER_STATE', 'BUYER_COUNTY', 'YEAR'])['MME'].sum().reset_index()
# staging_shipment.to_parquet('/Users/robintitus/Desktop/PDS/Final Project/staging_shipment.parquet')

# Viewing staged dataframe
# staging_shipment = pd.read_parquet(
#     "/Users/robintitus/Desktop/PDS/Final Project/staging_shipment.parquet"
# )
# print(staging_shipment.head(10))
# print(staging_shipment.shape)

# Save to Parquet for analysis

# Ready for analysis, git-lfs. 
