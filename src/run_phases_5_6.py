from __future__ import annotations

from pathlib import Path
import csv

from simulation import SimulationParams, run_default_experiments, run_simulation


def read_summary_rows(summary_path: Path) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    with summary_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            parsed: dict[str, float | str] = {
                "scenario": row["scenario"],
                "seed": float(row["seed"]),
                "lambda": float(row["lambda"]),
                "total_requests": float(row["total_requests"]),
                "completed_requests": float(row["completed_requests"]),
                "canceled_requests": float(row["canceled_requests"]),
                "completion_rate": float(row["completion_rate"]),
                "cancellation_rate": float(row["cancellation_rate"]),
                "avg_matching_delay": float(row["avg_matching_delay"]),
                "avg_passenger_wait": float(row["avg_passenger_wait"]),
                "avg_trip_time": float(row["avg_trip_time"]),
                "throughput": float(row["throughput"]),
                "utilization": float(row["utilization"]),
            }
            rows.append(parsed)
    return rows


def mean(values: list[float]) -> float:
    return (sum(values) / len(values)) if values else 0.0


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def aggregate_scenario_averages(rows: list[dict[str, float | str]]) -> list[dict[str, object]]:
    scenarios = ["low", "medium", "high"]
    out: list[dict[str, object]] = []

    for scenario in scenarios:
        group = [r for r in rows if r["scenario"] == scenario]
        out.append(
            {
                "scenario": scenario,
                "runs": len(group),
                "lambda": mean([float(r["lambda"]) for r in group]),
                "avg_total_requests": mean([float(r["total_requests"]) for r in group]),
                "avg_completed_requests": mean([float(r["completed_requests"]) for r in group]),
                "avg_canceled_requests": mean([float(r["canceled_requests"]) for r in group]),
                "avg_completion_rate": mean([float(r["completion_rate"]) for r in group]),
                "avg_cancellation_rate": mean([float(r["cancellation_rate"]) for r in group]),
                "avg_matching_delay": mean([float(r["avg_matching_delay"]) for r in group]),
                "avg_passenger_wait": mean([float(r["avg_passenger_wait"]) for r in group]),
                "avg_trip_time": mean([float(r["avg_trip_time"]) for r in group]),
                "avg_throughput": mean([float(r["throughput"]) for r in group]),
                "avg_utilization": mean([float(r["utilization"]) for r in group]),
            }
        )

    return out


def run_phase_5_validation(results_dir: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    def make_row(
        case: str,
        expected: str,
        observed_total_requests: object = "",
        observed_completed_requests: object = "",
        observed_canceled_requests: object = "",
        ref_avg_matching_delay: object = "",
        ref_cancellation_rate: object = "",
        observed_avg_matching_delay: object = "",
        observed_cancellation_rate: object = "",
        passed: bool = False,
    ) -> dict[str, object]:
        return {
            "case": case,
            "expected": expected,
            "observed_total_requests": observed_total_requests,
            "observed_completed_requests": observed_completed_requests,
            "observed_canceled_requests": observed_canceled_requests,
            "ref_avg_matching_delay": ref_avg_matching_delay,
            "ref_cancellation_rate": ref_cancellation_rate,
            "observed_avg_matching_delay": observed_avg_matching_delay,
            "observed_cancellation_rate": observed_cancellation_rate,
            "passed": passed,
        }

    zero_demand = run_simulation(SimulationParams(arrival_rate_lambda=0.0), seed=1)["metrics"]
    zero_demand_pass = (
        zero_demand["total_requests"] == 0.0
        and zero_demand["completed_requests"] == 0.0
        and zero_demand["canceled_requests"] == 0.0
    )
    rows.append(
        make_row(
            case="lambda_zero",
            expected="No requests generated",
            observed_total_requests=zero_demand["total_requests"],
            observed_completed_requests=zero_demand["completed_requests"],
            observed_canceled_requests=zero_demand["canceled_requests"],
            passed=zero_demand_pass,
        )
    )

    high_driver = run_simulation(SimulationParams(num_drivers=120, arrival_rate_lambda=1.0), seed=1)["metrics"]
    high_driver_pass = high_driver["cancellation_rate"] == 0.0 and high_driver["avg_matching_delay"] <= 0.1
    rows.append(
        make_row(
            case="high_driver_supply",
            expected="Near zero matching delay and zero cancellation",
            observed_total_requests=high_driver["total_requests"],
            observed_avg_matching_delay=high_driver["avg_matching_delay"],
            observed_cancellation_rate=high_driver["cancellation_rate"],
            passed=high_driver_pass,
        )
    )

    medium_ref = run_simulation(SimulationParams(num_drivers=40, arrival_rate_lambda=1.0), seed=1)["metrics"]
    overloaded = run_simulation(SimulationParams(num_drivers=20, arrival_rate_lambda=3.0), seed=1)["metrics"]
    overloaded_pass = (
        overloaded["avg_matching_delay"] > medium_ref["avg_matching_delay"]
        or overloaded["cancellation_rate"] >= medium_ref["cancellation_rate"]
    )
    rows.append(
        make_row(
            case="overloaded_system",
            expected="Worse delay or cancellation compared to medium reference",
            ref_avg_matching_delay=medium_ref["avg_matching_delay"],
            ref_cancellation_rate=medium_ref["cancellation_rate"],
            observed_avg_matching_delay=overloaded["avg_matching_delay"],
            observed_cancellation_rate=overloaded["cancellation_rate"],
            passed=overloaded_pass,
        )
    )

    write_csv(results_dir / "phase5_validation_results.csv", rows)
    return rows


def execute_phases_5_6(save_request_files: bool = True) -> dict[str, Path]:
    project_root = Path(__file__).resolve().parents[1]
    results_dir = project_root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Phase 6: execute experiment campaign for low, medium, high demand.
    run_default_experiments(save_request_files=save_request_files)

    summary_path = results_dir / "summary_metrics.csv"
    summary_rows = read_summary_rows(summary_path)
    scenario_averages = aggregate_scenario_averages(summary_rows)
    scenario_path = results_dir / "phase6_scenario_averages.csv"
    write_csv(scenario_path, scenario_averages)

    # Phase 5: run sanity and stress validation cases.
    validation_path = results_dir / "phase5_validation_results.csv"
    run_phase_5_validation(results_dir)

    return {
        "summary_path": summary_path,
        "scenario_path": scenario_path,
        "validation_path": validation_path,
    }


def main() -> None:
    output = execute_phases_5_6(save_request_files=True)

    print("Phase 5 and Phase 6 execution completed.")
    print(f"Experiment summary: {output['summary_path']}")
    print(f"Scenario averages: {output['scenario_path']}")
    print(f"Validation results: {output['validation_path']}")


if __name__ == "__main__":
    main()
