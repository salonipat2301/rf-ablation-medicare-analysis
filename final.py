import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

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

# Define classification function
def classify_zipcodes(row):
    if row['Rndrng_Prvdr_Zip5'] == '35249' and row['Rndrng_Prvdr_State_Abrvtn'] == 'AL':
        return '"Urban"'
    elif row['Rndrng_Prvdr_Zip5'] == '96913' and row['Rndrng_Prvdr_State_Abrvtn'] == 'GU':
        return '"Rural"'
    else:
        return row['Rndrng_Prvdr_RUCA_Desc']  # Keep existing classification
    
# Define function to save and display a plot
def save_and_show_plot(fig, filename):
    output_path = PROJECT_ROOT / filename
    fig.savefig(output_path, bbox_inches='tight')
    plt.close(fig)
    return output_path

# ==============================================
# SECTION 1: DATA IMPORT & CLEANING
# ==============================================

# Load the filtered provider-service dataset from the project root.
file_path = PROJECT_ROOT / "Filtered_RF_Providers.csv"
rf_data = pd.read_csv(file_path, dtype=str)
output_path = PROJECT_ROOT

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
    'Tot_Benes', 'Tot_Srvcs', 'Tot_Bene_Day_Srvcs',
    'Avg_Sbmtd_Chrg', 'Avg_Mdcr_Alowd_Amt',
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

num_output_path ="Numeric_Summary.csv"
sum_num.to_csv(num_output_path, index=False)

cat_output_path = "Categorical_Summary.csv"
sum_cat.to_csv(cat_output_path, index=False)

# Extract the 9 rows with missing RUCA descriptions
missing_ruca = rf_data[rf_data['Rndrng_Prvdr_RUCA_Desc'].isna()]
miss_output_path = "missing.csv"
missing_ruca.to_csv(miss_output_path, index=False)

# Impute RUCA description for missing rows
ruca_impute_value = "Metropolitan area core: primary flow within an urbanized area of 50,000 and greater"

# Apply imputation to the main dataset
rf_data['Rndrng_Prvdr_RUCA_Desc'] = rf_data['Rndrng_Prvdr_RUCA_Desc'].fillna(ruca_impute_value)
rf_data.loc[(rf_data['Rndrng_Prvdr_Zip5'] == '91460'), 'Rndrng_Prvdr_Zip5'] = '94609'

# Apply only to Unknown classifications
rf_data['Rndrng_Prvdr_RUCA_Desc'] = rf_data.apply(
    lambda row: classify_zipcodes(row) if row['Rndrng_Prvdr_RUCA_Desc'] == "Unknown" else row['Rndrng_Prvdr_RUCA_Desc'],
    axis=1
)

# ==============================================
# SECTION 2: Provider Density Analysis

# Provider Density = Unique_Providers / Total_Beneficiaries
# Tot_Bene_Day_Srvcs (unique beneficiaries per day) instead of Tot_Benes (total beneficiaries across services) to prevent duplicate counts
# ==============================================

# TODO: US-Wide Provider Density by Facility & Urban/Rural
# US-level summary
# us_summary = rf_data.groupby(['Place_Of_Srvc', 'Rndrng_Prvdr_RUCA_Desc']).agg(
#     Total_Beneficiaries=('Tot_Bene_Day_Srvcs', 'sum'),
#     Unique_Providers=('Rndrng_NPI', 'nunique')
# ).reset_index()
# us_summary['Provider_Density'] = us_summary['Unique_Providers'] / us_summary['Total_Beneficiaries']
# us_summary.to_csv("us_summary.csv", index=False)
# Aggregate data with additional metrics

us_summary = rf_data.groupby(['Place_Of_Srvc', 'Rndrng_Prvdr_RUCA_Desc']).agg(
    Total_Services=('Tot_Srvcs', 'sum'),
    Total_Beneficiaries=('Tot_Benes', 'sum'),
    Total_Beneficiary_Days=('Tot_Bene_Day_Srvcs', 'sum'),
    Unique_Providers=('Rndrng_NPI', 'nunique')
).reset_index()
# Calculate key metrics
us_summary['Provider_Density_Per_Day'] = us_summary['Unique_Providers'] / us_summary['Total_Beneficiary_Days']
us_summary['Provider_Coverage'] = (us_summary['Unique_Providers'] / us_summary['Total_Beneficiaries'])
us_summary['Visits_Per_Beneficiary'] = us_summary['Total_Beneficiary_Days'] / us_summary['Total_Beneficiaries']
us_summary['Visits_per_Provider'] = us_summary['Total_Beneficiary_Days']  / us_summary['Unique_Providers']
us_summary.to_csv("us_summary.csv", index=False)

# TODO: CPT-Specific Provider Density (e.g., Surgery vs. Consultations)
# Group by CPT code, facility type, and urban/rural
cpt_summary = rf_data.groupby(['HCPCS_Cd', 'Place_Of_Srvc', 'Rndrng_Prvdr_RUCA_Desc']).agg(
    Total_Beneficiaries=('Tot_Bene_Day_Srvcs', 'sum'), Unique_Providers=('Rndrng_NPI', 'nunique')
).reset_index()
cpt_summary['Provider_Density'] = cpt_summary['Unique_Providers'] / cpt_summary['Total_Beneficiaries']
cpt_summary.to_csv("cpt_summary.csv", index=False)

# TODO: State-Level Analysis
# State-level provider density
rf_data['Rndrng_Prvdr_RUCA_Desc'] = rf_data['Rndrng_Prvdr_RUCA_Desc'].astype(str)
state_summary = rf_data.groupby(['Rndrng_Prvdr_State_Abrvtn', 'Place_Of_Srvc', 'Rndrng_Prvdr_RUCA_Desc']).agg(
    Total_Beneficiaries=('Tot_Bene_Day_Srvcs', 'sum'),
    Unique_Providers=('Rndrng_NPI', 'nunique')
).reset_index()

state_summary['Provider_Density'] = state_summary['Unique_Providers'] / state_summary['Total_Beneficiaries']
state_summary.to_csv("state_summary.csv", index=False)

# TODO: Urban vs. Rural Provider Density by Facility Type
# Filter US data for Facility (F) vs. Office (O)
us_facility = us_summary[us_summary['Place_Of_Srvc'] == 'F']
us_office = us_summary[us_summary['Place_Of_Srvc'] == 'O']
distinct_values = rf_data['Rndrng_Prvdr_RUCA_Desc'].unique()
print(distinct_values)
# Combine and simplify RUCA labels (e.g., "Metropolitan" = Urban)
# TODO: 
urban_rural_labels = {
    'Metropolitan area core: primary flow within an urbanized area of 50,000 and greater': 'Urban',
    'Micropolitan area core: primary flow within an urban cluster of 10,000 to 49,999': 'Urban',
    'Secondary flow 30% to <50% to a larger urbanized area of 50,000 and greater': 'Urban',
    'Small town core: primary flow within an urban cluster of 2,500 to 9,999': 'Rural',
    'Metropolitan area high commuting: primary flow 30% or more to a urbanized area of 50,000 and greater': 'Urban',
    'Metropolitan area low commuting: primary flow 10% to <30% to a urbanized area of 50,000 and greater': 'Urban',
    'Rural areas: primary flow to a tract outside a urbanized area of 50,000 and greater or UC': 'Rural',
    'Metropolitan area low commuting: primary flow 10% to <30% to a urbanized area of 50,000 and greater': 'Urban',
    'Secondary flow 30% to <50% to a larger urbanized area of 50,000 and greater': 'Urban',
    'Micropolitan high commuting: primary flow 30% or more to a urban cluster of 10,000 to 49,999': 'Rural',
    'Secondary flow 30% to <50% to a urban cluster of 10,000 to 49,999': 'Urban',
    'Small town low commuting: primary flow 10% to <30% to a urban cluster of 2,500 to 9,999': 'Rural',
    'Small town high commuting: primary flow 30% or more to a urban cluster of 2,500 to 9,999': 'Rural',
    'Micropolitan low commuting: primary flow 10% to <30% to a urban cluster of 10,000 to 49,999':'Rural',
    'Urban':'Urban',
    'Rural':'Rural'
}

us_summary['Urban_Rural'] = us_summary['Rndrng_Prvdr_RUCA_Desc'].map(urban_rural_labels)
# # Plot
# plt.figure(figsize=(10, 6))
# sns.barplot(data=us_summary, x='Place_Of_Srvc', y='Provider_Density_Per_Day', hue='Urban_Rural')
# plt.title('Provider Density: Urban vs. Rural (National)', fontsize=14, pad=20)
# plt.xlabel('Facility Type (F = Facility, O = Office)', fontsize=12)
# plt.ylabel('Providers per Beneficiary', fontsize=12)
# plt.xticks(fontsize=11)
# plt.yticks(fontsize=11)
# plt.grid(axis='y', linestyle='--', alpha=0.4)
# plt.legend(title='Urban_Rural', title_fontsize=11, fontsize=10)
# sns.despine(left=True, top=True)  # Removes the left and top axes lines
# plt.tight_layout()
# plt.show()

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=us_summary, x='Place_Of_Srvc', y='Provider_Coverage', hue='Urban_Rural', ax=ax, ci=None)
ax.set_title('Provider Density: Urban vs. Rural (National)', fontsize=14, pad=20)
ax.set_xlabel('Facility Type (F = Facility, O = Office)', fontsize=12)
ax.set_ylabel('Providers per Beneficiary', fontsize=12)
ax.tick_params(axis='both', labelsize=11)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.legend(title='Urban_Rural', title_fontsize=11, fontsize=10)
sns.despine(left=True, top=True)
save_and_show_plot(fig, "us_provider_density.png")

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=us_summary, x='Place_Of_Srvc', y='Provider_Density_Per_Day', hue='Urban_Rural', ax=ax, ci=None)
ax.set_title('Provider_Density_Per_Day: Urban vs. Rural (National)', fontsize=14, pad=20)
ax.set_xlabel('Facility Type (F = Facility, O = Office)', fontsize=12)
ax.set_ylabel('Providers per Beneficiary', fontsize=12)
ax.tick_params(axis='both', labelsize=11)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.legend(title='Urban_Rural', title_fontsize=11, fontsize=10)
sns.despine(left=True, top=True)
save_and_show_plot(fig, "us_provider_density_per_day.png")


fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=us_summary,x='Place_Of_Srvc',y='Visits_per_Provider',hue='Urban_Rural',ci=None,ax=ax)
ax.set_title('Visits per Provider: Urban vs. Rural (National)', fontsize=14, pad=20)
ax.set_xlabel('Facility Type (F = Facility, O = Office)', fontsize=12)
ax.set_ylabel('Visits per Provider', fontsize=12)
ax.tick_params(axis='both', labelsize=11)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.legend(title='Urban_Rural', title_fontsize=11, fontsize=10)
sns.despine(left=True, top=True)
save_and_show_plot(fig, "Visits_per_Provider.png")

# TODO: 2. State-Level Disparities
# Calculate urban-rural gap ratio for each state
state_summary['Rndrng_Prvdr_RUCA_Desc'] = state_summary['Rndrng_Prvdr_RUCA_Desc'].astype(str)
state_summary['Urban_Rural'] = state_summary['Rndrng_Prvdr_RUCA_Desc'].map(urban_rural_labels)

# Add diagnostic prints
print("\nChecking state data:")
print("Total states in state_summary:", len(state_summary['Rndrng_Prvdr_State_Abrvtn'].unique()))
print("States in state_summary:", sorted(state_summary['Rndrng_Prvdr_State_Abrvtn'].unique()))
print("\nNJ data in state_summary:")
print(state_summary[state_summary['Rndrng_Prvdr_State_Abrvtn'] == 'NJ'])

# Ensure we have both urban and rural data for each state
state_urban = state_summary[state_summary['Urban_Rural'] == 'Urban'].copy()
state_rural = state_summary[state_summary['Urban_Rural'] == 'Rural'].copy()

# Print NJ data in urban and rural
print("\nNJ data in urban areas:")
print(state_urban[state_urban['Rndrng_Prvdr_State_Abrvtn'] == 'NJ'])
print("\nNJ data in rural areas:")
print(state_rural[state_rural['Rndrng_Prvdr_State_Abrvtn'] == 'NJ'])

# Merge urban and rural data, keeping all states
state_gap = pd.merge(
    state_urban,
    state_rural,
    on=['Rndrng_Prvdr_State_Abrvtn', 'Place_Of_Srvc'],
    how='outer',
    suffixes=('_Urban', '_Rural')
)

# Fill missing values with 0 for calculation purposes
state_gap = state_gap.fillna(0)

# Calculate gap ratio, handling division by zero
state_gap['Gap_Ratio'] = np.where(
    state_gap['Provider_Density_Rural'] > 0,
    state_gap['Provider_Density_Urban'] / state_gap['Provider_Density_Rural'],
    np.inf  # Use infinity for states with no rural providers
)

# Print NJ data in state_gap
print("\nNJ data in state_gap:")
print(state_gap[state_gap['Rndrng_Prvdr_State_Abrvtn'] == 'NJ'])

# Create comprehensive state-level analysis
state_analysis = state_gap.copy()

# Calculate absolute values and ratios
state_analysis['Urban_Patients'] = state_analysis['Total_Beneficiaries_Urban']
state_analysis['Rural_Patients'] = state_analysis['Total_Beneficiaries_Rural']
state_analysis['Urban_Providers'] = state_analysis['Unique_Providers_Urban']
state_analysis['Rural_Providers'] = state_analysis['Unique_Providers_Rural']

# Calculate patients per provider, handling division by zero
state_analysis['Urban_Patients_per_Provider'] = np.where(
    state_analysis['Urban_Providers'] > 0,
    state_analysis['Urban_Patients'] / state_analysis['Urban_Providers'],
    np.inf
)
state_analysis['Rural_Patients_per_Provider'] = np.where(
    state_analysis['Rural_Providers'] > 0,
    state_analysis['Rural_Patients'] / state_analysis['Rural_Providers'],
    np.inf
)

# Print unique states to verify
print("\nFinal states in analysis:", sorted(state_analysis['Rndrng_Prvdr_State_Abrvtn'].unique()))

# Save comprehensive state analysis
state_analysis.to_csv("comprehensive_state_analysis.csv", index=False)

# Create appendix-style visualization for all states
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), height_ratios=[1, 1])

# Plot 1: Urban vs Rural Provider Density Ratio
# Sort states alphabetically
state_analysis_sorted = state_analysis[state_analysis['Place_Of_Srvc'] == 'F'].sort_values('Rndrng_Prvdr_State_Abrvtn')

# Print NJ data specifically
print("\nNJ data in sorted analysis:")
print(state_analysis_sorted[state_analysis_sorted['Rndrng_Prvdr_State_Abrvtn'] == 'NJ'])

# Replace infinite values with a large number for visualization
state_analysis_sorted['Gap_Ratio_Plot'] = state_analysis_sorted['Gap_Ratio'].replace([np.inf, -np.inf], 100)

sns.barplot(data=state_analysis_sorted, 
            x='Gap_Ratio_Plot', 
            y='Rndrng_Prvdr_State_Abrvtn',
            ax=ax1,
            palette='viridis',
            ci=None)
ax1.set_title('Urban vs Rural Provider Density Ratio by State (Facility)', fontsize=12)
ax1.set_xlabel('Urban/Rural Provider Density Ratio', fontsize=10)
ax1.set_ylabel('State', fontsize=10)
ax1.grid(axis='x', linestyle='--', alpha=0.4)

# Plot 2: Absolute Values
# Create a melted dataframe for easier plotting
melted_data = pd.melt(state_analysis_sorted,
                      id_vars=['Rndrng_Prvdr_State_Abrvtn'],
                      value_vars=['Urban_Patients', 'Rural_Patients'],
                      var_name='Area',
                      value_name='Number_of_Patients')

sns.barplot(data=melted_data,
            x='Number_of_Patients',
            y='Rndrng_Prvdr_State_Abrvtn',
            hue='Area',
            ax=ax2,
            palette='Set2',
            ci=None)
ax2.set_title('Number of Patients by State and Area Type (Facility)', fontsize=12)
ax2.set_xlabel('Number of Patients', fontsize=10)
ax2.set_ylabel('State', fontsize=10)
ax2.grid(axis='x', linestyle='--', alpha=0.4)
ax2.legend(title='Area Type')

plt.tight_layout()
save_and_show_plot(fig, "state_level_analysis_appendix.png")

# Create a summary table for all states
all_states_summary = state_analysis[state_analysis['Place_Of_Srvc'] == 'F'][[
    'Rndrng_Prvdr_State_Abrvtn',
    'Urban_Patients',
    'Rural_Patients',
    'Urban_Providers',
    'Rural_Providers',
    'Urban_Patients_per_Provider',
    'Rural_Patients_per_Provider',
    'Gap_Ratio'
]].sort_values('Rndrng_Prvdr_State_Abrvtn').round(2)

all_states_summary.to_csv("all_states_summary.csv", index=False)

# Print summary of states
print("\nNumber of states in analysis:", len(all_states_summary))
print("\nStates with highest urban-rural gap ratios:")
print(all_states_summary.nlargest(10, 'Gap_Ratio')[['Rndrng_Prvdr_State_Abrvtn', 'Gap_Ratio']])
print("\nStates with lowest urban-rural gap ratios:")
print(all_states_summary.nsmallest(10, 'Gap_Ratio')[['Rndrng_Prvdr_State_Abrvtn', 'Gap_Ratio']])

# Plot only top 5 and bottom 5 states by gap ratio (with ties)
# Top 5 (with ties)
sorted_states = all_states_summary.sort_values('Gap_Ratio', ascending=False)
if len(sorted_states) >= 5:
    cutoff = sorted_states.iloc[4]['Gap_Ratio']
    top5_states = sorted_states[sorted_states['Gap_Ratio'] >= cutoff]
else:
    top5_states = sorted_states

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=top5_states, x='Gap_Ratio', y='Rndrng_Prvdr_State_Abrvtn', palette='viridis', ax=ax, ci=None)
ax.set_title('Top 5 States with Highest Urban-Rural Provider Density Gaps (Facility)', fontsize=14, pad=20)
ax.set_xlabel('Urban/Rural Provider Density Ratio', fontsize=12)
ax.set_ylabel('State', fontsize=12)
ax.grid(axis='x', linestyle='--', alpha=0.4)
save_and_show_plot(fig, "top5_state_gaps_facility.png")

# Bottom 5 (with ties)
sorted_states = all_states_summary.sort_values('Gap_Ratio', ascending=True)
if len(sorted_states) >= 5:
    cutoff = sorted_states.iloc[4]['Gap_Ratio']
    bottom5_states = sorted_states[sorted_states['Gap_Ratio'] <= cutoff]
else:
    bottom5_states = sorted_states

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=bottom5_states, x='Gap_Ratio', y='Rndrng_Prvdr_State_Abrvtn', palette='viridis', ax=ax, ci=None)
ax.set_title('Bottom 5 States with Lowest Urban-Rural Provider Density Gaps (Facility)', fontsize=14, pad=20)
ax.set_xlabel('Urban/Rural Provider Density Ratio', fontsize=12)
ax.set_ylabel('State', fontsize=12)
ax.grid(axis='x', linestyle='--', alpha=0.4)
save_and_show_plot(fig, "bottom5_state_gaps_facility.png")

# Analyze drug-related services
drug_analysis = rf_data.groupby(['Rndrng_Prvdr_State_Abrvtn', 'Place_Of_Srvc', 'Rndrng_Prvdr_RUCA_Desc']).agg(
    Total_Services=('Tot_Srvcs', 'sum'),
    Drug_Services=('HCPCS_Drug_Ind', lambda x: (x == 'Yes').sum()),
    Total_Beneficiaries=('Tot_Bene_Day_Srvcs', 'sum'),
    Unique_Providers=('Rndrng_NPI', 'nunique')
).reset_index()

# Calculate drug service percentages and provider metrics
drug_analysis['Drug_Service_Pct'] = (drug_analysis['Drug_Services'] / drug_analysis['Total_Services'] * 100).round(2)
drug_analysis['Provider_Density'] = drug_analysis['Unique_Providers'] / drug_analysis['Total_Beneficiaries']
drug_analysis['Urban_Rural'] = drug_analysis['Rndrng_Prvdr_RUCA_Desc'].map(urban_rural_labels)

# Save drug analysis
drug_analysis.to_csv("drug_service_analysis.csv", index=False)

# Create visualization for drug services by urban/rural
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), height_ratios=[1, 1])

# Plot 1: Drug Service Percentage by Urban/Rural
sns.barplot(data=drug_analysis[drug_analysis['Place_Of_Srvc'] == 'F'],
            x='Drug_Service_Pct',
            y='Rndrng_Prvdr_State_Abrvtn',
            hue='Urban_Rural',
            ax=ax1,
            palette='Set2',
            ci=None)
ax1.set_title('Percentage of Drug-Related Services by State and Area Type (Facility)', fontsize=14, pad=20)
ax1.set_xlabel('Percentage of Drug Services', fontsize=12)
ax1.set_ylabel('State', fontsize=12)
ax1.grid(axis='x', linestyle='--', alpha=0.4)
ax1.legend(title='Area Type', title_fontsize=11, fontsize=10)
save_and_show_plot(fig, "drug_services_by_state.png")

# Plot 2: Provider Density vs Drug Services
fig, ax = plt.subplots(figsize=(12, 8))
sns.scatterplot(data=drug_analysis[drug_analysis['Place_Of_Srvc'] == 'F'],
                x='Provider_Density',
                y='Drug_Service_Pct',
                hue='Urban_Rural',
                ax=ax,
                palette='Set2',
                alpha=0.6)
ax.set_title('Relationship between Provider Density and Drug Services', fontsize=14, pad=20)
ax.set_xlabel('Provider Density (Providers per Beneficiary)', fontsize=12)
ax.set_ylabel('Percentage of Drug Services', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.4)
ax.legend(title='Area Type', title_fontsize=11, fontsize=10)
save_and_show_plot(fig, "provider_density_vs_drug_services.png")

# Create summary statistics for drug services
drug_summary = drug_analysis.groupby(['Urban_Rural', 'Place_Of_Srvc']).agg({
    'Drug_Service_Pct': ['mean', 'std', 'min', 'max'],
    'Provider_Density': ['mean', 'std', 'min', 'max'],
    'Total_Services': 'sum',
    'Drug_Services': 'sum'
}).round(2)

drug_summary.to_csv("drug_service_summary.csv")

# Calculate correlation between provider density and drug services
correlation = drug_analysis[drug_analysis['Place_Of_Srvc'] == 'F'].groupby('Urban_Rural').apply(
    lambda x: x['Provider_Density'].corr(x['Drug_Service_Pct'])
).round(3)

correlation.to_csv("provider_density_drug_correlation.csv")

# Create a heatmap of drug service percentages by state and urban/rural
drug_pivot = drug_analysis[drug_analysis['Place_Of_Srvc'] == 'F'].pivot_table(
    index='Rndrng_Prvdr_State_Abrvtn',
    columns='Urban_Rural',
    values='Drug_Service_Pct'
).round(2)

fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(drug_pivot, 
            annot=True, 
            cmap='YlGnBu',
            ax=ax,
            fmt='.1f')
ax.set_title('Drug Service Percentage by State and Area Type', fontsize=14, pad=20)
save_and_show_plot(fig, "drug_services_heatmap.png")

# Create a box plot of drug service percentages by urban/rural
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=drug_analysis[drug_analysis['Place_Of_Srvc'] == 'F'],
            x='Urban_Rural',
            y='Drug_Service_Pct',
            ax=ax,
            palette='Set2',
            showfliers=False)
ax.set_title('Distribution of Drug Service Percentages by Area Type', fontsize=14, pad=20)
ax.set_xlabel('Area Type', fontsize=12)
ax.set_ylabel('Percentage of Drug Services', fontsize=12)
ax.grid(axis='y', linestyle='--', alpha=0.4)
save_and_show_plot(fig, "drug_services_boxplot.png")

# # Group by CPT code and provider type to summarize total services and total providers
# summary_cpt_provider = rf_data.groupby(['HCPCS_Cd', 'Rndrng_Prvdr_Type']).agg(
#     Total_Services=('Tot_Srvcs', 'sum'),
#     Total_Providers=('Rndrng_NPI', 'nunique'),
#     Total_Beneficiaries=('Tot_Benes', 'sum')
# ).reset_index().sort_values(by='Total_Services', ascending=False)
# output_path = "RF_Procedure_Volume_by_CPT_and_Provider_Type.csv"
# summary_cpt_provider.to_csv(output_path, index=False)


# # Drop rows with missing critical data
# rf_data_s = rf_data.dropna(subset=['Tot_Bene_Day_Srvcs', 'Rndrng_NPI', 'Place_Of_Srvc', 'Rndrng_Prvdr_RUCA_Desc', 'Rndrng_Prvdr_State_Abrvtn'])

# # Grouping for US-wide totals by Place of Service and RUCA (rural vs urban)
# us_summary = rf_data_s.groupby(['Place_Of_Srvc', 'Rndrng_Prvdr_RUCA_Desc']).agg(
#     Total_Services=('Tot_Bene_Day_Srvcs', 'sum'),
#     Unique_Providers=('Rndrng_NPI', pd.Series.nunique)
# ).reset_index()

# us_summary['Patients_per_Provider'] = us_summary['Total_Services'] / us_summary['Unique_Providers']

# # Grouping for state-wise totals by Place of Service and RUCA
# state_summary = rf_data_s.groupby(['Rndrng_Prvdr_State_Abrvtn', 'Place_Of_Srvc', 'Rndrng_Prvdr_RUCA_Desc']).agg(
#     Total_Services=('Tot_Bene_Day_Srvcs', 'sum'),
#     Unique_Providers=('Rndrng_NPI', pd.Series.nunique)
# ).reset_index()

# state_summary['Patients_per_Provider'] = state_summary['Total_Services'] / state_summary['Unique_Providers']

# import seaborn as sns
# import matplotlib.pyplot as plt


# # Plot for US-wide totals
# plt.figure(figsize=(12, 6))
# sns.barplot(data=us_summary, x='Place_Of_Srvc', y='Patients_per_Provider', hue='Rndrng_Prvdr_RUCA_Desc')
# plt.title("Patients per Provider by Place of Service and RUCA (US-wide)")
# plt.ylabel("Patients per Provider")
# plt.xlabel("Place of Service")
# plt.legend(title="RUCA Description", bbox_to_anchor=(1.05, 1), loc='upper left')
# plt.tight_layout()
# plt.show()


# # # Group by state and CPT code to analyze RF access and procedure volume
# # summary_state_cpt = rf_data.groupby(['Rndrng_Prvdr_State_Abrvtn', 'HCPCS_Cd']).agg(
# #     Total_Services=('Tot_Srvcs', 'sum'),
# #     Total_Providers=('Rndrng_NPI', 'nunique'),
# #     Total_Beneficiaries=('Tot_Benes', 'sum')
# # ).reset_index().sort_values(by='Total_Services', ascending=False)
# # state_output_path = "State_Level_RF_Access_and_Distribution.csv"
# # summary_state_cpt.to_csv(state_output_path, index=False)

# # # Group by ZIP and RUCA description to calculate Opportunity Index
# # # Group by ZIP and RUCA to calculate metrics
# # zip_summary = rf_data.groupby(['Rndrng_Prvdr_Zip5', 'Rndrng_Prvdr_RUCA_Desc']).agg(
# #     Total_Providers=('Rndrng_NPI', 'nunique'),
# #     Total_Beneficiaries=('Tot_Benes', 'sum'),
# #     Avg_Allowed_Amt=('Avg_Mdcr_Alowd_Amt', 'mean')
# # ).reset_index()

# # # Compute Opportunity Index (proxy using Avg_Allowed_Amt as a stand-in for Avg Risk Score)
# # zip_summary['Opportunity_Index'] = (zip_summary['Total_Beneficiaries'] + zip_summary['Avg_Allowed_Amt']) / zip_summary['Total_Providers']

# # # Save the result
# # zip_output_path = "Opportunity_Index_by_ZIP.csv"
# # zip_summary.to_csv(zip_output_path, index=False)

# # # Group by state and RUCA description to calculate Opportunity Index
# # state_summary = rf_data.groupby(['Rndrng_Prvdr_State_Abrvtn', 'Rndrng_Prvdr_RUCA_Desc']).agg(
# #     Total_Providers=('Rndrng_NPI', 'nunique'),
# #     Total_Beneficiaries=('Tot_Benes', 'sum'),
# #     Avg_Allowed_Amt=('Avg_Mdcr_Alowd_Amt', 'mean')
# # ).reset_index()

# # # Compute Opportunity Index
# # state_summary['Opportunity_Index'] = (state_summary['Total_Beneficiaries'] + state_summary['Avg_Allowed_Amt']) / state_summary['Total_Providers']

# # # Save the result
# # state_output_path = "Opportunity_Index_by_State.csv"
# # state_summary.to_csv(state_output_path, index=False)


# # Checking for Missing values
# # # Create a DataFrame for missing values and data types
# # missing_df = rf_data.isnull().sum().reset_index()
# # missing_df.columns = ['Column', 'Missing_Values']
# # missing_df['% Missing'] = (missing_df['Missing_Values'] / len(rf_data) * 100).round(2)
# # missing_df['Data_Type'] = rf_data.dtypes.values

# # # Sort by number of missing values
# # missing_df = missing_df.sort_values(by='Missing_Values', ascending=False).reset_index(drop=True)

# # # Display final data types for inspection
# # dtype_summary = rf_data[potential_numeric].dtypes.reset_index()
# # dtype_summary.columns = ['Column', 'Data_Type']
