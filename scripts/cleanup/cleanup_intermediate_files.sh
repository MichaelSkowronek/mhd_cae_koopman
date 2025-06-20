#!/bin/bash

# ==============================================================================
# WARNING: This script PERMANENTLY DELETES files. Review carefully.
#
# This script cleans up intermediate data files that are no longer needed
# after the final .npz datasets have been created and verified. It targets
# raw .dat, .zip, and intermediate .pkl files across all specified
# Hartmann numbers.
# ==============================================================================

# --- Configuration ---

# IMPORTANT: This is the absolute path to your main data directory.
# This script is NOT portable and is hardcoded for this path.
BASE_DATA_DIR="/home/skowronek/Documents/PhD/nuclear_fusion_cooling/data"

# The Hartmann numbers to process.
HA_NUMBERS=(300 500 700 1000)

# List of file paths to delete, relative to the ".../re1000_ha<XXX>/3d/" directory.
FILES_TO_DELETE=(
    "du.dat"
    "dv.dat"
    "dw.dat"
    "du.zip"
    "dv.zip"
    "dw.zip"
    "vxyz_jxyz_p_f.dat"
    "vxyz_jxyz_p_f.zip"
    "pkl/du.pkl"
    "pkl/dv.pkl"
    "pkl/dw.pkl"
    "pkl/vxyz_jxyz_p_f.pkl"
)

# --- Safety Confirmation Prompt ---
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
echo "!!! DANGER: This script will PERMANENTLY DELETE files.       !!!"
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
echo "This script will attempt to delete the following file patterns:"
for pattern in "${FILES_TO_DELETE[@]}"; do
    echo "  - .../re1000_ha<XXX>/3d/${pattern}"
done
echo ""
echo "From the base directory: ${BASE_DATA_DIR}"
echo "For Hartmann numbers: ${HA_NUMBERS[*]}"
echo ""
read -p "Are you absolutely sure you want to proceed? Type 'yes' to continue: " CONFIRMATION

if [ "$CONFIRMATION" != "yes" ]; then
    echo "Aborting cleanup. No files were deleted."
    exit 1
fi

echo ""
echo "Confirmation received. Starting cleanup..."

# --- Main Processing Loop ---
for ha in "${HA_NUMBERS[@]}"; do
    HA_DIR="${BASE_DATA_DIR}/re1000_ha${ha}/3d"
    echo ""
    echo "--- Processing for ha=$ha in directory: $HA_DIR ---"

    for file_rel_path in "${FILES_TO_DELETE[@]}"; do
        FILE_TO_DELETE="${HA_DIR}/${file_rel_path}"

        if [ -f "$FILE_TO_DELETE" ]; then
            echo "Deleting: ${FILE_TO_DELETE}"
            rm -f "$FILE_TO_DELETE" # Use -f to avoid errors if file is missing
        else
            echo "Skipping (not found): ${FILE_TO_DELETE}"
        fi
    done
done

echo ""
echo "================================================="
echo "Cleanup script has finished."
echo "================================================="