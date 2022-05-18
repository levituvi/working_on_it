import numpy as np
import pandas as pd
import datetime as dt
import seaborn as sns
import datetime as dt

df = pd.read_csv('rfm\DATA\online_retail_II.csv')
df = df.rename(columns={'StockCode': 'Stock_Code',
'InvoiceDate': 'Invoice_Date', 'Customer ID': 'Customer_ID'})

# Change data types and grouping
df['Invoice_Date'] = pd.DatetimeIndex(df['Invoice_Date']).normalize()
df.astype({'Price': 'float64'}).dtypes
dfg = df.groupby(['Customer_ID'])


# Excluting RFM irrelevant values (contain and drop)
none_ID_df = df[(df['Customer_ID'].isna())] 
sub_zero_df = df['Price'] < 0
quan_sub_zero = df['Quantity'] < 0
df = df.drop(df[df['Price'] < 0].index)
df = df.drop(df[df['Quantity'] < 0].index)
df = df.drop(df[df['Customer_ID'].isna()].index)

# Ranges check
print('Quantity min - max :', df['Quantity'].min(),  '-',   df['Quantity'].max())
print('Invoice_Date min - max :', df['Invoice_Date'].min(),  '  -  ',   df['Invoice_Date'].max())
print('Price min - max :', df['Price'].min(),  '-',   df['Price'].max())

###### df['Invoice_Date'] = pd.to_datetime(df['Invoice_Date'])

# getting Recency
temp_R = df.groupby(['Customer_ID'])['Invoice_Date'].max()-df['Invoice_Date'].max()
df = pd.merge(df, temp_R, on = 'Customer_ID')

# getting Frequency
temp_F = df.groupby(['Customer_ID'])['Invoice'].nunique()
df = pd.merge(df, temp_F, on = 'Customer_ID')

# getting Monetary
df['spent'] = df['Price'] * df['Quantity']
temp_M = df.groupby(['Customer_ID'])['spent'].sum()
df = pd.merge(df, temp_M, on = 'Customer_ID')

rfm = df[['Customer_ID', 'Invoice_Date_y', 'Invoice_y', 'spent_y']].copy()
dict = {'Invoice_Date_y': 'Last_Invoice_Date', 'Invoice_y': 'Invoices_count',
 'spent_y': 'Total_spent'}
rfm.rename(columns=dict, inplace=True)
rfm.drop_duplicates(subset=None, keep='first', inplace=True, ignore_index=True)

# Cleaning and prepering values of Last_Invoice_Date
rfm['Last_Invoice_Date'] = rfm['Last_Invoice_Date'].astype('str')
rfm['Last_Invoice_Date'] = rfm['Last_Invoice_Date'].map(lambda x: x.lstrip('-'))
rfm['Last_Invoice_Date'] = rfm['Last_Invoice_Date'].map(lambda x: x.rstrip('days'))
rfm['Last_Invoice_Date'] = rfm['Last_Invoice_Date'].astype('int')

# slicing Recency by:

RS = rfm['Last_Invoice_Date'].quantile(q=[0.05, 0.25, 0.35, 0.7, 0.9])

# # slicing Frequency by:

FS = rfm['Invoices_count'].quantile(q=[0.5, 0.65, 0.8, 0.9, 0.95])

# # slicing Monetary by:

MS = rfm['Total_spent'].quantile(q=[0.5, 0.75, 0.90, 0.95, 0.99])

print('RS:\n',RS,'\n'*2,'FS:\n',FS,'\n'*2,'MS:\n',MS)

# Slicing definition

def R_score(x):
    if x <= -625:
        return 1
    elif x <= -380:
        return 2
    elif x <= -247: 
        return 3
    elif x <= -33: 
        return 4
    else:
        return 5
    

def F_score(x):
    if x <= 3:
        return 1
    elif x <= 5:
        return 2
    elif x <= 8: 
        return 3
    elif x <= 13: 
        return 4
    else:
        return 5
    
    
def M_score(x):
    if x <=  897.620:
        return 1
    elif x <=  2304.180:
        return 2
    elif x <= 5594.960: 
        return 3
    elif x <= 9530.080: 
        return 4
    else:
        return 5


segmented_rfm = rfm

segmented_rfm['R_quartile'] = segmented_rfm['Last_Invoice_Date'].apply(R_score)
segmented_rfm['F_quartile'] = segmented_rfm['Invoices_count'].apply(F_score)
segmented_rfm['M_quartile'] = segmented_rfm['Total_spent'].apply(M_score)
rfm


rfm['rfm_mean'] =  (rfm['R_quartile'] + rfm['F_quartile'] + rfm['M_quartile']) / 3
rfm['rfm_class'] = str((rfm['R_quartile'] + rfm['F_quartile'] + rfm['M_quartile']))

print(rfm)