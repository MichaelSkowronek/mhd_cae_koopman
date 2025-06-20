#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Converts a single .pkl file containing a data dictionary into a
memory-efficient, compressed .npz file.
"""

import argparse
import sys
from pathlib import Path

# Attempt to import necessary modules.
try:
    from mhd_cae_koopman.utils.pickle_io import load_object
    from mhd_cae_koopman.utils.numpy_io import save_numpy_object
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(
        "\nPlease ensure that the 'mhd_cae_koopman' package is installed and "
        "accessible."
    )
    print("You might need to install it (e.g., 'pip install -e .') or adjust your PYTHONPATH.")
    sys.exit(1)


def main():
    """Main function to parse arguments and run the conversion."""
    parser = argparse.ArgumentParser(
        description="Convert a .pkl data file to a compressed .npz file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the source .pkl file.",
    )
    parser.add_argument(
        "output_file",
        type=Path,
        help="Path for the destination compressed .npz file.",
    )
    args = parser.parse_args()

    if not args.input_file.is_file():
        print(f"Error: Input file not found at {args.input_file}")
        sys.exit(1)

    print(f"Loading data from: {args.input_file}")
    data_to_convert = load_object(args.input_file)

    if data_to_convert:
        print(f"Saving compressed data to: {args.output_file}")
        # The 'compressed=True' argument is the default in our function.
        save_numpy_object(data_to_convert, args.output_file, compressed=True)
        print("\nConversion complete.")
    else:
        print(f"Failed to load data from {args.input_file}. Aborting.")
        sys.exit(1)


if __name__ == "__main__":
    main()
