# RF Ablation Medicare Access & Distribution Analysis

## Objective

This repository evaluates where Medicare RF-ablation services are being delivered and where access may be uneven. It uses CMS Medicare Physician & Other Practitioners data to compare service volume, beneficiaries, providers, and provider density across states, place of service, and rural/urban context. The intended use is descriptive planning: identify patterns that deserve further investigation, not make a clinical, quality, or causal claim.

## Published report

Read the report: [`Report on Treatment Access & Distribution Analysis.pdf`](Report%20on%20Treatment%20Access%20%26%20Distribution%20Analysis.pdf)

The report’s figures are generated from the plot-facing summary fields documented in [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md). The raw files contain additional columns, but those columns are not needed to interpret the charts.

## What viewers should look at

- **Access and volume:** `Total_Services`, `Total_Beneficiaries`, `Total_Beneficiary_Days`, and `Unique_Providers`.
- **Provider measures:** `Provider_Coverage`, `Provider_Density_Per_Day`, `Provider_Density`, and `Visits_per_Provider`.
- **Geography and setting:** `Rndrng_Prvdr_State_Abrvtn`, `Rndrng_Prvdr_Zip5`, `Place_Of_Srvc`, and `Urban_Rural`.
- **Procedure and mix:** `HCPCS_Cd`, `Drug_Services`, and `Drug_Service_Pct`.
- **Targeting:** `Opportunity_Index`, `Total_Providers`, and `Num_Target_ZIPs`.

In the charts, `F` means facility and `O` means office. “Urban” and “Rural” are derived from the CMS RUCA description; they are analysis groupings, not a new CMS geographic designation.

## Data sources

The primary source is the CMS [Medicare Physician & Other Practitioners — by Provider and Service](https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider-and-service) dataset for 2023. The analysis also uses the CMS geography-and-service extract in `Medicare Physician & Other Practitioners - by Geography and Service/2023/`.

The provider-service raw CSV is intentionally not committed because it is hundreds of megabytes. Download it from CMS and pass its local path to `analysis.py`. The repository includes filtered and aggregated outputs so the published figures can be reviewed without downloading the raw provider file.

RF procedure rows are selected using these HCPCS/CPT codes: `64633`, `64634`, `64635`, `64636`, `64624`, `64625`, `64640`, and `77002`. The code list is a project definition of the RF-ablation scope; it should be reviewed against the current coding guidance before reuse.

## Assumptions and limitations

- CMS utilization is treated as a description of recorded Medicare activity, not total clinical demand or total access.
- A provider is counted by distinct `Rndrng_NPI` within each aggregation.
- Provider density is a ratio of providers to the relevant beneficiary or beneficiary-day count; it is not a travel-time or capacity measure.
- `Tot_Bene_Day_Srvcs` is used as a beneficiary-day/visit proxy in several measures. It should not be interpreted as unique patients.
- Place of service is retained as CMS reports it; facility and office comparisons are not risk-adjusted.
- Missing RUCA descriptions are imputed in `final.py`, and a small number of known geographic values are corrected there. These transformations can affect rural/urban comparisons.
- Opportunity scores are screening indicators built from the available utilization and provider fields. They do not establish unmet need, profitability, or causation.
- Results describe the 2023 extract and may not represent current utilization.

## Reproduce the analysis

```bash
pip install -r requirements.txt
python analysis.py --input /path/to/MUP_PHY_R25_P05_V20_D23_Prov_Svc.csv
python final.py
python rural.py
```

The geography filter and summary scripts are documented in [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md). Run them when regenerating the geography-based outputs.

## Repository map

- `analysis.py` filters provider-service rows to the RF procedure scope.
- `final.py` creates the national, state, rural/urban, and drug-service summaries and plots.
- `rural.py` creates ZIP/state opportunity outputs.
- `Filtered_RF_Providers.csv` and the summary CSVs are derived data products, not independent source data.
- `archive/legacy_outputs/` contains historical figures that are not part of the current report.
