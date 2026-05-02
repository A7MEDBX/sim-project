from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from src.simulation import (
    SimulationParams,
    run_simulation,
    write_requests_csv,
    write_summary_csv,
)


st.set_page_config(page_title="Ride-Sharing Simulation Dashboard", layout="wide")

PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
SUMMARY_PATH = RESULTS_DIR / "summary_metrics.csv"

PLOT_COLORS = {
    "wait": "#2E86AB",
    "throughput": "#2F9E44",
    "utilization": "#6F42C1",
    "cancellation": "#C92A2A",
    "trip": "#E67700",
}


@st.cache_data(show_spinner=False)
def _to_requests_df(requests: list) -> pd.DataFrame:
    return pd.DataFrame([asdict(r) for r in requests])


def _build_scenario_table(rows: List[Dict[str, float]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    return df


def _prepare_summary_views(summary_rows: List[Dict[str, float]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    # summary_rows already contains per-seed metrics. Keep them to avoid mean-of-means.
    summary_df = pd.DataFrame(summary_rows)
    scenario_avg = summary_df.groupby("scenario", as_index=False).mean(numeric_only=True)
    return summary_df, scenario_avg


def _load_summary_csv() -> List[Dict[str, float]]:
    df = pd.read_csv(SUMMARY_PATH)
    return df.to_dict(orient="records")


def _load_request_csvs() -> Dict[Tuple[str, int], pd.DataFrame]:
    cache: Dict[Tuple[str, int], pd.DataFrame] = {}
    for path in RESULTS_DIR.glob("requests_*_seed*.csv"):
        stem = path.stem
        parts = stem.split("_")
        if len(parts) < 3 or parts[0] != "requests":
            continue
        scenario = parts[1]
        seed_part = parts[2].replace("seed", "")
        seed_digits = "".join(ch for ch in seed_part if ch.isdigit())
        if not seed_digits:
            continue
        seed = int(seed_digits)
        cache[(scenario, seed)] = pd.read_csv(path)
    return cache


def _build_requests_df(requests_cache: Dict[Tuple[str, int], pd.DataFrame]) -> pd.DataFrame:
    if not requests_cache:
        return pd.DataFrame()

    frames: list[pd.DataFrame] = []
    for (scenario, seed), df in requests_cache.items():
        if df.empty:
            continue
        data = df.copy()
        data["scenario"] = scenario
        data["seed"] = seed
        if "pickup_time" in data.columns and "request_time" in data.columns:
            data["waiting_time"] = data["pickup_time"] - data["request_time"]
        if "dropoff_time" in data.columns and "pickup_time" in data.columns:
            data["trip_time"] = data["dropoff_time"] - data["pickup_time"]
        frames.append(data)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _plot_dashboard(summary: pd.DataFrame) -> None:
    scenario_order = ["low", "medium", "high"]
    summary = summary.copy()
    summary["scenario"] = pd.Categorical(
        summary["scenario"], categories=scenario_order, ordered=True
    )
    summary = summary.sort_values("scenario")

    x = range(len(summary))
    labels = summary["scenario"].astype(str).tolist()

    fig = plt.figure(figsize=(14, 8), facecolor="white")
    grid = fig.add_gridspec(nrows=2, ncols=2, hspace=0.35, wspace=0.3)

    ax_wait = fig.add_subplot(grid[0, 0])
    ax_throughput = fig.add_subplot(grid[0, 1])
    ax_util = fig.add_subplot(grid[1, 0])
    ax_cancel = fig.add_subplot(grid[1, 1])

    ax_wait.plot(
        x,
        summary["avg_passenger_wait"],
        marker="o",
        linewidth=2,
        color=PLOT_COLORS["wait"],
    )
    ax_wait.set_title("Waiting Time vs Demand")
    ax_wait.set_xlabel("Scenario")
    ax_wait.set_ylabel("Avg Passenger Wait")
    ax_wait.set_xticks(x)
    ax_wait.set_xticklabels(labels)
    ax_wait.grid(True, alpha=0.3)

    ax_throughput.plot(
        x,
        summary["throughput"],
        marker="o",
        linewidth=2,
        color=PLOT_COLORS["throughput"],
    )
    ax_throughput.set_title("Throughput vs Demand")
    ax_throughput.set_xlabel("Scenario")
    ax_throughput.set_ylabel("Throughput")
    ax_throughput.set_xticks(x)
    ax_throughput.set_xticklabels(labels)
    ax_throughput.grid(True, alpha=0.3)

    ax_util.plot(
        x,
        summary["utilization"],
        marker="o",
        linewidth=2,
        color=PLOT_COLORS["utilization"],
    )
    ax_util.set_title("Utilization vs Demand")
    ax_util.set_xlabel("Scenario")
    ax_util.set_ylabel("Utilization")
    ax_util.set_xticks(x)
    ax_util.set_xticklabels(labels)
    ax_util.grid(True, alpha=0.3)

    if "cancellation_rate" in summary.columns:
        ax_cancel.plot(
            x,
            summary["cancellation_rate"],
            marker="o",
            linewidth=2,
            color=PLOT_COLORS["cancellation"],
        )
        ax_cancel.set_title("Cancellation Rate vs Demand")
        ax_cancel.set_xlabel("Scenario")
        ax_cancel.set_ylabel("Cancellation Rate")
        ax_cancel.set_xticks(x)
        ax_cancel.set_xticklabels(labels)
        ax_cancel.grid(True, alpha=0.3)
    else:
        ax_cancel.axis("off")
        ax_cancel.text(0.5, 0.5, "Cancellation Rate not available", ha="center", va="center")

    st.pyplot(fig)


st.title("Ride-Sharing Simulation Dashboard")

with st.sidebar:
    st.header("Simulation Controls")
    mode = st.radio("Mode", ["Scenario sweep", "Single run"], horizontal=False)

    simulation_time = st.number_input("Simulation time", min_value=10, max_value=2000, value=100, step=10)
    num_drivers = st.number_input("Number of drivers", min_value=1, max_value=5000, value=20, step=1)
    arrival_rate = st.number_input("Arrival rate (lambda)", min_value=0.0, max_value=1000.0, value=1.0, step=0.1)
    city_size = st.number_input("City size", min_value=5, max_value=200, value=20, step=5)
    max_wait_time = st.number_input("Max wait time", min_value=1, max_value=200, value=20, step=1)
    driver_speed = st.number_input("Driver speed", min_value=0.1, max_value=10.0, value=1.5, step=0.1)

    with st.expander("Hotspot settings"):
        request_hotspot_ratio = st.slider(
            "Request hotspot ratio",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.05,
        )
        driver_hotspot_ratio = st.slider(
            "Driver hotspot ratio",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.05,
        )
        hotspot_x = st.number_input("Hotspot center X", min_value=0.0, max_value=float(city_size), value=5.0, step=0.5)
        hotspot_y = st.number_input("Hotspot center Y", min_value=0.0, max_value=float(city_size), value=5.0, step=0.5)

    save_requests = st.checkbox("Save request CSVs", value=True)
    run_button = st.button("Run simulation", type="primary")
    reload_button = st.button("Reload summary_metrics.csv")

if run_button:
    st.session_state.clear()
    summary_rows: List[Dict[str, float]] = []
    requests_cache: Dict[Tuple[str, int], pd.DataFrame] = {}

    if mode == "Scenario sweep":
        scenarios = [
            ("low", 0.5),
            ("medium", 1.0),
            ("high", 2.0),
        ]
        seeds = [1, 2, 3]
    else:
        scenarios = [("custom", arrival_rate)]
        seeds = [1]

    for scenario_name, lambda_value in scenarios:
        for seed in seeds:
            params = SimulationParams(
                simulation_time=int(simulation_time),
                num_drivers=int(num_drivers),
                arrival_rate_lambda=float(lambda_value),
                city_size=int(city_size),
                max_wait_time=int(max_wait_time),
                driver_speed=float(driver_speed),
                hotspot_ratio=float(request_hotspot_ratio),
                driver_hotspot_ratio=float(driver_hotspot_ratio),
                hotspot_center=(float(hotspot_x), float(hotspot_y)),
            )
            output = run_simulation(params, seed)
            requests = output["requests"]
            metrics = output["metrics"]

            if save_requests:
                req_path = RESULTS_DIR / f"requests_{scenario_name}_seed{seed}.csv"
                write_requests_csv(req_path, requests)

            summary_row = {
                "scenario": scenario_name,
                "seed": float(seed),
                "lambda": float(lambda_value),
                **metrics,
            }
            summary_rows.append(summary_row)
            requests_cache[(scenario_name, seed)] = _to_requests_df(requests)

    write_summary_csv(RESULTS_DIR / "summary_metrics.csv", summary_rows)

    st.session_state["summary_rows"] = summary_rows
    st.session_state["requests_cache"] = requests_cache

if reload_button:
    if SUMMARY_PATH.exists():
        st.session_state["summary_rows"] = _load_summary_csv()
        st.session_state["requests_cache"] = {}
    else:
        st.warning("summary_metrics.csv not found in results folder.")

if "summary_rows" not in st.session_state and SUMMARY_PATH.exists():
    st.session_state["summary_rows"] = _load_summary_csv()
    st.session_state["requests_cache"] = {}


if "summary_rows" in st.session_state:
    summary_rows = st.session_state["summary_rows"]
    summary_df, scenario_avg = _prepare_summary_views(summary_rows)

    st.subheader("Key Performance Indicators")
    # KPI calculations use per-seed records directly to avoid mean-of-means bias.
    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Average Waiting Time", f"{summary_df['avg_passenger_wait'].mean():.2f}")
    kpi_cols[1].metric("Average Throughput", f"{summary_df['throughput'].mean():.2f}")
    kpi_cols[2].metric("Average Utilization", f"{summary_df['utilization'].mean():.2%}")

    if (scenario_avg["utilization"] > 0.9).any():
        st.warning("System near saturation: utilization exceeds 0.90 in at least one scenario.")
    if len(scenario_avg) >= 2:
        scenario_sorted = scenario_avg.sort_values("scenario")
        if scenario_sorted["avg_passenger_wait"].iloc[-1] > 1.5 * scenario_sorted["avg_passenger_wait"].iloc[0]:
            st.warning("Waiting time increases sharply across scenarios, indicating overload behavior.")

    tab_dashboard, tab_summary, tab_requests, tab_distributions, tab_variability, tab_analysis = st.tabs(
        ["Dashboard", "Summary Table", "Requests", "Distributions", "Variability", "Analysis"]
    )

    with tab_dashboard:
        st.subheader("System Performance Dashboard")
        _plot_dashboard(scenario_avg)

    with tab_summary:
        st.subheader("Scenario Summary")
        summary_view = scenario_avg[["scenario", "avg_passenger_wait", "throughput", "utilization"]].copy()
        summary_view.columns = ["Scenario", "Avg Wait", "Throughput", "Utilization"]
        st.dataframe(summary_view, use_container_width=True)

        best_wait_idx = scenario_avg["avg_passenger_wait"].idxmin()
        worst_util_idx = scenario_avg["utilization"].idxmax()
        best_scenario = scenario_avg.loc[best_wait_idx, "scenario"]
        worst_scenario = scenario_avg.loc[worst_util_idx, "scenario"]
        st.info(
            f"Best scenario (lowest waiting): {best_scenario}. "
            f"Highest load (utilization peak): {worst_scenario}."
        )

    with tab_requests:
        st.subheader("Request Records")
        requests_cache = st.session_state["requests_cache"]
        if not requests_cache:
            st.info("Request CSVs not loaded. Click to load from results folder.")
            if st.button("Load request CSVs"):
                st.session_state["requests_cache"] = _load_request_csvs()
                st.rerun()
        else:
            scenario_options = sorted({k[0] for k in requests_cache.keys()})
            scenario_pick = st.selectbox("Scenario", scenario_options)
            seed_options = sorted({k[1] for k in requests_cache.keys() if k[0] == scenario_pick})
            seed_pick = st.selectbox("Seed", seed_options)
            st.dataframe(requests_cache[(scenario_pick, seed_pick)], use_container_width=True)

    with tab_distributions:
        st.subheader("Distribution Analysis")
        requests_cache = st.session_state.get("requests_cache", {})
        if not requests_cache:
            st.info("Load request CSVs to enable distribution and time-series analysis.")
        else:
            request_df = _build_requests_df(requests_cache)
            if request_df.empty:
                st.info("No request-level data available to plot distributions.")
            else:
                fig, axes = plt.subplots(1, 2, figsize=(12, 4), facecolor="white")
                if "waiting_time" in request_df.columns:
                    axes[0].hist(request_df["waiting_time"].dropna(), bins=30, color=PLOT_COLORS["wait"], alpha=0.75)
                    axes[0].set_title("Waiting Time Distribution")
                    axes[0].set_xlabel("Waiting Time")
                    axes[0].set_ylabel("Count")
                    axes[0].grid(True, alpha=0.25)
                else:
                    axes[0].axis("off")
                    axes[0].text(0.5, 0.5, "Waiting time not available", ha="center", va="center")

                if "trip_time" in request_df.columns:
                    axes[1].hist(request_df["trip_time"].dropna(), bins=30, color=PLOT_COLORS["trip"], alpha=0.75)
                    axes[1].set_title("Trip Time Distribution")
                    axes[1].set_xlabel("Trip Time")
                    axes[1].set_ylabel("Count")
                    axes[1].grid(True, alpha=0.25)
                else:
                    axes[1].axis("off")
                    axes[1].text(0.5, 0.5, "Trip time not available", ha="center", va="center")

                st.pyplot(fig)

                if "request_time" in request_df.columns and "waiting_time" in request_df.columns:
                    st.subheader("Waiting Time Over Simulation Time")
                    scenario_pick = st.selectbox("Scenario", sorted(request_df["scenario"].unique()), key="time_series_scenario")
                    seed_pick = st.selectbox(
                        "Seed",
                        sorted(request_df.loc[request_df["scenario"] == scenario_pick, "seed"].unique()),
                        key="time_series_seed",
                    )
                    subset = request_df[(request_df["scenario"] == scenario_pick) & (request_df["seed"] == seed_pick)]
                    fig_ts, ax_ts = plt.subplots(figsize=(10, 4), facecolor="white")
                    ax_ts.scatter(subset["request_time"], subset["waiting_time"], s=12, alpha=0.4, color=PLOT_COLORS["wait"])
                    ax_ts.set_title("Waiting Time Over Time")
                    ax_ts.set_xlabel("Request Time")
                    ax_ts.set_ylabel("Waiting Time")
                    ax_ts.grid(True, alpha=0.3)
                    st.pyplot(fig_ts)

    with tab_variability:
        st.subheader("Seed Variability Analysis")
        fig, axes = plt.subplots(1, 2, figsize=(12, 4), facecolor="white")
        summary_df.boxplot(column="avg_passenger_wait", by="scenario", ax=axes[0], grid=False)
        axes[0].set_title("Waiting Time by Scenario (Seeds)")
        axes[0].set_xlabel("Scenario")
        axes[0].set_ylabel("Avg Passenger Wait")

        summary_df.boxplot(column="utilization", by="scenario", ax=axes[1], grid=False)
        axes[1].set_title("Utilization by Scenario (Seeds)")
        axes[1].set_xlabel("Scenario")
        axes[1].set_ylabel("Utilization")

        plt.suptitle("")
        st.pyplot(fig)

    with tab_analysis:
        st.subheader("Analysis")
        scenario_sorted = scenario_avg.sort_values("scenario")
        wait_low = scenario_sorted["avg_passenger_wait"].iloc[0]
        wait_high = scenario_sorted["avg_passenger_wait"].iloc[-1]
        util_high = scenario_sorted["utilization"].iloc[-1]
        throughput_low = scenario_sorted["throughput"].iloc[0]
        throughput_high = scenario_sorted["throughput"].iloc[-1]
        throughput_growth = (throughput_high - throughput_low) / max(throughput_low, 1e-6)
        st.write(
            "Waiting time increases with demand because higher arrival rates outpace driver availability, "
            "so requests accumulate in the queue. This is consistent with utilization rising toward full capacity. "
            "Throughput grows with demand early on, but growth slows as the fleet saturates, indicating that drivers "
            "rather than travel distance are the primary bottleneck."
        )

        st.markdown(
            "**Scenario comparison**\n"
            f"- Low demand wait: {wait_low:.2f}\n"
            f"- High demand wait: {wait_high:.2f}\n"
            f"- High demand utilization: {util_high:.2%}\n"
            f"- Throughput growth (low to high): {throughput_growth:.1%}"
        )

    st.success("Dashboard ready. CSV files saved in the results folder.")
else:
    st.info("Run a simulation or load summary_metrics.csv to generate the dashboard.")
