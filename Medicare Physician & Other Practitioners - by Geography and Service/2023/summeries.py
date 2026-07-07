import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]

# Define zero counter
def count_zeros(series):
    return ((series == "") | (series.isna())).sum()

# Summarize numerical columns
def summarize_numerics(data):
    statistics = []
    numerics = data.select_dtypes(include=[np.number]).columns
    for col in numerics:
        num_zeros = count_zeros(data[col])
        statistics.append((col,
                           'numeric',
                           data[col].notnull().sum(),
                           f'{data[col].notnull().sum()/data.shape[0]*100:.1f}%',
                           num_zeros,
                           round(data[col].min(), 2),
                           round(data[col].max(), 2),
                           round(data[col].mean(), 2),
                           round(data[col].std(), 2),
                           data[col].mode()[0] if not data[col].mode().empty else ''
                           ))
    return pd.DataFrame(statistics, columns=[
        'Field Name', 'Field Type', '# Records Have Values',
        '% Populated', '# Zeros', 'Min', 'Max', 'Mean',
        'Standard Deviation', 'Most Common'])

# Summarize categorical columns
def summarize_categoricals(data):
    statistics = []
    categoricals = data.select_dtypes(include=['object']).columns
    # Convert string "0" to blank before processing
    for col in categoricals:
        data[col] = data[col].replace("0", "")
    for col in categoricals:
        statistics.append((col,
                           'categorical',
                           data[col].notnull().sum(),
                           f'{data[col].notnull().sum()/data.shape[0]*100:.1f}%',
                           count_zeros(data[col]),
                           data[col].nunique(),
                           data[col].mode()[0] if not data[col].mode().empty else ''
                           ))
    return pd.DataFrame(statistics, columns=[
        'Field Name', 'Field Type', '# Records Have Values',
        '% Populated', '# Zeros', '# Unique Values', 'Most Common'])

# # Define classification function
# def classify_zipcodes(row):
#     if row['Rndrng_Prvdr_Zip5'] == '35249' and row['Rndrng_Prvdr_State_Abrvtn'] == 'AL':
#         return 'Urban'
#     elif row['Rndrng_Prvdr_Zip5'] == '96913' and row['Rndrng_Prvdr_State_Abrvtn'] == 'GU':
#         return 'Rural'
#     else:
#         return row['Rndrng_Prvdr_RUCA_Desc']  # Keep existing classification
    

# ==============================================
# SECTION 1: DATA IMPORT & CLEANING
# ==============================================

# Load the filtered geography dataset from the project root.
file_path = PROJECT_ROOT / "Filtered_RF_Geography_Service.csv"
rf_data = pd.read_csv(file_path, dtype=str)
output_path = SCRIPT_DIR

# Basic structure and completeness checks
basic_info = {
    "shape": rf_data.shape,
    "datatypes":rf_data.dtypes,
    "columns": rf_data.columns.tolist(),
    "missing_values": rf_data.isnull().sum().sort_values(ascending=False),
    "duplicate_rows": rf_data.duplicated().sum()
}

# Data Type Checks
dtype_summary = rf_data.dtypes.reset_index()
dtype_summary.columns = ['Column', 'Data_Type']
# print(dtype_summary)

# Converting the Datatypes
numeric = [
    'Tot_Rndrng_Prvdrs','Tot_Benes', 'Tot_Srvcs', 'Tot_Bene_Day_Srvcs','Avg_Sbmtd_Chrg', 'Avg_Mdcr_Alowd_Amt',
    'Avg_Mdcr_Pymt_Amt', 'Avg_Mdcr_Stdzd_Amt'
]
for col in numeric:
    rf_data[col] = pd.to_numeric(rf_data[col])

# Summarize numerical columns
sum_num = summarize_numerics(rf_data)
# print(sum_num)
# Summarize categorical columns
sum_cat = summarize_categoricals(rf_data)
# print(sum_cat)

num_output_path = output_path / "Numeric_Summary.csv"
sum_num.to_csv(num_output_path, index=False)

cat_output_path = output_path / "Categorical_Summary.csv"
sum_cat.to_csv(cat_output_path, index=False)
