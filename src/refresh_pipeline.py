import subprocess
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


PIPELINE_STEPS = [
    ("Transform mortgage delinquency data", "src/transform_data.py"),
    ("Transform borrower risk-profile data", "src/transform_risk_profiles.py"),
    ("Build monthly mortgage dataset", "src/build_monthly_dataset.py"),
    ("Build master dataset", "src/build_master_dataset.py"),
    ("Build KPI dataset", "src/build_kpi_dataset.py"),
    ("Rebuild DuckDB analytical database", "src/build_duckdb.py"),
]


def run_step(description, script):

    print("\n" + "=" * 70)
    print(description)
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, script],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout)

    if result.returncode != 0:

        if result.stderr:
            print(result.stderr)

        raise RuntimeError(
            f"Pipeline failed at: {description}"
        )


def main():

    start_time = datetime.now()

    print("=" * 70)
    print("MORTGAGE RISK AI - AUTOMATED DATA REFRESH")
    print("=" * 70)
    print(f"Started: {start_time:%Y-%m-%d %H:%M:%S}")

    try:

        for description, script in PIPELINE_STEPS:
            run_step(description, script)

        end_time = datetime.now()

        print("\n" + "=" * 70)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"Started : {start_time:%Y-%m-%d %H:%M:%S}")
        print(f"Finished: {end_time:%Y-%m-%d %H:%M:%S}")
        print(f"Duration: {end_time - start_time}")

    except Exception as e:

        print("\n" + "=" * 70)
        print("PIPELINE FAILED")
        print("=" * 70)
        print(str(e))

        sys.exit(1)


if __name__ == "__main__":
    main()