# RF Ablation Medicare Analysis

This project analyzes CMS Medicare Physician & Other Practitioners data to estimate RF ablation access, volume, and targeting opportunities across geography, provider type, and rural/urban context.

## What The Repo Does

- Filters raw CMS provider-service data to RF ablation CPT codes.
- Filters raw CMS geography-service data to the same CPT set.
- Generates numeric and categorical summaries for the filtered geography data.
- Builds national, state-level, and drug-service analyses from the filtered provider data.
- Identifies target ZIP codes and state-level opportunity counts.
- Produces charts and CSVs that support a final report or slide deck.

## Main Scripts

- `analysis.py` filters the provider-service source file down to RF CPT rows and writes `Filtered_RF_Providers.csv`.
- `Medicare Physician & Other Practitioners - by Geography and Service/2023/data.py` filters the geography-service source file and writes `Filtered_RF_Geography_Service.csv`.
- `Medicare Physician & Other Practitioners - by Geography and Service/2023/summeries.py` creates the numeric and categorical summary tables for the filtered geography file.
- `final.py` performs the main analysis pass on the filtered provider data and writes the core summary CSVs and figures.
- `rural.py` consumes the summary tables and builds ZIP targeting outputs plus state/state-gap visualizations.

## Data Inputs

- `Medicare Physician & Other Practitioners - by Provider 2/2023/MUP_PHY_R25_P05_V20_D23_Prov.csv` is a very large raw CMS source file and is too large to publish directly on GitHub.
- `Medicare Physician & Other Practitioners - by Geography and Service/2023/MUP_PHY_R25_P05_V20_D23_Geo.csv` is the geography-service source used by the geography filter script.
- `MUP_PHY_RY25_20250408_TBL_POS.xlsx` and the PDF files are supporting reference material.

## Outputs

The project currently writes a mix of derived CSVs and figures into the repository root and the geography subfolder. The main active outputs include:

- `Filtered_RF_Providers.csv`
- `Filtered_RF_Geography_Service.csv`
- `Numeric_Summary.csv`
- `Categorical_Summary.csv`
- `us_summary.csv`
- `cpt_summary.csv`
- `state_summary.csv`
- `comprehensive_state_analysis.csv`
- `all_states_summary.csv`
- `drug_service_analysis.csv`
- `drug_service_summary.csv`
- `provider_density_drug_correlation.csv`
- `RF_Procedure_Volume_by_CPT_and_Provider_Type.csv`
- `State_Level_RF_Access_and_Distribution.csv`
- `Opportunity_Index_by_ZIP.csv`
- `Opportunity_Index_by_State.csv`
- `Top_25_Target_ZIPs.csv`
- `State_Target_ZIP_Counts.csv`
- `Enhanced_Top_25_Target_ZIPs_with_Provider.csv`
- The PNG charts written by `final.py` and `rural.py`

## Run Order

1. Install dependencies with `pip install -r requirements.txt`.
2. Run the geography filter:
   `python "Medicare Physician & Other Practitioners - by Geography and Service/2023/data.py"`
3. Run the geography summary script:
   `python "Medicare Physician & Other Practitioners - by Geography and Service/2023/summeries.py"`
4. Run the provider filter with the correct provider-service CSV path:
   `python analysis.py --input /path/to/MUP_PHY_R25_P05_V20_D23_Prov_Svc.csv`
5. Run the main analysis:
   `python final.py`
6. Run the targeting pass:
   `python rural.py`

## Repo Hygiene

- `.gitignore` excludes Python cache files, macOS metadata, and the large raw provider CSV so the repo stays GitHub-friendly.
- Historical screenshots and legacy charts are archived in `archive/legacy_outputs/`; the detailed inventory in `docs/PROJECT_REPORT.md` separates current outputs from older files.

## Detailed Inventory

See [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md) for the file-by-file report and notes on legacy artifacts.
