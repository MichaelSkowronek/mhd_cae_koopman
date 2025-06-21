#!/bin/bash

# ==============================================================================
# This script merges all source .pkl files into large, UNCOMPRESSED .npz files
# for fast loading during ML tasks.
# ==============================================================================

# Exit immediately if a command exits with a non-zero status.
set -e

# --- User Configuration ---
# IMPORTANT: Set this variable to the absolute path of your top-level data directory.
# This is the only line you should need to edit.
DATA_DIR="/home/skowronek/Documents/PhD/nuclear_fusion_cooling/data"

# --- Script Configuration ---
HA_NUMBERS=(300 500 700 1000)

# Get the absolute path of the directory where this script is located.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
MERGE_SCRIPT="${SCRIPT_DIR}/merge_data.py"

# --- Sanity Checks ---
if [ "$DATA_DIR" == "/path/to/your/data_directory" ]; then
    echo "Error: Please edit this script and set the DATA_DIR variable to the correct path." >&2
    exit 1
fi

if [ ! -d "$DATA_DIR" ]; then
    echo "Error: The specified data directory does not exist: $DATA_DIR" >&2
    exit 1
fi

if [ ! -f "$MERGE_SCRIPT" ]; then
    echo "Error: The python helper script was not found at: $MERGE_SCRIPT" >&2
    exit 1
fi

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
