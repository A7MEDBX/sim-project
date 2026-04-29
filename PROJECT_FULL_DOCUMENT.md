# Ride-Sharing System Simulation - Complete Master Documentation

## 1. Project Overview & Executive Summary
This project simulates a dynamic ride-sharing platform in a 2D virtual city environment. The objective is to construct a rigorous mathematical and probabilistic model of ride-sharing systems, evaluating system behavior under varying constraints such as demand (arrival rates), supply (driver availability), and service capacity.

This project was built incrementally across 9 phases:
*   **Phases 1-3:** Mathematical formulation, probabilistic modeling, and architecture design.
*   **Phases 4-6:** Python-based simulation engine development, boundary testing, and output aggregation.
*   **Phases 7-9:** Graphic visualization (MATLAB & Python inline), quality assurance (QA), and final packaging.

---

## 2. Mathematical Foundation & Physics Engine

The simulation is strictly governed by a mathematical engine that dictates object movement, arrival likelihoods, and performance evaluations.

### 2.1. Spatial Physics
The city is modeled as a Cartesian grid ($D \times D$). 
**Distance:** The physical distance $d$ between two coordinates $(x_1,y_1)$ and $(x_2,y_2)$ is straight-line Euclidean:
$$d = \sqrt{(x_1 - x_2)^2 + (y_1 - y_2)^2}$$

### 2.2. Temporal Mathematics
Given a constant driver speed ($s$), the time it takes to travel is calculated as:
**Pickup Travel Time:**
$$T_{pickup} = \frac{distance(driver, pickup)}{speed}$$

**Trip Travel Time:**
$$T_{trip} = \frac{distance(pickup, destination)}{speed}$$

Timeline mapping for a request:
$$pickup\_time = match\_time + T_{pickup}$$
$$dropoff\_time = pickup\_time + T_{trip}$$

### 2.3. Queueing & Performance Metrics
We measure the efficiency of the ride-sharing queue using standard operational metrics.
**Matching Delay:**	$$D_{match} = match\_time - request\_time$$
**Passenger Waiting Time:** $$W = pickup\_time - request\_time$$
**Trip Duration:** $$Trip\_time = dropoff\_time - pickup\_time$$
**Total Service Time:** $$S = T_{pickup} + T_{trip}$$
**Service Rate:** $$\mu = \frac{1}{\mathbb{E}[S]}$$
**System Load:** $$\rho = \frac{\lambda}{c \times \mu}$$ 

**Throughput:** $$Throughput = \frac{number\_of\_completed\_requests}{simulation\_time}$$
**Driver Utilization:** $$Utilization = \frac{total\_driver\_busy\_time}{number\_of\_drivers \times simulation\_time}$$
**Completion Rate:** $$Completion\_rate = \frac{completed\_requests}{total\_requests}$$
**Cancellation Rate:** $$Cancellation\_rate = \frac{canceled\_requests}{total\_requests}$$

### 2.4. Demand Generation (Poisson Process)
Customer ride requests enter the system governed by a generic Poisson distribution where $\lambda$ is the expected arrival rate per time-step:
$$ P(X=k) = \frac{\lambda^k e^{-\lambda}}{k!} $$

---

## 3. Simulation Architecture

### 3.1. Core Entities
*   **Request Object:** Tracks `request_id`, coordinates (`pickup_x, pickup_y, dest_x, dest_y`), requested `car_type`, constraints, and time lifecycles (`match_time`, `pickup_time`, `dropoff_time`).
*   **Driver Object:** Tracks `driver_id`, vehicle `car_type`, current coordinates, and exact availability scheduling (`busy_time`, `available_time`).

### 3.2. Lifecycle Loop
For every discrete time step $t$ from $0 \rightarrow T$:
1.  **Release:** Check all `busy` drivers. If their `available_time` $\le t$, free them to `idle`.
2.  **Generate:** Draw $k$ from the Poisson distribution ($\lambda$). Spawn $k$ `Request` objects with randomly assigned spatial coordinates.
3.  **Clean:** Scan the queue. If $t - request\_time > max\_wait\_time$, strictly mark the request as `canceled`.
4.  **Match:** For each waiting request, identify all `idle` drivers where `driver.car_type == request.car_type`. Select the driver with the minimum Euclidean distance. Calculate and lock their future trajectory.

---

## 4. Phase 5 & 6: Validation, Quality Assurance & Aggregation

To ensure the mathematical validity of the engine, strict boundary constraints are enforced and tested:
1.  **Zero-Demand Check ($\lambda=0$):** Validates that exactly $0$ requests are matched, canceled, or generated. 
2.  **Over-supply Check (Drivers=120):** Confirms that cancellation rates drop to $0\%$ and matching delay is near instant.
3.  **Overloaded System ($\lambda=3.0$, Drivers=20):** Confirms that queue limits behave correctly, enforcing high passenger wait times and high cancellation tracking.

For final deliverables, the system loops over $3$ distinct seeds across $\lambda \in \{0.5, 1.0, 2.0\}$ ("low", "medium", "high"), generating a `summary_metrics.csv` containing the aggregated averages.

---

## 5. Phase 7: Graphical Analysis

Data is plotted using Python's `matplotlib` (and/or MATLAB scripts) to extract hardware-agnostic behavior limits:
*   **Waiting Time vs Demand:** Wait times predictably curve upward as $\lambda$ grows and drivers exhaust.
*   **Throughput vs Demand:** Demonstrates system capacity constraints. Throughput eventually plateaus (bottlenecks) based on fleet limits.
*   **Utilization vs Demand:** utilization tracks $\rho$. High demand scenarios push the driver fleet to $\sim 100\%$ operational busy-time.

---

## 6. How to Run the Project

You may execute the project in two distinct ways:

### Method 1: Python CLI Pipeline
Run the modular simulation:
```bash
python src/simulation.py
```
This produces decoupled `results/requests_*.csv` datasets, `summary_metrics.csv`, outputs, and `.png` graph generations. 

### Method 2: Jupyter Master Notebook
Open and run **`Ride_Sharing_Simulation.ipynb`**. 
This single file acts as the entire autonomous monolithic pipeline. It houses the Markdown mathematical formulas, natively runs the Poisson/Euclidean engine, aggregates the metrics in-memory, visualizes the exact line charts inline, and prints the QA execution report continuously without needing external scripts.