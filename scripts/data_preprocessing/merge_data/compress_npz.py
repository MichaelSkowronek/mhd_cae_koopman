#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Compresses an existing uncompressed .npz file.

This utility script loads a specified .npz file and saves it again in the
compressed .npz format.
"""

import argparse
from pathlib import Path
import sys

# Attempt to import necessary modules.
try:
    from mhd_cae_koopman.utils.numpy_io import save_numpy_object, load_numpy_object
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(
        "\nPlease ensure that the 'mhd_cae_koopman' package is installed and "
        "accessible."
    )
    print("You might need to install it (e.g., 'pip install -e .') or adjust your PYTHONPATH.")
    sys.exit(1)


def main():
    """Main function to parse arguments and run the compression."""
    parser = argparse.ArgumentParser(
        description="Load an uncompressed .npz file and save it as a compressed .npz file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the source uncompressed .npz file.",
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
    data_to_compress = load_numpy_object(args.input_file)

    print(f"Saving compressed data to: {args.output_file}")
    # The 'compressed=True' argument is the default, but we set it explicitly for clarity.
    save_numpy_object(data_to_compress, args.output_file, compressed=True)
    
    print("\nCompression complete.")


if __name__ == "__main__":
    main()
