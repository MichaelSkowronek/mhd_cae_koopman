#!/bin/bash

# ==============================================================================
# This script automates the processing of the Tecplot data file
# 'vxyz_jxyz_p_f.dat' for a range of different Hartmann numbers (ha).
# ==============================================================================

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
HA_NUMBERS=(300 500 700 1000)
FILE_NAME="vxyz_jxyz_p_f.dat"
DATA_DIR="../../../../../../data/"
PYTHON_SCRIPT="store_tecplot_as_pickle.py"

# --- Main Processing Loop ---
echo "Starting Tecplot data processing batch job..."

# Loop over each Hartmann number
for ha in "${HA_NUMBERS[@]}"; do
    echo ""
    echo "================================================="
    echo "Processing for Hartmann number (ha): $ha"
    echo "================================================="
    
    # Construct the full command
    COMMAND="python $PYTHON_SCRIPT --ha $ha --file_name $FILE_NAME --data_dir $DATA_DIR --verify"
    
    # Print the command for logging purposes
    echo "Running command: $COMMAND"
    echo ""
    
    # Execute the command
    $COMMAND
    
    echo ""
    echo "--- Finished processing for ha=$ha ---"
done

echo ""
echo "================================================="
echo "All Tecplot processing complete."
echo "================================================="
