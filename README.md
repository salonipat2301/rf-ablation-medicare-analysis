# RF Ablation Medicare Access & Distribution Analysis

## Objective and aim

The objective of this repository is to describe how Medicare RF-ablation treatment is distributed across states, facilities and offices, and rural/urban areas.

The aim is to help viewers identify differences in service volume, beneficiaries served, provider availability, and possible geographic access gaps. The analysis is descriptive: it highlights patterns for further review and does not prove unmet need, clinical quality, causation, or market opportunity.

## What the analysis does

The analysis filters 2023 CMS Medicare Physician & Other Practitioners records to the RF-ablation-related HCPCS/CPT codes used in the project. It then summarizes services, beneficiaries, beneficiary-day services, and distinct providers by state, place of service, rural/urban context, procedure code, and ZIP code. It calculates provider-density and workload measures, compares urban and rural patterns, and creates an opportunity screen for ZIP codes with relatively high activity and few providers.

The main question is: **Where is RF-ablation Medicare activity concentrated, and which places may warrant a closer look for access planning?**

## Report

Read the published report: [`Report on Treatment Access & Distribution Analysis.pdf`](Report%20on%20Treatment%20%26%20Distribution%20Analysis.pdf)

The report uses CMS Medicare Physician & Other Practitioners data for 2023 and focuses on RF-ablation-related HCPCS/CPT codes. In the figures, `F` means facility and `O` means office. “Urban” and “Rural” are analysis groupings derived from CMS RUCA descriptions.

## Conclusions from the report

- RF-ablation activity is concentrated in urban settings and in a relatively small number of higher-volume states. Rural and small-town areas account for much less recorded activity and have fewer identified providers.
- The rural/urban comparisons indicate potential distribution gaps: some rural areas serve beneficiaries with a small provider base, which can mean a higher workload per provider and less redundancy in local access.
- The ZIP-code screening results identify rural, micropolitan, and small-town ZIPs—often with one recorded provider—as places for follow-up. These are leads for investigation, not confirmed access shortages.
- Facility and office activity are distributed differently by geography, so “access” should not be interpreted from service volume alone; setting, provider count, and beneficiary counts need to be considered together.
- The drug-service indicator is zero in the filtered RF-ablation extract. The drug-service plots therefore do not provide a meaningful drug-mix conclusion for this analysis and should not be used as evidence about treatment access.
- The findings describe Medicare utilization in 2023. They should be validated with current data, local travel/access information, payer mix, capacity, and clinical context before making decisions.

## Assumptions and limitations

- The results represent recorded 2023 Medicare activity, not all-payer demand or total access.
- A provider is counted by distinct `Rndrng_NPI` within each summary.
- Beneficiary-day services are used as an activity/visit proxy; they are not the same as unique patients.
- Provider density is a ratio, not a measure of travel time, capacity, quality, or appointment availability.
- Facility and office comparisons are not risk-adjusted.
- Missing RUCA descriptions and a small number of geographic values are handled by project-specific rules in `final.py`.
- Opportunity scores are screening indicators only and should not be treated as proof of unmet need or profitability.
- Small counts can produce unstable ratios, so results should be interpreted with the underlying counts in mind.
