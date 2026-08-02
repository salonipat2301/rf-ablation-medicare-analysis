# RF Ablation Medicare Access & Distribution Analysis

## Objective and aim

The objective of this repository is to describe how Medicare RF-ablation treatment is distributed across states, facilities and offices, and rural/urban areas.

The aim is to help viewers identify differences in service volume, beneficiaries served, provider availability, and possible geographic access gaps. The analysis is descriptive: it highlights patterns for further review and does not prove unmet need, clinical quality, causation, or market opportunity.

## Report

Read the published report: [`Report on Treatment Access & Distribution Analysis.pdf`](Report%20on%20Treatment%20%26%20Distribution%20Analysis.pdf)

The report uses CMS Medicare Physician & Other Practitioners data for 2023 and focuses on RF-ablation-related HCPCS/CPT codes. In the figures, `F` means facility and `O` means office. “Urban” and “Rural” are analysis groupings derived from CMS RUCA descriptions.

## Assumptions and limitations

- The results represent recorded 2023 Medicare activity, not all-payer demand or total access.
- A provider is counted by distinct `Rndrng_NPI` within each summary.
- Beneficiary-day services are used as an activity/visit proxy; they are not the same as unique patients.
- Provider density is a ratio, not a measure of travel time, capacity, quality, or appointment availability.
- Facility and office comparisons are not risk-adjusted.
- Missing RUCA descriptions and a small number of geographic values are handled by project-specific rules in `final.py`.
- Opportunity scores are screening indicators only and should not be treated as proof of unmet need or profitability.
- Small counts can produce unstable ratios, so results should be interpreted with the underlying counts in mind.
