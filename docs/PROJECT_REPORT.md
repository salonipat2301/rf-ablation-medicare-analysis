# Project Report

This repository is an RF ablation Medicare analysis workspace built from CMS Physician & Other Practitioners data.

## Snapshot

- Total files discovered: 78
- Python scripts: 5
- CSV outputs/data files: 25
- PNG figures: 27
- PDF references: 10
- Excel workbooks: 3
- Cache/temp files: 5 `.pyc` files plus macOS metadata

## Workflow

1. `analysis.py` filters the provider-service CMS file to RF ablation CPT codes.
2. `Medicare Physician & Other Practitioners - by Geography and Service/2023/data.py` filters the geography-service CMS file to the same CPT set.
3. `Medicare Physician & Other Practitioners - by Geography and Service/2023/summeries.py` builds numeric and categorical summaries from the filtered geography output.
4. `final.py` performs the main provider-side analysis, generates state and drug-service summaries, and writes the primary charts.
5. `rural.py` combines the summary tables into ZIP targeting and state opportunity outputs.

## Script Inventory

### `analysis.py`

- Purpose: filter the provider-service source file to RF ablation CPT codes.
- Input: a CMS provider-service CSV with an `HCPCS_Cd` column.
- Output: `Filtered_RF_Providers.csv`.
- Notes: the script now accepts `--input` and `--output` so the source file can live anywhere locally.

### `Medicare Physician & Other Practitioners - by Geography and Service/2023/data.py`

- Purpose: filter the geography-service source file to RF ablation CPT codes.
- Input: `MUP_PHY_R25_P05_V20_D23_Geo.csv`.
- Output: `Filtered_RF_Geography_Service.csv`.
- Notes: the script writes the filtered file back to the repository root for downstream use.

### `Medicare Physician & Other Practitioners - by Geography and Service/2023/summeries.py`

- Purpose: create data-quality summaries for the filtered geography file.
- Inputs: `Filtered_RF_Geography_Service.csv`.
- Outputs: `Numeric_Summary.csv` and `Categorical_Summary.csv` in the geography folder.

### `final.py`

- Purpose: run the main analysis on the filtered provider data.
- Inputs: `Filtered_RF_Providers.csv`.
- Outputs:
  - `us_summary.csv`
  - `cpt_summary.csv`
  - `state_summary.csv`
  - `comprehensive_state_analysis.csv`
  - `all_states_summary.csv`
  - `drug_service_analysis.csv`
  - `drug_service_summary.csv`
  - `provider_density_drug_correlation.csv`
  - `Numeric_Summary.csv`
  - `Categorical_Summary.csv`
  - `missing.csv`
  - `us_provider_density.png`
  - `us_provider_density_per_day.png`
  - `Visits_per_Provider.png`
  - `state_level_analysis_appendix.png`
  - `top5_state_gaps_facility.png`
  - `bottom5_state_gaps_facility.png`
  - `drug_services_by_state.png`
  - `provider_density_vs_drug_services.png`
  - `drug_services_heatmap.png`
  - `drug_services_boxplot.png`
- Notes: this is the main reporting script for the project.

### `rural.py`

- Purpose: produce state and ZIP targeting outputs from the summary tables.
- Inputs:
  - `RF_Procedure_Volume_by_CPT_and_Provider_Type.csv`
  - `State_Level_RF_Access_and_Distribution.csv`
  - `Opportunity_Index_by_ZIP.csv`
  - `Opportunity_Index_by_State.csv`
  - `Filtered_RF_Providers.csv`
- Outputs:
  - `Top_25_Target_ZIPs.csv`
  - `State_Target_ZIP_Counts.csv`
  - `Enhanced_Top_25_Target_ZIPs_with_Provider.csv`
- Notes: the script also shows two charts interactively with `plt.show()`.

## Current Data Products

### Provider-side outputs

- `Filtered_RF_Providers.csv`
- `us_summary.csv`
- `cpt_summary.csv`
- `state_summary.csv`
- `comprehensive_state_analysis.csv`
- `all_states_summary.csv`
- `drug_service_analysis.csv`
- `drug_service_summary.csv`
- `provider_density_drug_correlation.csv`

### Geography-side outputs

- `Filtered_RF_Geography_Service.csv`
- `Numeric_Summary.csv`
- `Categorical_Summary.csv`

### Targeting outputs

- `RF_Procedure_Volume_by_CPT_and_Provider_Type.csv`
- `State_Level_RF_Access_and_Distribution.csv`
- `Opportunity_Index_by_ZIP.csv`
- `Opportunity_Index_by_State.csv`
- `Top_25_Target_ZIPs.csv`
- `State_Target_ZIP_Counts.csv`
- `Enhanced_Top_25_Target_ZIPs_with_Provider.csv`

## Large Files

- `Medicare Physician & Other Practitioners - by Provider 2/2023/MUP_PHY_R25_P05_V20_D23_Prov.csv` is about 472.4 MB and should stay out of a normal GitHub repository.
- `Medicare Physician & Other Practitioners - by Geography and Service/2023/MUP_PHY_R25_P05_V20_D23_Geo.csv` is about 40.1 MB.
- `Filtered_RF_Providers.csv` is about 7.7 MB.

## Legacy Artifacts

The older or one-off outputs have been moved to `archive/legacy_outputs/`. They are useful as historical artifacts but should be treated separately from the core workflow:

- `top_disparity_states_summary.csv`
- `top_gap_states_facility.png`
- `top_gap_states_office.png`
- `state_gaps_facility.png`
- `state_gaps_office.png`
- `top10_state_gaps_facility.png`
- `bottom10_state_gaps_facility.png`
- `top_cpt_density.png`
- `cpt_density_heatmap.png`
- `drug_service_analysis.png`
- `Provider Density-Urban vs Rural.png`
- `Top RF Procedure Volumes.png`
- `Top 10 states by RF procedure Volumne.png`
- Screenshot captures from June and October 2025

## Cleanup Recommendations

- Initialize a Git repository before publishing.
- Keep the raw 472 MB provider CSV local, or store it outside the repo.
- Consider moving current outputs into a dedicated `outputs/` folder if you want the root to stay minimal.
- Remove `__pycache__` and `.DS_Store` files from the working tree when you are ready to commit.
