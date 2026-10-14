
import subprocess
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
RESULTS_DIR = PROJECT_ROOT / "results"

EXPERIMENTS = [
    ("Official native-noise baseline", "official_baseline.py",
     "official_baseline_output.txt"),
    ("Parity-protected experiment", "protected_benchmark.py",
     "protected_benchmark_output.txt"),
    ("Common-noise comparison", "common_noise_baseline.py",
     "common_noise_output.txt"),
]


def main():
    RESULTS_DIR.mkdir(exist_ok=True)

    for title, script_name, output_name in EXPERIMENTS:
        script_path = SRC_DIR / script_name
        output_path = RESULTS_DIR / output_name

        print(f"\n{'=' * 60}")
        print(title)
        print(f"{'=' * 60}")

        with output_path.open("w", encoding="utf-8") as output_file:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=PROJECT_ROOT,
                stdout=output_file,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )

        if result.returncode != 0:
            print(f"FAILED: {script_name}")
            print(f"Check the log: {output_path}")
            sys.exit(result.returncode)

        print(f"Completed. Results saved to: {output_path}")

    print("\nAll three experiments completed successfully.")
    print(f"Review the results in: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
