#!/bin/bash

# ==============================================================================
# This script merges all source .pkl files into large, UNCOMPRESSED .npz files
# for fast loading during ML tasks.
# ==============================================================================

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
HA_NUMBERS=(300 500 700 1000)
DATA_DIR="../../../../../../data/"
MERGE_SCRIPT="merge_data.py"

# --- Main Processing Loop ---
echo "================================================="
echo "Merging data into UNCOMPRESSED .npz files"
echo "================================================="

for ha in "${HA_NUMBERS[@]}"; do
    echo ""
    echo "--- Merging for ha=$ha (uncompressed) ---"
    
    # Construct and run the command to create the uncompressed file
    # The --uncompressed flag ensures a fast-loading .npz file is created
    COMMAND_MERGE="python $MERGE_SCRIPT --ha $ha --data_dir $DATA_DIR --uncompressed --verify"
    echo "Running command: $COMMAND_MERGE"
    $COMMAND_MERGE
done

echo ""
echo "================================================="
echo "All uncompressed merging complete."
echo "================================================="
