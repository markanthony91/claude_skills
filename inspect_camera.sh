#!/bin/bash
################################################################################
# Camera Inspector - Detailed analysis of specific camera/store
# Usage: ./inspect_camera.sh [store_name]
################################################################################

set -e

CAMERAS_DIR="/home/marcelo/sistemas/captura_cameras/cameras"
REPORT_JSON="/home/marcelo/sistemas/anomaly_detection_report.json"

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "ERROR: jq is required. Install with: sudo apt-get install jq"
    exit 1
fi

# Function to show usage
usage() {
    echo "Usage: $0 [store_name]"
    echo ""
    echo "Examples:"
    echo "  $0 Marginal_Tiete_Pte_Anhanguera"
    echo "  $0 Prestes_Maia"
    echo "  $0 \"list\"  # Show all stores with anomalies"
    exit 1
}

# List stores with anomalies
list_anomalous_stores() {
    echo "================================================================================"
    echo "STORES WITH DETECTED ANOMALIES"
    echo "================================================================================"
    echo ""

    if [ ! -f "$REPORT_JSON" ]; then
        echo "ERROR: Run anomaly detector first: python3 anomaly_detector_ml.py"
        exit 1
    fi

    jq -r '.top_anomalies | group_by(.directory) | map({
        store: .[0].directory,
        anomaly_count: length,
        avg_score: (map(.anomaly_score) | add / length),
        severity: .[0].severity
    }) | sort_by(.avg_score) | .[] | "[\(.severity)] \(.store) - \(.anomaly_count) anomalies (avg score: \(.avg_score | tonumber | . * 100 | round / 100))"' "$REPORT_JSON"

    echo ""
    echo "================================================================================"
}

# Inspect specific store
inspect_store() {
    STORE_NAME="$1"
    STORE_PATH="$CAMERAS_DIR/$STORE_NAME"

    if [ ! -d "$STORE_PATH" ]; then
        echo "ERROR: Store directory not found: $STORE_PATH"
        echo ""
        echo "Available stores:"
        ls -1 "$CAMERAS_DIR" | head -20
        echo "..."
        exit 1
    fi

    echo "================================================================================"
    echo "DETAILED CAMERA INSPECTION: $STORE_NAME"
    echo "================================================================================"
    echo ""

    # Count files
    TOTAL_FILES=$(find "$STORE_PATH" -type f -name "*.jpg" | wc -l)
    echo "📁 Total Files: $TOTAL_FILES"
    echo ""

    # Analyze by camera position
    echo "📷 FILES BY CAMERA POSITION:"
    echo "-----------------------------------"
    for cam in P1 P2 P3; do
        COUNT=$(find "$STORE_PATH" -type f -name "${cam}_*.jpg" | wc -l)
        if [ $COUNT -gt 0 ]; then
            echo "  $cam: $COUNT files"

            # Get size statistics
            SIZES=$(find "$STORE_PATH" -type f -name "${cam}_*.jpg" -exec ls -l {} \; | awk '{print $5}')
            TOTAL_SIZE=$(echo "$SIZES" | awk '{sum+=$1} END {print sum}')
            AVG_SIZE=$(echo "$SIZES" | awk '{sum+=$1; count++} END {print sum/count}')
            MIN_SIZE=$(echo "$SIZES" | sort -n | head -1)
            MAX_SIZE=$(echo "$SIZES" | sort -n | tail -1)

            AVG_KB=$(echo "scale=2; $AVG_SIZE / 1024" | bc)
            MIN_KB=$(echo "scale=2; $MIN_SIZE / 1024" | bc)
            MAX_KB=$(echo "scale=2; $MAX_SIZE / 1024" | bc)

            echo "     Avg Size: ${AVG_KB} KB | Range: ${MIN_KB} - ${MAX_KB} KB"
        fi
    done
    echo ""

    # Date range
    echo "📅 DATE RANGE:"
    echo "-----------------------------------"
    OLDEST=$(find "$STORE_PATH" -type f -name "*.jpg" -printf '%T+ %p\n' | sort | head -1 | awk '{print $1}')
    NEWEST=$(find "$STORE_PATH" -type f -name "*.jpg" -printf '%T+ %p\n' | sort | tail -1 | awk '{print $1}')
    echo "  Oldest: $OLDEST"
    echo "  Newest: $NEWEST"
    echo ""

    # Check for anomalies in report
    echo "🔍 ANOMALY ANALYSIS:"
    echo "-----------------------------------"

    if [ -f "$REPORT_JSON" ]; then
        ANOMALY_COUNT=$(jq "[.top_anomalies[] | select(.directory == \"$STORE_NAME\")] | length" "$REPORT_JSON")

        if [ "$ANOMALY_COUNT" -gt 0 ]; then
            echo "  ⚠️  $ANOMALY_COUNT anomalous files detected"
            echo ""
            echo "  Top 5 Anomalies:"
            jq -r ".top_anomalies[] | select(.directory == \"$STORE_NAME\") | \"    - \(.filename) | \(.size_kb) KB | Severity: \(.severity) | Score: \(.anomaly_score)\"" "$REPORT_JSON" | head -5
        else
            echo "  ✓ No anomalies detected for this store"
        fi
    else
        echo "  (Run anomaly detector to see anomaly analysis)"
    fi
    echo ""

    # Recent files
    echo "📋 5 MOST RECENT FILES:"
    echo "-----------------------------------"
    find "$STORE_PATH" -type f -name "*.jpg" -printf '%T+ %p %s\n' | sort -r | head -5 | while read timestamp path size; do
        filename=$(basename "$path")
        size_kb=$(echo "scale=2; $size / 1024" | bc)
        echo "  $filename"
        echo "    Date: $timestamp | Size: ${size_kb} KB"
    done
    echo ""

    # Storage summary
    TOTAL_SIZE_BYTES=$(find "$STORE_PATH" -type f -name "*.jpg" -exec ls -l {} \; | awk '{sum+=$5} END {print sum}')
    TOTAL_SIZE_MB=$(echo "scale=2; $TOTAL_SIZE_BYTES / 1024 / 1024" | bc)

    echo "💾 STORAGE SUMMARY:"
    echo "-----------------------------------"
    echo "  Total Storage: ${TOTAL_SIZE_MB} MB"
    echo "  Average per File: $(echo "scale=2; $TOTAL_SIZE_BYTES / $TOTAL_FILES / 1024" | bc) KB"
    echo ""

    echo "================================================================================"
    echo "RECOMMENDATIONS FOR: $STORE_NAME"
    echo "================================================================================"

    if [ -f "$REPORT_JSON" ]; then
        ANOMALY_COUNT=$(jq "[.top_anomalies[] | select(.directory == \"$STORE_NAME\")] | length" "$REPORT_JSON")

        if [ "$ANOMALY_COUNT" -gt 0 ]; then
            echo ""
            echo "⚠️  ACTION REQUIRED:"
            echo "  1. Inspect camera hardware at this location"
            echo "  2. Verify network connectivity from cameras to server"
            echo "  3. Check camera configuration (resolution, compression settings)"
            echo "  4. Compare with known good cameras to identify differences"
            echo "  5. Consider replacing/reconfiguring cameras if issue persists"
            echo ""
        else
            echo ""
            echo "✓ Camera system at this location appears healthy"
            echo "  No anomalies detected. Continue regular monitoring."
            echo ""
        fi
    fi

    echo "================================================================================"
}

# Main execution
if [ $# -eq 0 ]; then
    usage
fi

if [ "$1" = "list" ]; then
    list_anomalous_stores
else
    inspect_store "$1"
fi
