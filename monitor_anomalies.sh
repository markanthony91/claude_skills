#!/bin/bash
################################################################################
# Automated Anomaly Detection Monitor
# Runs ML anomaly detection and sends alerts for critical issues
################################################################################

set -e

# Configuration
SCRIPT_DIR="/home/marcelo/sistemas"
DETECTOR_SCRIPT="$SCRIPT_DIR/anomaly_detector_ml.py"
REPORT_JSON="$SCRIPT_DIR/anomaly_detection_report.json"
REPORT_MD="$SCRIPT_DIR/ANOMALY_ANALYSIS_REPORT.md"
LOG_FILE="$SCRIPT_DIR/anomaly_monitor.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

echo "================================================================================"
echo "AUTOMATED ANOMALY DETECTION MONITOR"
echo "================================================================================"
echo ""

log "Starting anomaly detection analysis..."

# Check if detector script exists
if [ ! -f "$DETECTOR_SCRIPT" ]; then
    echo -e "${RED}ERROR: Detector script not found: $DETECTOR_SCRIPT${NC}"
    exit 1
fi

# Run anomaly detector
log "Executing ML anomaly detector..."
python3 "$DETECTOR_SCRIPT" 2>&1 | tee -a "$LOG_FILE"

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Anomaly detector failed!${NC}"
    log "ERROR: Anomaly detector execution failed"
    exit 1
fi

# Check if report was generated
if [ ! -f "$REPORT_JSON" ]; then
    echo -e "${RED}ERROR: Report not generated: $REPORT_JSON${NC}"
    exit 1
fi

log "Report generated successfully"

# Parse report and extract key metrics
TOTAL_FILES=$(jq -r '.metadata.total_files_analyzed' "$REPORT_JSON")
ANOMALIES=$(jq -r '.metadata.anomalies_detected' "$REPORT_JSON")
CONTAMINATION=$(jq -r '.metadata.contamination_rate' "$REPORT_JSON")

echo ""
echo "================================================================================"
echo "SUMMARY"
echo "================================================================================"
echo "Total Files Analyzed: $TOTAL_FILES"
echo "Anomalies Detected: $ANOMALIES"
echo "Contamination Rate: ${CONTAMINATION}%"
echo ""

log "Analysis complete: $TOTAL_FILES files, $ANOMALIES anomalies (${CONTAMINATION}%)"

# Check for high severity anomalies
HIGH_SEVERITY=$(jq '[.top_anomalies[] | select(.severity == "HIGH")] | length' "$REPORT_JSON")

if [ "$HIGH_SEVERITY" -gt 0 ]; then
    echo -e "${RED}⚠️  WARNING: $HIGH_SEVERITY HIGH severity anomalies detected!${NC}"
    log "WARNING: $HIGH_SEVERITY HIGH severity anomalies detected"

    echo ""
    echo "Top 5 Critical Anomalies:"
    jq -r '.top_anomalies[] | select(.severity == "HIGH") | "\(.filename) - \(.size_kb) KB - Score: \(.anomaly_score)"' "$REPORT_JSON" | head -5
    echo ""

    # Alert (customize this section for email/webhook notifications)
    echo "🔔 ALERT: Critical anomalies require investigation"

    # Example: Send email (uncomment and configure)
    # echo "Check report: $REPORT_MD" | mail -s "CRITICAL: Camera Anomalies Detected" admin@example.com

    # Example: Slack webhook (uncomment and configure)
    # curl -X POST -H 'Content-type: application/json' \
    #   --data "{\"text\":\"⚠️ ALERT: $HIGH_SEVERITY critical camera anomalies detected. Check $REPORT_MD\"}" \
    #   YOUR_SLACK_WEBHOOK_URL

else
    echo -e "${GREEN}✓ No critical anomalies detected${NC}"
    log "No critical anomalies detected"
fi

# Show recommendations
echo ""
echo "================================================================================"
echo "RECOMMENDATIONS"
echo "================================================================================"
jq -r '.recommendations[] | "[\(.priority)] \(.issue)\n   → \(.action)\n"' "$REPORT_JSON"

echo ""
echo "================================================================================"
echo "Full reports available at:"
echo "  - JSON: $REPORT_JSON"
echo "  - Markdown: $REPORT_MD"
echo "  - Log: $LOG_FILE"
echo "================================================================================"
echo ""

log "Monitor execution complete"

exit 0
