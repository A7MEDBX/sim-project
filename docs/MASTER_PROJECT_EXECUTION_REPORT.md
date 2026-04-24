# Master Project Execution Report

## Project Status
This repository now runs as one connected pipeline from implementation to QA.

## Connected Flow
1. Core simulation executes demand scenarios.
2. Validation checks run on edge and stress cases.
3. Analysis and plots are generated from scenario outputs.
4. Packaging docs are generated.
5. QA verifies all required artifacts and trends.

## Final Scenario Metrics
| Scenario | Avg Wait | Avg Throughput | Avg Utilization |
| --- | ---: | ---: | ---: |
| low | 4.4086 | 0.3867 | 0.2153 |
| medium | 4.7519 | 0.8067 | 0.4672 |
| high | 13.3662 | 1.2200 | 0.8167 |

## QA Summary
- QA checks passed: 6/6

## Key Artifacts
- docs/FINAL_PROJECT_REPORT.md
- docs/PRESENTATION_OUTLINE.md
- docs/PHASES_1_2_3_REPORT.md
- docs/PHASES_4_5_6_REPORT.md
- docs/PHASES_7_8_9_REPORT.md
- results/summary_metrics.csv
- results/phase5_validation_results.csv
- results/phase6_scenario_averages.csv
- results/phase7_waiting_vs_demand.png
- results/phase7_throughput_vs_demand.png
- results/phase7_utilization_vs_demand.png
- results/phase9_qa_results.csv