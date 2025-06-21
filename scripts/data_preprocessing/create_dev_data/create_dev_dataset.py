#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Creates a smaller development dataset from a full dataset.

This script loads a large, uncompressed .npz file, slices the 'timeseries'
array to keep a specified number of initial snapshots, and saves the result
as a new, smaller .npz file for rapid testing and development.
"""

import argparse
import sys
from pathlib import Path

# Attempt to import necessary modules from the mhd_cae_koopman package.
try:
    from mhd_cae_koopman.utils.numpy_io import (
        load_numpy_object,
        save_numpy_object,
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(
        "\nPlease ensure that the 'mhd_cae_koopman' package is installed and "
        "accessible."
    )
    print("You might need to install it (e.g., 'pip install -e .') or adjust your PYTHONPATH.")
    sys.exit(1)


def create_development_set(
        input_path: Path,
        output_path: Path,
        num_snapshots: int,
    ):
    """
    Loads a dataset, slices it, and saves a smaller version.

    Args:
        input_path (Path): Path to the source .npz file.
        output_path (Path): Path to save the new development .npz file.
        num_snapshots (int): The number of snapshots to keep from the beginning.
    """
    print(f"Loading full dataset from: {input_path}")
    full_data = load_numpy_object(input_path)

    original_shape = full_data['timeseries'].shape
    print(f"Original timeseries shape: {original_shape}")

    if num_snapshots > original_shape[0]:
        print(f"Warning: Requested {num_snapshots} snapshots, but only {original_shape[0]} are available. Using all available snapshots.")
        num_snapshots = original_shape[0]

    # Create the smaller dataset by slicing the timeseries array
    dev_timeseries = full_data['timeseries'][:num_snapshots]
    dev_data = {
        'timeseries': dev_timeseries,
        'labels': full_data['labels']
    }

    print(f"New timeseries shape: {dev_timeseries.shape}")
    print(f"Saving development dataset to: {output_path}")
    
    # Ensure the output directory exists before saving
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    
    # Save uncompressed for fast I/O during development
    save_numpy_object(
        dev_data,
        output_path,
        compressed=False,
    )
    print("Development dataset created successfully.")


def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(
        description="Create a smaller development dataset from a full .npz file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input_file",
        type=Path,
        required=True,
        help="Path to the source uncompressed .npz file.",
    )
    parser.add_argument(
        "--output_file",
        type=Path,
        required=True,
        help="Path to save the new development .npz file.",
    )
    parser.add_argument(
        "--snapshots",
        type=int,
        default=2,
        help="Number of snapshots to include in the development set.",
    )
    args = parser.parse_args()

    try:
        create_development_set(
            input_path=args.input_file,
            output_path=args.output_file,
            num_snapshots=args.snapshots,
        )
    except (FileNotFoundError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()