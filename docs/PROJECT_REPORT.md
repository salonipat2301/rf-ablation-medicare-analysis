# Report and plot field guide

This is the compact field guide for the published PDF, [`Report on Treatment Access & Distribution Analysis.pdf`](../Report%20on%20Treatment%20Access%20%26%20Distribution%20Analysis.pdf). It documents only the fields needed to understand the report’s plots and summary tables.

## Report objective

Describe Medicare RF-ablation treatment distribution and surface possible access differences by state, care setting, and rural/urban context. The analysis is descriptive and intended to support questions for follow-up.

## Plot-facing fields

| Field | Meaning in this repository | Used for |
|---|---|---|
| `HCPCS_Cd` | RF procedure code | Procedure-volume comparisons |
| `Rndrng_Prvdr_State_Abrvtn` | Provider state abbreviation | State comparisons |
| `Rndrng_Prvdr_Zip5` | Provider ZIP code | ZIP-level opportunity screening |
| `Place_Of_Srvc` | CMS place-of-service code (`F` facility, `O` office) | Setting comparisons |
| `Rndrng_Prvdr_RUCA_Desc` | CMS RUCA description | Rural/urban classification |
| `Urban_Rural` | Derived grouping from RUCA description | Rural/urban plots |
| `Tot_Srvcs` / `Total_Services` | Reported services | Volume and utilization |
| `Tot_Benes` / `Total_Beneficiaries` | Reported beneficiaries | Population served |
| `Tot_Bene_Day_Srvcs` / `Total_Beneficiary_Days` | Reported beneficiary-day services | Visit/activity proxy |
| `Rndrng_NPI` / `Unique_Providers` | Provider identifier and distinct-provider count | Provider access measures |
| `Provider_Coverage` | `Unique_Providers / Total_Beneficiaries` | National setting comparison |
| `Provider_Density_Per_Day` | `Unique_Providers / Total_Beneficiary_Days` | National setting comparison |
| `Provider_Density` | `Unique_Providers / Total_Beneficiaries` in state/CPT summaries | State and procedure comparisons |
| `Visits_per_Provider` | `Total_Beneficiary_Days / Unique_Providers` | Provider workload proxy |
| `Gap_Ratio` | Urban provider density divided by rural provider density | State gap comparison |
| `Drug_Services` | Services flagged as drug services in the source | Service-mix analysis |
| `Drug_Service_Pct` | `Drug_Services / Total_Services * 100` | Service-mix plots |
| `Opportunity_Index` | Derived ZIP screening score | Targeting screen |
| `Total_Providers` / `Num_Target_ZIPs` | Provider count and selected ZIP count | Targeting summaries |

The detailed provider identity, address, credential, payment, and source metadata columns remain in the filtered data for traceability, but they are not required to read the report plots.

## Source and transformation path

1. CMS provider-service data is filtered to HCPCS/CPT codes `64633`, `64634`, `64635`, `64636`, `64624`, `64625`, `64640`, and `77002` by `analysis.py`.
2. The CMS geography-service extract is filtered by `Medicare Physician & Other Practitioners - by Geography and Service/2023/data.py`.
3. `final.py` aggregates the filtered provider rows by setting, state, RUCA grouping, and service mix, then writes the report-facing CSVs and PNGs.
4. `rural.py` applies the ZIP/state screening logic and writes targeting outputs.

## Interpretation notes

The counts describe 2023 Medicare activity captured by CMS. They are not estimates of all-payer demand, total patients, clinician capacity, travel burden, or unmet need. Ratios can be unstable where counts are small or zero. RUCA imputation and project-specific geographic corrections occur in `final.py`; any comparison involving rural/urban labels should be read with that assumption in mind.

## Main report-facing outputs

- `us_summary.csv` — national setting and rural/urban measures.
- `state_summary.csv` and `comprehensive_state_analysis.csv` — state-level provider and gap measures.
- `drug_service_analysis.csv` and `drug_service_summary.csv` — service-mix measures.
- `Opportunity_Index_by_ZIP.csv`, `Top_25_Target_ZIPs.csv`, and `State_Target_ZIP_Counts.csv` — screening outputs.
- PNG files in the repository root — figures used by the analysis workflow.
