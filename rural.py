import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

# Load all final summary files for visualization and analysis
cpt_provider_path = PROJECT_ROOT / "RF_Procedure_Volume_by_CPT_and_Provider_Type.csv"
state_access_path = PROJECT_ROOT / "State_Level_RF_Access_and_Distribution.csv"
zip_opportunity_path = PROJECT_ROOT / "Opportunity_Index_by_ZIP.csv"
state_opportunity_path = PROJECT_ROOT / "Opportunity_Index_by_State.csv"

cpt_df = pd.read_csv(cpt_provider_path)
state_df = pd.read_csv(state_access_path)
zip_df = pd.read_csv(zip_opportunity_path)
state_opp_df = pd.read_csv(state_opportunity_path)
rf_data = pd.read_csv(PROJECT_ROOT / "Filtered_RF_Providers.csv")

# Convert provider type and RUCA to categorical for better control
zip_df['Rndrng_Prvdr_RUCA_Desc'] = zip_df['Rndrng_Prvdr_RUCA_Desc'].astype('category')
state_opp_df['Rndrng_Prvdr_RUCA_Desc'] = state_opp_df['Rndrng_Prvdr_RUCA_Desc'].astype('category')

# Summary: Count how many ZIPs and states are rural
rural_zip_count = zip_df['Rndrng_Prvdr_RUCA_Desc'].str.contains("Rural", case=False, na=False).sum()
rural_state_count = state_opp_df['Rndrng_Prvdr_RUCA_Desc'].str.contains("Rural", case=False, na=False).sum()

# Get share of rural areas in dataset
rural_summary = {
    "Total ZIPs": len(zip_df),
    "Rural ZIPs": rural_zip_count,
    "Total State x RUCA Groups": len(state_opp_df),
    "Rural State x RUCA Groups": rural_state_count
}
print(rural_summary)

# 1. Bar chart: Total_Services by CPT and Provider Type (Top 15)
top_cpt_provider = cpt_df.sort_values(by="Total_Services", ascending=False).head(15)

plt.figure(figsize=(12, 6))
sns.barplot(
    data=top_cpt_provider,
    x="Total_Services",
    y="HCPCS_Cd",
    hue="Rndrng_Prvdr_Type",
    dodge=False
)
plt.title("Top RF Procedure Volumes by CPT Code and Provider Type")
plt.xlabel("Total Services")
plt.ylabel("CPT Code")
plt.legend(title="Provider Type", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# Aggregate total services by state
state_totals = state_df.groupby("Rndrng_Prvdr_State_Abrvtn")["Total_Services"].sum().reset_index()
state_totals = state_totals.sort_values(by="Total_Services", ascending=False)

# Top 10 states
top10 = state_totals.head(10)

# Bottom 10 states (excluding states with 0 total services if any)
bottom10 = state_totals[state_totals["Total_Services"] > 0].tail(10)

# Plot side-by-side
fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharex=False)

# Top 10 states
sns.barplot(data=top10, x="Total_Services", y="Rndrng_Prvdr_State_Abrvtn", ax=axes[0], palette="Blues_d")
axes[0].set_title("Top 10 States by RF Procedure Volume")
axes[0].set_xlabel("Total Services")
axes[0].set_ylabel("State")

# Bottom 10 states
sns.barplot(data=bottom10, x="Total_Services", y="Rndrng_Prvdr_State_Abrvtn", ax=axes[1], palette="Reds_d")
axes[1].set_title("Bottom 10 States by RF Procedure Volume")
axes[1].set_xlabel("Total Services")
axes[1].set_ylabel("")

plt.tight_layout()
plt.show()

# Prepare targeting fields
zip_df["RUCA_Category"] = zip_df["Rndrng_Prvdr_RUCA_Desc"].str.lower()

# Define targeting criteria
target_zip_df = zip_df[
    (zip_df["Opportunity_Index"] > 500) &
    (zip_df["Total_Providers"] < 20) &
    (zip_df["RUCA_Category"].str.contains("rural|micropolitan|small town"))
]

# Extract ZIP to state mapping
zip_to_state = rf_data[["Rndrng_Prvdr_Zip5", "Rndrng_Prvdr_State_Abrvtn"]].drop_duplicates()
target_zip_df["Rndrng_Prvdr_Zip5"] = target_zip_df["Rndrng_Prvdr_Zip5"].astype(str)
zip_to_state["Rndrng_Prvdr_Zip5"] = zip_to_state["Rndrng_Prvdr_Zip5"].astype(str)

# Merge state info
target_zip_df = target_zip_df.merge(zip_to_state, on="Rndrng_Prvdr_Zip5", how="left")

# Top ZIPs to target
top_target_zips = target_zip_df.sort_values(by="Opportunity_Index", ascending=False).head(25)

# Count ZIPs per state
state_opportunity_counts = target_zip_df.groupby("Rndrng_Prvdr_State_Abrvtn").size().reset_index(name="Num_Target_ZIPs")
state_opportunity_counts = state_opportunity_counts.sort_values(by="Num_Target_ZIPs", ascending=False)

# Save the targeting outputs to CSV files
top_zip_path = PROJECT_ROOT / "Top_25_Target_ZIPs.csv"
state_summary_path = PROJECT_ROOT / "State_Target_ZIP_Counts.csv"

top_target_zips.to_csv(top_zip_path, index=False)
state_opportunity_counts.to_csv(state_summary_path, index=False)

# Get ZIP codes from Top 25
top_zip_list = pd.read_csv(top_zip_path)
top_zip_codes = top_zip_list["Rndrng_Prvdr_Zip5"].astype(str).unique()

# Filter original data to just those ZIPs
rf_top_zips = rf_data[rf_data["Rndrng_Prvdr_Zip5"].isin(top_zip_codes)]

# Group by ZIP + Provider (NPI) and sum services
provider_summary = rf_top_zips.groupby(
    ["Rndrng_Prvdr_Zip5", "Rndrng_NPI", "Rndrng_Prvdr_Last_Org_Name", "Rndrng_Prvdr_First_Name", "Rndrng_Prvdr_Type"]
)["Tot_Srvcs"].sum().reset_index()

# For each ZIP, keep the top provider by Tot_Srvcs
top_provider_by_zip = provider_summary.sort_values(["Rndrng_Prvdr_Zip5", "Tot_Srvcs"], ascending=[True, False])\
    .groupby("Rndrng_Prvdr_Zip5").head(1).reset_index(drop=True)

# Merge with the opportunity data for context
enhanced_top_zips = pd.merge(top_zip_list, top_provider_by_zip, on="Rndrng_Prvdr_Zip5", how="left")

# Ensure both ZIP columns are string type for merging
top_zip_list["Rndrng_Prvdr_Zip5"] = top_zip_list["Rndrng_Prvdr_Zip5"].astype(str)
top_provider_by_zip["Rndrng_Prvdr_Zip5"] = top_provider_by_zip["Rndrng_Prvdr_Zip5"].astype(str)

# Merge again after fixing types
enhanced_top_zips = pd.merge(top_zip_list, top_provider_by_zip, on="Rndrng_Prvdr_Zip5", how="left")

# Save final table
output_path = PROJECT_ROOT / "Enhanced_Top_25_Target_ZIPs_with_Provider.csv"
enhanced_top_zips.to_csv(output_path, index=False)
