from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import csv
import math
import random


CAR_TYPES = ("economy", "premium", "van")


@dataclass
class SimulationParams:
    simulation_time: int = 100
    num_drivers: int = 20
    arrival_rate_lambda: float = 1.0
    city_size: int = 20
    max_wait_time: int = 20
    driver_speed: float = 1.5
    driver_type_probs: Dict[str, float] = None
    request_type_probs: Dict[str, float] = None
    hotspot_ratio: float = 0.0
    driver_hotspot_ratio: float = 0.0
    hotspot_center: Tuple[float, float] = (5.0, 5.0)

    def __post_init__(self) -> None:
        if self.driver_type_probs is None:
            self.driver_type_probs = {"economy": 0.7, "premium": 0.2, "van": 0.1}
        if self.request_type_probs is None:
            self.request_type_probs = {"economy": 0.7, "premium": 0.2, "van": 0.1}


@dataclass
class Driver:
    driver_id: int
    car_type: str
    x: float
    y: float
    speed: float
    status: str = "idle"
    available_time: float = 0.0
    busy_start_time: float = 0.0
    busy_time: float = 0.0
    current_request_id: Optional[int] = None
    next_x: Optional[float] = None
    next_y: Optional[float] = None


@dataclass
class Request:
    request_id: int
    request_time: int
    pickup_x: float
    pickup_y: float
    dest_x: float
    dest_y: float
    car_type: str
    status: str = "waiting"
    match_time: Optional[float] = None
    pickup_time: Optional[float] = None
    dropoff_time: Optional[float] = None
    driver_id: Optional[int] = None


def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def poisson_sample(lam: float, rng: random.Random) -> int:
    if lam <= 0:
        return 0
    l_val = math.exp(-lam)
    k = 0
    p = 1.0
    while p > l_val:
        k += 1
        p *= rng.random()
    return k - 1


def weighted_choice(prob_map: Dict[str, float], rng: random.Random) -> str:
    threshold = rng.random()
    cumulative = 0.0
    for key in CAR_TYPES:
        cumulative += prob_map[key]
        if threshold <= cumulative:
            return key
    return CAR_TYPES[-1]


def sample_location(
    params: SimulationParams,
    rng: random.Random,
    hotspot_ratio: Optional[float] = None,
) -> Tuple[float, float]:
    ratio = params.hotspot_ratio if hotspot_ratio is None else hotspot_ratio
    if rng.random() < ratio:
        center_x, center_y = params.hotspot_center
        x = min(max(center_x + rng.uniform(-1.5, 1.5), 0.0), float(params.city_size))
        y = min(max(center_y + rng.uniform(-1.5, 1.5), 0.0), float(params.city_size))
        return x, y
    return rng.uniform(0.0, float(params.city_size)), rng.uniform(0.0, float(params.city_size))


def init_drivers(params: SimulationParams, rng: random.Random) -> List[Driver]:
    drivers: List[Driver] = []
    for idx in range(params.num_drivers):
        x, y = sample_location(params, rng, params.driver_hotspot_ratio)
        drivers.append(
            Driver(
                driver_id=idx + 1,
                car_type=weighted_choice(params.driver_type_probs, rng),
                x=x,
                y=y,
                speed=params.driver_speed,
            )
        )
    return drivers


def release_completed_drivers(current_time: int, drivers: List[Driver], request_map: Dict[int, Request]) -> None:
    for driver in drivers:
        if driver.status == "busy" and driver.available_time <= current_time:
            driver.status = "idle"
            driver.busy_time += max(0.0, driver.available_time - driver.busy_start_time)

            if driver.current_request_id is not None:
                request_map[driver.current_request_id].status = "completed"

            if driver.next_x is not None and driver.next_y is not None:
                driver.x = driver.next_x
                driver.y = driver.next_y

            driver.current_request_id = None
            driver.next_x = None
            driver.next_y = None


def cancel_overdue_requests(
    current_time: int,
    queue: List[int],
    request_map: Dict[int, Request],
    max_wait_time: int,
) -> List[int]:
    remaining: List[int] = []
    for req_id in queue:
        req = request_map[req_id]
        if req.status != "waiting":
            continue
        if current_time - req.request_time > max_wait_time:
            req.status = "canceled"
        else:
            remaining.append(req_id)
    return remaining


def match_requests(
    current_time: int,
    queue: List[int],
    drivers: List[Driver],
    request_map: Dict[int, Request],
) -> List[int]:
    still_waiting: List[int] = []

    for req_id in queue:
        req = request_map[req_id]
        if req.status != "waiting":
            continue

        candidates = [
            d
            for d in drivers
            if d.status == "idle" and d.car_type == req.car_type
        ]

        if not candidates:
            still_waiting.append(req_id)
            continue

        best_driver = min(
            candidates,
            key=lambda d: euclidean_distance(d.x, d.y, req.pickup_x, req.pickup_y),
        )

        pickup_distance = euclidean_distance(best_driver.x, best_driver.y, req.pickup_x, req.pickup_y)
        trip_distance = euclidean_distance(req.pickup_x, req.pickup_y, req.dest_x, req.dest_y)

        pickup_time = float(current_time) + pickup_distance / best_driver.speed
        dropoff_time = pickup_time + trip_distance / best_driver.speed

        req.match_time = float(current_time)
        req.pickup_time = pickup_time
        req.dropoff_time = dropoff_time
        req.driver_id = best_driver.driver_id
        req.status = "in_trip"

        best_driver.status = "busy"
        best_driver.busy_start_time = float(current_time)
        best_driver.available_time = dropoff_time
        best_driver.current_request_id = req.request_id
        best_driver.next_x = req.dest_x
        best_driver.next_y = req.dest_y

    return still_waiting


def mean(values: List[float]) -> float:
    return (sum(values) / len(values)) if values else 0.0


def compute_metrics(params: SimulationParams, drivers: List[Driver], requests: List[Request]) -> Dict[str, float]:
    completed = [r for r in requests if r.status == "completed"]
    canceled = [r for r in requests if r.status == "canceled"]

    matching_delay = [r.match_time - r.request_time for r in completed if r.match_time is not None]
    passenger_wait = [r.pickup_time - r.request_time for r in completed if r.pickup_time is not None]
    trip_time = [
        r.dropoff_time - r.pickup_time
        for r in completed
        if r.dropoff_time is not None and r.pickup_time is not None
    ]

    total_busy = 0.0
    for driver in drivers:
        busy = driver.busy_time
        if driver.status == "busy":
            capped_available = min(driver.available_time, float(params.simulation_time))
            busy += max(0.0, capped_available - driver.busy_start_time)
        total_busy += busy

    horizon = max(1, params.simulation_time)

    return {
        "total_requests": float(len(requests)),
        "completed_requests": float(len(completed)),
        "canceled_requests": float(len(canceled)),
        "completion_rate": (len(completed) / len(requests)) if requests else 0.0,
        "cancellation_rate": (len(canceled) / len(requests)) if requests else 0.0,
        "avg_matching_delay": mean(matching_delay),
        "avg_passenger_wait": mean(passenger_wait),
        "avg_trip_time": mean(trip_time),
        "throughput": len(completed) / horizon,
        "utilization": total_busy / (len(drivers) * horizon) if drivers else 0.0,
    }


def run_simulation(params: SimulationParams, seed: int) -> Dict[str, object]:
    rng = random.Random(seed)
    drivers = init_drivers(params, rng)

    requests: List[Request] = []
    request_map: Dict[int, Request] = {}
    queue: List[int] = []
    next_id = 1

    for t in range(params.simulation_time + 1):
        release_completed_drivers(t, drivers, request_map)

        arrivals = poisson_sample(params.arrival_rate_lambda, rng)
        for _ in range(arrivals):
            pickup_x, pickup_y = sample_location(params, rng)
            dest_x, dest_y = sample_location(params, rng)
            req = Request(
                request_id=next_id,
                request_time=t,
                pickup_x=pickup_x,
                pickup_y=pickup_y,
                dest_x=dest_x,
                dest_y=dest_y,
                car_type=weighted_choice(params.request_type_probs, rng),
            )
            requests.append(req)
            request_map[next_id] = req
            queue.append(next_id)
            next_id += 1

        queue = cancel_overdue_requests(t, queue, request_map, params.max_wait_time)
        queue = match_requests(t, queue, drivers, request_map)

    metrics = compute_metrics(params, drivers, requests)
    return {"drivers": drivers, "requests": requests, "metrics": metrics}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_requests_csv(file_path: Path, requests: List[Request]) -> None:
    headers = [
        "request_id",
        "request_time",
        "pickup_x",
        "pickup_y",
        "dest_x",
        "dest_y",
        "car_type",
        "status",
        "match_time",
        "pickup_time",
        "dropoff_time",
        "driver_id",
    ]
    with file_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for req in requests:
            writer.writerow(asdict(req))


def write_summary_csv(file_path: Path, rows: List[Dict[str, float]]) -> None:
    if not rows:
        return
    headers = list(rows[0].keys())
    with file_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def run_default_experiments(save_request_files: bool = True) -> None:
    scenarios = [
        ("low", 0.5),
        ("medium", 1.0),
        ("high", 2.0),
    ]
    seeds = [1, 2, 3]

    project_root = Path(__file__).resolve().parents[1]
    results_dir = project_root / "results"
    ensure_dir(results_dir)

    summary_rows: List[Dict[str, float]] = []

    for scenario_name, lambda_value in scenarios:
        for seed in seeds:
            params = SimulationParams(arrival_rate_lambda=lambda_value)
            output = run_simulation(params, seed)
            requests = output["requests"]
            metrics = output["metrics"]

            if save_request_files:
                requests_csv = results_dir / f"requests_{scenario_name}_seed{seed}.csv"
                write_requests_csv(requests_csv, requests)

            summary_row = {
                "scenario": scenario_name,
                "seed": float(seed),
                "lambda": lambda_value,
                **metrics,
            }
            summary_rows.append(summary_row)

    write_summary_csv(results_dir / "summary_metrics.csv", summary_rows)

    print("Simulation completed.")
    print(f"Summary file: {results_dir / 'summary_metrics.csv'}")


if __name__ == "__main__":
    run_default_experiments()
