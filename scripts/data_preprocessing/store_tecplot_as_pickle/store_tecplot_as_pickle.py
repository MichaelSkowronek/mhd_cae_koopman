#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Processes Tecplot data files and stores them as pickle files.

This script reads a Tecplot timeseries data file, processes it, and
saves the result in a serialized format (pickle) for faster access
in subsequent analysis. It also includes an option to verify the
saved data.
"""

import argparse
from pathlib import Path
import sys


# Attempt to import necessary modules. Provide guidance if imports fail.
try:
    from mhd_cae_koopman.utils import save_object, load_object
    from mhd_cae_koopman.data_processing.tecplot_data import parse_tecplot_timeseries
    from mhd_cae_koopman.data_processing.utils import print_timeseries_info
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("\nPlease ensure that the 'mhd_cae_koopman' package is installed and accessible.")
    print("You might need to install it (e.g., 'pip install .') or adjust your PYTHONPATH.")
    sys.exit(1)


def process_tecplot_data(
    tecplot_file: Path,
    output_path: Path,
    verify: bool = False,
    verbose: bool = True,
):
    """
    Loads data from a Tecplot file, saves it as a pickle, and optionally verifies.

    Args:
        tecplot_file (Path): The path to the input Tecplot .dat file.
        output_path (Path): The path where the output .pkl file will be saved.
        verify (bool, optional): If True, loads the pickle file after saving to
                                 verify its contents. Defaults to False.
        verbose (bool, optional): If True, prints detailed information about the
                                  processed data. Defaults to True.
    """
    if not tecplot_file.is_file():
        print(f"Error: Tecplot file not found at {tecplot_file}")
        sys.exit(1)

    print(f"Loading data from: {tecplot_file}")
    data = {}
    data['timeseries'], data['labels'] = parse_tecplot_timeseries(tecplot_file)

    if verbose:
        print("\n--- Loaded Data Summary ---")
        print_timeseries_info(data['timeseries'], data['labels'])

    # Ensure the output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nSaving processed data to: {output_path}")
    save_object(data, output_path)

    if verify:
        print("\n--- Verification Step ---")
        print(f"Loading data from pickle file for verification: {output_path}")
        loaded_data = load_object(output_path)
        print_timeseries_info(loaded_data['timeseries'], loaded_data['labels'])
        print("Verification successful.")


def main():
    """Main function to parse arguments and run the data processing."""
    parser = argparse.ArgumentParser(
        description="Convert Tecplot data files to pickle format.",
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
        default="vxyz_jxyz_p_f.dat",
        help="Name of the Tecplot file (including e.g. .dat extension).",
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
    tecplot_file_path = base_data_path / args.file_name
    
    # Create the pickle filename by replacing the extension
    pkl_file_name = Path(args.file_name).with_suffix('.pkl').name
    pkl_store_file_path = base_data_path / "pkl" / pkl_file_name

    process_tecplot_data(
        tecplot_file=tecplot_file_path,
        output_path=pkl_store_file_path,
        verify=args.verify,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
