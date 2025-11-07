#!/bin/bash
# Automatically find most recent ADIF file and update SKCC contacts

echo "===================================="
echo "SKCC Contact Auto-Update Script"
echo "===================================="
echo

# Search for ADIF files in common locations
SEARCH_PATHS=(
    "$HOME/logs"
    "$HOME/Logs"
    "$HOME/Documents/logs"
    "$HOME/Documents/SKCC Logger"
    "$HOME/.skcc_logger"
    "$HOME/Downloads"
    "$HOME"
    "/home/user/logs"
    "/home/user/Logs"
)

echo "Searching for ADIF files..."
ADIF_FILES=()

for path in "${SEARCH_PATHS[@]}"; do
    if [ -d "$path" ]; then
        echo "  Checking: $path"
        while IFS= read -r file; do
            ADIF_FILES+=("$file")
        done < <(find "$path" -maxdepth 2 -type f \( -name "*.adi" -o -name "*.adif" \) 2>/dev/null)
    fi
done

if [ ${#ADIF_FILES[@]} -eq 0 ]; then
    echo
    echo "❌ No ADIF files found!"
    echo
    echo "Please specify the path to your SKCC Logger ADIF file:"
    echo "  python3 update_skcc_from_adif.py /path/to/your/file.adi"
    echo
    echo "Common SKCC Logger locations:"
    echo "  Windows: C:\\Users\\<YourName>\\Documents\\SKCC Logger\\"
    echo "  Mac/Linux: ~/Documents/SKCC Logger/"
    exit 1
fi

echo
echo "Found ${#ADIF_FILES[@]} ADIF file(s):"
echo

# Sort by modification time and show list
for i in "${!ADIF_FILES[@]}"; do
    file="${ADIF_FILES[$i]}"
    mtime=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null)
    size=$(stat -c %s "$file" 2>/dev/null || stat -f %z "$file" 2>/dev/null)
    date=$(stat -c %y "$file" 2>/dev/null | cut -d' ' -f1 || stat -f %Sm "$file" 2>/dev/null)
    printf "%2d) %s\n" $((i+1)) "$file"
    printf "    Modified: %s | Size: %s bytes\n" "$date" "$size"
done

echo
echo "Which file do you want to use?"
echo "  Enter number (1-${#ADIF_FILES[@]}), or 'q' to quit"
echo "  Press ENTER to use most recent file"
read -p "Choice: " choice

if [ "$choice" = "q" ] || [ "$choice" = "Q" ]; then
    echo "Cancelled."
    exit 0
fi

# Default to most recent (first in list after sorting)
if [ -z "$choice" ]; then
    # Find most recent by modification time
    MOST_RECENT=""
    NEWEST_TIME=0
    for file in "${ADIF_FILES[@]}"; do
        mtime=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null)
        if [ "$mtime" -gt "$NEWEST_TIME" ]; then
            NEWEST_TIME=$mtime
            MOST_RECENT="$file"
        fi
    done
    SELECTED_FILE="$MOST_RECENT"
else
    # Use user's choice
    idx=$((choice - 1))
    if [ $idx -ge 0 ] && [ $idx -lt ${#ADIF_FILES[@]} ]; then
        SELECTED_FILE="${ADIF_FILES[$idx]}"
    else
        echo "Invalid choice!"
        exit 1
    fi
fi

echo
echo "Using: $SELECTED_FILE"
echo
echo "Running update script..."
echo

cd "$(dirname "$0")"
python3 update_skcc_from_adif.py "$SELECTED_FILE"
