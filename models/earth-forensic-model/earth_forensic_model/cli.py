"""Command-line runner for the v0.1 paleoshoreline baseline."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path

from .shoreline import SeaLevelScenario, Site, calculate_exposure


OUTPUT_FIELDS = [
    "scenario_id",
    "site_id",
    "age_ka_bp",
    "mean_local_rsl_m",
    "mean_exposure_margin_m",
    "combined_standard_deviation_m",
    "probability_exposed",
    "margin_ci95_lower_m",
    "margin_ci95_upper_m",
    "classification",
]


def load_scenarios(path: Path) -> list[SeaLevelScenario]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("scenarios")
    if not isinstance(rows, list) or not rows:
        raise ValueError("scenario file must contain a non-empty 'scenarios' list")
    return [
        SeaLevelScenario(
            scenario_id=row["id"],
            age_ka_bp=float(row["age_ka_bp"]),
            global_mean_sea_level_m=float(row["global_mean_sea_level_m"]),
            standard_deviation_m=float(row["standard_deviation_m"]),
        )
        for row in rows
    ]


def load_sites(path: Path) -> list[Site]:
    sites: list[Site] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            sites.append(
                Site(
                    site_id=row["site_id"],
                    present_elevation_m=float(row["present_elevation_m"]),
                    elevation_standard_deviation_m=float(
                        row.get("elevation_standard_deviation_m") or 0
                    ),
                    local_rsl_anomaly_m=float(
                        row.get("local_rsl_anomaly_m") or 0
                    ),
                    local_rsl_standard_deviation_m=float(
                        row.get("local_rsl_standard_deviation_m") or 0
                    ),
                )
            )
    if not sites:
        raise ValueError("site file contains no data rows")
    return sites


def run(scenarios_path: Path, sites_path: Path, output_path: Path) -> int:
    scenarios = load_scenarios(scenarios_path)
    sites = load_sites(sites_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for scenario in scenarios:
            for site in sites:
                row = asdict(calculate_exposure(scenario, site))
                row["probability_exposed"] = f"{row['probability_exposed']:.6f}"
                for key in (
                    "mean_local_rsl_m",
                    "mean_exposure_margin_m",
                    "combined_standard_deviation_m",
                    "margin_ci95_lower_m",
                    "margin_ci95_upper_m",
                ):
                    row[key] = f"{row[key]:.3f}"
                writer.writerow(row)
    return len(scenarios) * len(sites)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Estimate first-order exposure probabilities from global sea level, "
            "site elevation, and an explicit local RSL anomaly."
        )
    )
    parser.add_argument("--scenarios", required=True, type=Path)
    parser.add_argument("--sites", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    count = run(args.scenarios, args.sites, args.output)
    print(f"Wrote {count} scenario-site results to {args.output}")


if __name__ == "__main__":
    main()
