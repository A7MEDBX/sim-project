from __future__ import annotations

from pathlib import Path
import csv

from run_phases_5_6 import execute_phases_5_6
from run_phases_7_8_9 import execute_phases_7_8_9


def remove_old_request_files(results_dir: Path) -> int:
    deleted = 0
    for path in results_dir.glob("requests_*_seed*.csv"):
        path.unlink(missing_ok=True)
        deleted += 1
    return deleted


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_master_report(project_root: Path) -> Path:
    docs_dir = project_root / "docs"
    results_dir = project_root / "results"

    phase6_rows = read_csv(results_dir / "phase6_scenario_averages.csv")
    qa_rows = read_csv(results_dir / "phase9_qa_results.csv")

    order = {"low": 0, "medium": 1, "high": 2}
    phase6_rows.sort(key=lambda r: order.get(r["scenario"], 99))
    qa_passed = sum(1 for row in qa_rows if row["passed"] == "True")

    lines = [
        "# Master Project Execution Report",
        "",
        "## Project Status",
        "This repository now runs as one connected pipeline from implementation to QA.",
        "",
        "## Connected Flow",
        "1. Core simulation executes demand scenarios.",
        "2. Validation checks run on edge and stress cases.",
        "3. Analysis and plots are generated from scenario outputs.",
        "4. Packaging docs are generated.",
        "5. QA verifies all required artifacts and trends.",
        "",
        "## Final Scenario Metrics",
        "| Scenario | Avg Wait | Avg Throughput | Avg Utilization |",
        "| --- | ---: | ---: | ---: |",
    ]

    for row in phase6_rows:
        lines.append(
            f"| {row['scenario']} | {float(row['avg_passenger_wait']):.4f} | "
            f"{float(row['avg_throughput']):.4f} | {float(row['avg_utilization']):.4f} |"
        )

    lines.extend(
        [
            "",
            "## QA Summary",
            f"- QA checks passed: {qa_passed}/{len(qa_rows)}",
            "",
            "## Key Artifacts",
            "- docs/FINAL_PROJECT_REPORT.md",
            "- docs/PRESENTATION_OUTLINE.md",
            "- docs/PHASES_1_2_3_REPORT.md",
            "- docs/PHASES_4_5_6_REPORT.md",
            "- docs/PHASES_7_8_9_REPORT.md",
            "- results/summary_metrics.csv",
            "- results/phase5_validation_results.csv",
            "- results/phase6_scenario_averages.csv",
            "- results/phase7_waiting_vs_demand.png",
            "- results/phase7_throughput_vs_demand.png",
            "- results/phase7_utilization_vs_demand.png",
            "- results/phase9_qa_results.csv",
        ]
    )

    report_path = docs_dir / "MASTER_PROJECT_EXECUTION_REPORT.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    results_dir = project_root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    deleted_files = remove_old_request_files(results_dir)

    # Run phases 5 and 6 with compact outputs (no per-request csv clutter).
    execute_phases_5_6(save_request_files=False)

    # Run phases 7, 8, and 9 using outputs from phases 5 and 6.
    execute_phases_7_8_9()

    master_report = write_master_report(project_root)

    print("Full project pipeline completed.")
    print(f"Removed old request files: {deleted_files}")
    print(f"Master report: {master_report}")


if __name__ == "__main__":
    main()
