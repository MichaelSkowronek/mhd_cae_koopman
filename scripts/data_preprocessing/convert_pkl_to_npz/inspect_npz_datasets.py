#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inspects individual processed .npz datasets.

This script loads a specified .npz file, which is expected to contain
'timeseries' and 'labels' keys, and prints a summary of its contents
using the print_timeseries_info utility.
"""

import argparse
import sys
from pathlib import Path

# Attempt to import necessary modules from the mhd_cae_koopman package.
try:
    from mhd_cae_koopman.data_processing.utils import print_timeseries_info
    from mhd_cae_koopman.utils.numpy_io import load_numpy_object
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(
        "\nPlease ensure that the 'mhd_cae_koopman' package is installed and "
        "accessible."
    )
    print("You might need to install it (e.g., 'pip install -e .') or adjust your PYTHONPATH.")
    sys.exit(1)


def inspect_dataset(npz_file_path: Path, verbose: bool = True):
    """
    Loads an .npz dataset and prints its summary information.

    Args:
        npz_file_path (Path): The path to the .npz file.
        verbose (bool, optional): If True, prints detailed information. Defaults to True.
    """
    if not npz_file_path.is_file():
        print(f"Error: NPZ file not found at {npz_file_path.resolve()}")
        return

    if verbose:
        print(f"\n--- Inspecting: {npz_file_path.name} from {npz_file_path.resolve()} ---")

    try:
        loaded_data = load_numpy_object(npz_file_path)

        if 'timeseries' not in loaded_data or 'labels' not in loaded_data:
            print(f"Error: NPZ file {npz_file_path.name} does not contain 'timeseries' or 'labels' keys.")
            return

        if verbose:
            print_timeseries_info(
                loaded_data['timeseries'],
                loaded_data['labels']
            )
        print(f"Successfully loaded and inspected: {npz_file_path.name}")

    except Exception as e:
        print(f"An error occurred while inspecting {npz_file_path.name}: {e}")


def main():
    """Main function to parse arguments and run the dataset inspection."""
    parser = argparse.ArgumentParser(
        description="Inspect individual NPZ datasets by printing their summary.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--ha",
        type=int,
        required=True,
        help="Hartmann number (Ha) to specify the data subdirectory.",
    )
    parser.add_argument(
        "--data_dir",
        type=Path,
        required=True,
        help="Path to the main data directory.",
    )
    parser.add_argument(
        "--file_name",
        type=str,
        required=True,
        help="Name of the .npz file to inspect (e.g., du.npz).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="If set, suppress detailed print output.",
    )
    args = parser.parse_args()

    base_data_path = args.data_dir / f"re1000_ha{args.ha}/3d/pkl/"
    npz_file_path = base_data_path / args.file_name

    inspect_dataset(npz_file_path, verbose=not args.quiet)


if __name__ == "__main__":
    main()