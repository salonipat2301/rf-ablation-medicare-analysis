import argparse
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_INPUT = SCRIPT_DIR / "MUP_PHY_R25_P05_V20_D23_Geo.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "Filtered_RF_Geography_Service.csv"
RF_CPT_CODES = ["64633", "64634", "64635", "64636", "64624", "64625", "64640", "77002"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Filter the CMS geography-service file to RF ablation CPT codes."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--chunksize", type=int, default=100000)
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = args.input.expanduser()
    output_path = args.output.expanduser()

    if not input_path.exists():
        raise FileNotFoundError(f"Missing geography-service source file: {input_path}")

    filtered_chunks = []
    for i, chunk in enumerate(pd.read_csv(input_path, dtype=str, chunksize=args.chunksize), start=1):
        if "HCPCS_Cd" not in chunk.columns:
            raise KeyError("Expected HCPCS_Cd column in the geography-service CSV.")
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
