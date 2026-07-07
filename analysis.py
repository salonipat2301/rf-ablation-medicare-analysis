import argparse
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = PROJECT_ROOT / "Filtered_RF_Providers.csv"
RF_CPT_CODES = ["64633", "64634", "64635", "64636", "64624", "64625", "64640", "77002"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Filter the CMS provider-service file to RF ablation CPT codes."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to the CMS provider-service CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path for the filtered RF provider output CSV.",
    )
    parser.add_argument("--chunksize", type=int, default=100000)
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = args.input.expanduser()
    output_path = args.output.expanduser()

    if not input_path.exists():
        raise FileNotFoundError(
            f"Missing provider-service source file: {input_path}. "
            "Download the CMS provider-service CSV or pass it with --input."
        )

    filtered_chunks = []
    for i, chunk in enumerate(pd.read_csv(input_path, dtype=str, chunksize=args.chunksize), start=1):
        if "HCPCS_Cd" not in chunk.columns:
            raise KeyError("Expected HCPCS_Cd column in the provider-service CSV.")
        rf_chunk = chunk[chunk["HCPCS_Cd"].isin(RF_CPT_CODES)]
        if not rf_chunk.empty:
            filtered_chunks.append(rf_chunk)
        print(f"Processed chunk {i}")

    if not filtered_chunks:
        print("No rows matched the RF ablation CPT codes.")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rf_data = pd.concat(filtered_chunks, ignore_index=True)
    rf_data.to_csv(output_path, index=False)
    print(f"Saved filtered data to {output_path}")


if __name__ == "__main__":
    main()
