# Phases 4 to 6 Implementation Report

## Scope
This report documents execution of:
- Phase 4: Core simulation implementation
- Phase 5: Verification and validation
- Phase 6: Experiment campaign

Status: Completed.

## Phase 4: Core Simulation Implementation

### What was implemented
The simulation engine in src/simulation.py includes:
- Driver and request data models
- Time evolution loop from t=0 to simulation_time
- Poisson request generation using arrival_rate_lambda
- Queue handling with max_wait_time cancellation
- Nearest compatible driver matching by Euclidean distance
- Driver state transitions (idle, busy)
- Request state transitions (waiting, in_trip, completed, canceled)
- KPI calculation and CSV export

### Execution output
The implementation produced:
- Per run request files in results folder
- Run-level metrics in results/summary_metrics.csv

### Phase 4 completion result
Core simulation runs end-to-end and exports valid structured outputs.

## Phase 5: Verification and Validation

### Validation runner
Validation was implemented and executed through src/run_phases_5_6.py.
Validation results were written to results/phase5_validation_results.csv.

### Validation cases and outcomes
1. lambda_zero
- Expected: no requests generated
- Observed: total_requests=0.0, completed_requests=0.0, canceled_requests=0.0
- Result: PASS

2. high_driver_supply
- Expected: near zero matching delay and zero cancellation
- Observed: total_requests=209.0, avg_matching_delay=0.0, cancellation_rate=0.0
- Result: PASS

3. overloaded_system
- Expected: worse delay or cancellation than medium reference
- Reference: avg_matching_delay=0.04060913705583756, cancellation_rate=0.0
- Observed: avg_matching_delay=3.230612244897959, cancellation_rate=0.11205432937181664
- Result: PASS

### Phase 5 completion result
All defined validation checks passed, and behavior trends match simulation assumptions.

## Phase 6: Experiment Campaign

### Experiment setup
- Scenarios: low, medium, high demand
- Arrival rates: 0.5, 1.0, 2.0
- Seeds per scenario: 1, 2, 3
- Output files:
  - results/summary_metrics.csv
  - results/phase6_scenario_averages.csv

### Averaged results by scenario
From results/phase6_scenario_averages.csv:

1. Low demand
- avg_total_requests: 93.33333333333333
- avg_completed_requests: 92.33333333333333
- avg_completion_rate: 0.989179930651293
- avg_cancellation_rate: 0.0
- avg_matching_delay: 0.0
- avg_passenger_wait: 1.0588634899274572
- avg_throughput: 0.46166666666666667
- avg_utilization: 0.05357508269059364

2. Medium demand
- avg_total_requests: 194.33333333333334
- avg_completed_requests: 190.0
- avg_completion_rate: 0.9779239830060353
- avg_cancellation_rate: 0.0
- avg_matching_delay: 0.015409038194642483
- avg_passenger_wait: 1.188802006835224
- avg_throughput: 0.9500000000000001
- avg_utilization: 0.11191868067857863

3. High demand
- avg_total_requests: 410.6666666666667
- avg_completed_requests: 397.0
- avg_completion_rate: 0.9664705620969519
- avg_cancellation_rate: 0.001670843776106934
- avg_matching_delay: 0.4152400058796856
- avg_passenger_wait: 1.8149456573148612
- avg_throughput: 1.985
- avg_utilization: 0.24427334124236735

### Key observations
- Demand increase raised throughput and utilization strongly.
- Matching delay stayed near zero in low and medium, then increased significantly in high demand.
- Passenger wait increased from low to high demand.
- Cancellation remained low but became nonzero under highest demand.

### Phase 6 completion result
Experiment campaign completed successfully and produced consistent demand-vs-performance trends.

## Final Status After Phases 4 to 6
- Phase 4: Completed
- Phase 5: Completed
- Phase 6: Completed

The project is now ready to continue with Phase 7 analysis and visualization workflow using the generated result files.
