#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Merges processed data files into a single comprehensive dataset.

This script loads the individual processed .pkl files for a given Hartmann
number, validates their consistency, and concatenates them into a single,
compressed (default) or uncompressed .npz file.
"""

import argparse
import sys
import gc
from pathlib import Path

import numpy as np

# Attempt to import necessary modules.
try:
    from mhd_cae_koopman.data_processing.concatenation import load_and_concatenate_data
    from mhd_cae_koopman.data_processing.utils import print_timeseries_info
    # Import the NEW numpy-based save/load functions
    from mhd_cae_koopman.utils.numpy_io import save_numpy_object, load_numpy_object
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(
        "\nPlease ensure that the 'mhd_cae_koopman' package is installed and "
        "accessible."
    )
    print("You might need to install it (e.g., 'pip install -e .') or adjust your PYTHONPATH.")
    sys.exit(1)


def process_and_merge_data(
    input_paths: dict,
    output_path: Path,
    uncompressed: bool = False,
    verify: bool = False,
    verbose: bool = True,
):
    """
    Loads, concatenates, saves, and optionally verifies the merged dataset.

    Args:
        input_paths (dict): A dictionary mapping dataset names to their file paths.
        output_path (Path): The path where the final merged .npz file will be saved.
        uncompressed (bool): If True, saves a larger, uncompressed file for faster I/O.
                             Default is False (saves a compressed file).
        verify (bool, optional): If True, loads the final file after saving
                                 to verify its contents. Defaults to False.
        verbose (bool, optional): If True, prints detailed information. Defaults to True.
    """
    try:
        concatenated_data = load_and_concatenate_data(
            path_vxyz_jxyz_p_f=input_paths['vxyz_jxyz_p_f'],
            path_du=input_paths['du'],
            path_dv=input_paths['dv'],
            path_dw=input_paths['dw'],
        )

        if verbose:
            print("\n--- Final Merged Data Summary ---")
            print_timeseries_info(
                concatenated_data['timeseries'],
                concatenated_data['labels'],
            )

        print(f"\nSaving final concatenated data to: {output_path}")
        # Pass the compression flag to the save function
        save_numpy_object(concatenated_data, output_path, compressed=not uncompressed)

        if verify:
            print("\n--- Verification Step (First Snapshot Only & Memory-Safe) ---")

            original_first_snapshot = concatenated_data['timeseries'][0].copy()
            original_labels = concatenated_data['labels']

            print("Releasing memory from original concatenated data...")
            del concatenated_data
            gc.collect()

            print(f"Loading final data from file for verification: {output_path}")
            loaded_final_data = load_numpy_object(output_path)
            
            print_timeseries_info(
                loaded_final_data['timeseries'],
                loaded_final_data['labels']
            )

            assert original_first_snapshot.shape == loaded_final_data['timeseries'][0].shape, "Shape mismatch."
            assert original_labels == loaded_final_data['labels'], "Label mismatch."

            print("Verifying array data integrity for the first snapshot...")
            if np.array_equal(original_first_snapshot, loaded_final_data['timeseries'][0]):
                print("Verification successful: First snapshot matches.")
            else:
                raise AssertionError("Verification failed: Data mismatch in the first snapshot.")

    except (ValueError, FileNotFoundError) as e:
        print(f"\nAn error occurred during data processing: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)


def main():
    """Main function to parse arguments and run the data merging."""
    parser = argparse.ArgumentParser(
        description="Merge processed data files into a single .npz dataset.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--ha",
        type=int,
        default=300,
        help="Hartmann number (Ha) to specify the data subdirectory.",
    )
    parser.add_argument(
        "--data_dir",
        type=Path,
        default=Path("../../../../../../data"),
        help="Path to the main data directory.",
    )
    parser.add_argument(
        "--uncompressed",
        action='store_true',
        help="Save as a larger, uncompressed .npz file for faster loading.",
    )
    parser.add_argument(
        "--verify",
        action='store_true',
        help="If set, verify the final .npz file after creation by loading it.",
    )
    parser.add_argument(
        "--quiet",
        action='store_true',
        help="If set, suppress detailed print output.",
    )

    args = parser.parse_args()

    pkl_files = ['vxyz_jxyz_p_f', 'du', 'dv', 'dw']
    
    # Adjust output filename based on compression choice for clarity
    if args.uncompressed:
        output_file_name = "vxyz_jxyz_p_f_du_dv_dw_uncompressed.npz"
    else:
        output_file_name = "vxyz_jxyz_p_f_du_dv_dw_compressed.npz"
    
    base_data_path = args.data_dir / f"re1000_ha{args.ha}/3d/pkl/"
    
    if not base_data_path.is_dir():
        print(f"Error: Input directory not found at {base_data_path.resolve(strict=True)}")
        sys.exit(1)

    input_paths = {name: base_data_path / f"{name}.pkl" for name in pkl_files}
    output_path = base_data_path / output_file_name

    process_and_merge_data(
        input_paths=input_paths,
        output_path=output_path,
        uncompressed=args.uncompressed,
        verify=args.verify,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
