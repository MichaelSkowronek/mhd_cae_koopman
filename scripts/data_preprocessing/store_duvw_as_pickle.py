#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Processes binary duvw data files and stores them as pickle files.

This script reads a binary duvw data file (e.g., du.dat),
processes it using the parser in the mhd_cae_koopman package, and
saves the result in a serialized format (pickle) for faster access
in subsequent analysis.
"""

import argparse
import sys
from pathlib import Path

import numpy as np

# Attempt to import necessary modules from your local package.
try:
    from mhd_cae_koopman.data_processing.duvw import parse_duvw_binary
    from mhd_cae_koopman.data_processing.utils import print_timeseries_info
    from mhd_cae_koopman.utils import load_object
    from mhd_cae_koopman.utils import save_object
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(
        "\nPlease ensure that the 'mhd_cae_koopman' package is installed and "
        "accessible."
    )
    print(
        "You might need to install it in editable mode "
        "(e.g., 'pip install -e .')"
    )
    print("or adjust your PYTHONPATH environment variable.")
    sys.exit(1)


def process_duvw_data(
    duvw_file: Path,
    output_path: Path,
    verify: bool = False,
    verbose: bool = True,
):
    """
    Loads data from a duvw binary file, saves it as a pickle, and optionally verifies.

    Args:
        duvw_file (Path): The path to the input .dat file (e.g., du.dat).
        output_path (Path): The path where the output .pkl file will be saved.
        verify (bool, optional): If True, loads the pickle file after saving to
                                 verify its contents. Defaults to False.
        verbose (bool, optional): If True, prints detailed information.
    """
    if not duvw_file.is_file():
        print(f"Error: Data file not found at {duvw_file}")
        sys.exit(1)

    # Load the data using the custom parser
    timeseries, labels = parse_duvw_binary(duvw_file)

    # Make labels more specific based on the filename
    filename_stem = duvw_file.stem  # e.g., "du"
    if 'du' in filename_stem:
        specific_labels = ['x', 'y', 'z', 'du_dx', 'du_dy', 'du_dz']
    elif 'dv' in filename_stem:
        specific_labels = ['x', 'y', 'z', 'dv_dx', 'dv_dy', 'dv_dz']
    elif 'dw' in filename_stem:
        specific_labels = ['x', 'y', 'z', 'dw_dx', 'dw_dy', 'dw_dz']
    else:
        specific_labels = labels  # Fallback to generic labels

    data = {'timeseries': timeseries, 'labels': specific_labels}

    if verbose:
        print("\n--- Loaded Data Summary ---")
        print_timeseries_info(data['timeseries'], data['labels'])

    # Save the processed data using your project's save_object utility
    print(f"\nSaving processed data to: {output_path}")
    save_object(data, output_path)

    if verify:
        print("\n--- Verification Step ---")
        print(f"Loading data from pickle file for verification: {output_path}")
        loaded_data = load_object(output_path)
        print_timeseries_info(loaded_data['timeseries'], loaded_data['labels'])
        # A simple check to ensure data consistency
        assert np.array_equal(
            data['timeseries'], loaded_data['timeseries']
        ), "Verification failed: Timeseries data does not match."
        assert data['labels'] == loaded_data['labels'], \
            "Verification failed: Labels do not match."
        print("Verification successful.")


def main():
    """Main function to parse arguments and run the data processing."""
    parser = argparse.ArgumentParser(
        description="Convert binary duvw data files to pickle format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--ha",
        type=int,
        default=300,
        help="Hartmann number (Ha) to specify the data subdirectory.",
    )
    parser.add_argument(
        "--file_name",
        type=str,
        default="du.dat",
        help="Name of the binary data file (e.g., du.dat).",
    )
    parser.add_argument(
        "--data_dir",
        type=Path,
        default=Path("../../../../../../data"),
        help="Path to the main data directory.",
    )
    parser.add_argument(
        "--verify",
        action='store_true',
        help="If set, verify the pickle file after creation by loading it.",
    )
    parser.add_argument(
        "--quiet",
        action='store_true',
        help="If set, suppress detailed print output.",
    )
    args = parser.parse_args()

    # Construct full paths based on arguments
    base_data_path = args.data_dir / f"re1000_ha{args.ha}/3d/"
    duvw_file_path = base_data_path / args.file_name

    # Create the pickle filename by replacing the extension
    pkl_file_name = Path(args.file_name).with_suffix('.pkl').name
    pkl_store_file_path = base_data_path / "pkl" / pkl_file_name

    process_duvw_data(
        duvw_file=duvw_file_path,
        output_path=pkl_store_file_path,
        verify=args.verify,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()

