#!/bin/bash

# ==============================================================================
# This script creates COMPRESSED archives from existing uncompressed .npz files.
# It should be run after merge_all_uncompressed.sh has completed.
# ==============================================================================

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
HA_NUMBERS=(300 500 700 1000)
DATA_DIR="../../../../../../data"
COMPRESS_SCRIPT="compress_npz.py"

# --- Main Processing Loop ---
echo "================================================="
echo "Creating COMPRESSED archives from .npz files"
echo "================================================="

for ha in "${HA_NUMBERS[@]}"; do
    echo ""
    echo "--- Compressing for ha=$ha ---"
    
    # Define the input and output filenames
    BASE_PATH="${DATA_DIR}/re1000_ha${ha}/3d/pkl"
    UNCOMPRESSED_FILE="${BASE_PATH}/vxyz_jxyz_p_f_du_dv_dw_uncompressed.npz"
    COMPRESSED_FILE="${BASE_PATH}/vxyz_jxyz_p_f_du_dv_dw_compressed.npz"

    # Construct and run the command to compress the file
    COMMAND_COMPRESS="python $COMPRESS_SCRIPT $UNCOMPRESSED_FILE $COMPRESSED_FILE"
    echo "Running command: $COMMAND_COMPRESS"
    $COMMAND_COMPRESS
done

echo ""
echo "================================================="
echo "All compression complete."
echo "================================================="
