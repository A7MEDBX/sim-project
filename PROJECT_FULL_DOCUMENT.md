# Ride-Sharing System Simulation

## 1. Project Overview
This project simulates a ride-sharing platform in a virtual city. The objective is to model and analyze system behavior under changing demand and supply, not to build a mobile app.

The simulation includes:
- Passenger request arrivals over time
- Driver availability and movement
- Matching logic between requests and drivers
- Queueing and cancellation behavior
- Performance metrics across scenarios

## 2. Objectives
- Build a realistic dynamic-system model
- Implement a working Python simulation
- Analyze outcomes across controlled scenarios
- Identify bottlenecks and efficiency trends

## 3. Scope
Included:
- Poisson request arrivals
- Driver fleet with car types (economy, premium, van)
- Nearest compatible driver matching
- Request queue with max-wait cancellation
- Core metrics and scenario comparison

Excluded:
- Traffic and road graph constraints
- Dynamic pricing
- AI optimization models
- External map APIs

## 4. Core Entities
### 4.1 Request
Fields:
- request_id
- request_time
- pickup_x, pickup_y
- dest_x, dest_y
- car_type
- status (waiting, in_trip, completed, canceled)
- match_time
- pickup_time
- dropoff_time
- driver_id

### 4.2 Driver
Fields:
- driver_id
- car_type
- x, y
- speed
- status (idle, busy)
- available_time
- busy_start_time
- busy_time
- current_request_id

### 4.3 Simulation Controller
Responsibilities:
- Generate requests each timestep
- Update queue and cancellations
- Release completed drivers
- Match waiting requests
- Compute times and update states
- Record outputs and aggregate metrics

## 5. Inputs
- simulation_time: total horizon in seconds
- num_drivers: number of drivers
- arrival_rate_lambda: average requests per second
- city_size: city boundaries [0, city_size]
- max_wait_time: cancellation threshold in seconds
- driver_speed: distance units per second
- demand and supply type distributions

Optional demand realism:
- hotspot_ratio
- hotspot_center

## 6. Simulation Flow
For each time t from 0 to simulation_time:
1. Release drivers whose dropoff_time <= t
2. Generate Poisson arrivals for requests
3. Add requests to queue
4. Cancel requests where t - request_time > max_wait_time
5. Match queue requests to nearest compatible idle drivers
6. Compute pickup/trip/dropoff times for matches
7. Update driver and request states
8. Record events

## 7. Mathematical Model
Distance:

d = sqrt((x1 - x2)^2 + (y1 - y2)^2)

Pickup travel time:

T_pickup = d_driver_to_pickup / v

Trip travel time:

T_trip = d_pickup_to_dest / v

Times:

pickup_time = match_time + T_pickup

dropoff_time = pickup_time + T_trip

Delays:

matching_delay = match_time - request_time

passenger_wait = pickup_time - request_time

Service model:

S = T_pickup + T_trip

mu = 1 / E[S]

Load:

rho = lambda / (c * mu)

## 8. Queue and Matching Policies
Queue policy:
- Requests stay waiting until matched or canceled
- Cancel if waiting exceeds max_wait_time

Matching policy:
- Candidate drivers must be idle and type-compatible
- Select the nearest candidate by Euclidean distance
- If none available, request remains in queue

## 9. Output Data
### 9.1 Requests output
- Request fields plus assigned times, driver_id, status

### 9.2 Drivers output
- Driver final state and accumulated busy_time

### 9.3 Summary metrics
- total_requests
- completed_requests
- canceled_requests
- completion_rate
- cancellation_rate
- avg_matching_delay
- avg_passenger_wait
- avg_trip_time
- throughput
- utilization

## 10. Experiments
Baseline experiments:
- Low demand scenario
- Medium demand scenario
- High demand scenario

For each scenario:
- Run multiple seeds
- Compute average KPI values
- Compare trend behavior

## 11. Validation
Sanity checks:
- lambda = 0 should produce no waiting and no completions
- very high driver count should reduce waiting and cancellation
- high lambda with fixed drivers should increase waiting and utilization

## 12. Expected Insights
- Higher demand increases waiting and cancellation risk
- Higher driver utilization indicates tighter capacity
- Throughput rises with demand until saturation limits are reached

## 13. How to Run
1. Run the simulation script:
   python src/simulation.py
2. Outputs are generated in the results folder.
3. Use produced CSV files for MATLAB plotting.
