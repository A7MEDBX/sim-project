# Ride-Sharing Simulation Project

This project is now connected as one end-to-end pipeline, from simulation execution to validation, analysis, packaging, and QA.

## One-command full run
From the project root:

`c:/Simulation_Project/.venv/Scripts/python.exe src/run_full_project.py`

This command will:
1. Run experiments (low, medium, high demand)
2. Run validation checks
3. Generate analysis outputs and plots
4. Build final docs and presentation outline
5. Run final QA checks
6. Generate a single master execution report

## Core files
- PROJECT_FULL_DOCUMENT.md
- docs/PHASES_1_2_3_REPORT.md
- docs/PHASES_4_5_6_REPORT.md
- docs/PHASES_7_8_9_REPORT.md
- docs/FINAL_PROJECT_REPORT.md
- docs/PRESENTATION_OUTLINE.md
- docs/MASTER_PROJECT_EXECUTION_REPORT.md
- src/simulation.py
- src/run_full_project.py

## Main outputs
- results/summary_metrics.csv
- results/phase5_validation_results.csv
- results/phase6_scenario_averages.csv
- results/phase7_waiting_vs_demand.png
- results/phase7_throughput_vs_demand.png
- results/phase7_utilization_vs_demand.png
- results/phase9_qa_results.csv

## Optional MATLAB plotting
If you want MATLAB versions of plots, run:

`run('matlab/plot_results.m')`
