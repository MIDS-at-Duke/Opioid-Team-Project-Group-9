import pandas as pd
import numpy as np

#Initiate temporary list for data chunk
chunked_list = []
cols_of_interest = ['BUYER_STATE', 'BUYER_COUNTY', 'TRANSACTION_DATE', 'MME']
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
    # Group by state, county, and year and sum MME
    grouped_chunk = chunk.groupby(['BUYER_STATE', 'BUYER_COUNTY', 'YEAR'])['MME'].sum().reset_index()
    chunked_list.append(grouped_chunk)

#load chunked_list into dataframe
chunked_shipment = pd.concat(chunked_list)
print(chunked_shipment.shape)

#Final aggregate by state, county and year level
shipment_eda = chunked_shipment.groupby(['BUYER_STATE', 'BUYER_COUNTY', 'YEAR'])['MME'].sum().reset_index()
shipment_eda.to_parquet('/Users/robintitus/Desktop/PDS/Final Project/Opioid-Team-Project-Group-9-1/Data/processed/shipment_eda.parquet')

#Load chunked_shipment
shipment_eda = pd.read_parquet('/Users/robintitus/Desktop/PDS/Final Project/Opioid-Team-Project-Group-9-1/Data/processed/shipment_eda.parquet')

shipment_eda_shape = shipment_eda.shape
#print(f'dataframe shape: {shipment_eda_shape}') 
#Shape: (42908, 4)

shipment_eda_cols = shipment_eda.columns.tolist()
#print(f'These are the list of columns: {shipment_eda_cols}')
#Cols: ['BUYER_STATE', 'BUYER_COUNTY', 'MME', 'YEAR']

#Find nulls/na in each column
col_nulls = {}
for cols in shipment_eda.columns:
    col_nulls[cols] = shipment_eda[cols].isnull().sum()
    pass
#print(f'columns with null values: {col_nulls}')
#{'BUYER_STATE': 0, 'BUYER_COUNTY': 0, 'YEAR': 0, 'MME': 0}

#Check unique State count in dataframe
buyer_state = pd.Series(shipment_eda['BUYER_STATE'].unique())
print(f'Number of unique states in dataset: {shipment_eda.nunique()}')
#Number of unique states in dataset: 55

#Looking for state discripancies
actual_us_states = pd.read_csv('/Users/robintitus/Desktop/PDS/Final Project/Opioid-Team-Project-Group-9-1/Data/raw/us_states-ab.csv')
actual_us_states_code = actual_us_states['code']
mismatch = buyer_state[~buyer_state.isin(actual_us_states_code)]
#print(f'These are the states in our dataset that aren\'t actual US states: {mismatch}')
#These are territories of the United States but not states: PR, MP, VI, PW, GU, AE(army) 

#Ready EDA and further processing