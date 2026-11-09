#!/bin/bash
# review-history.sh - Query DevFlow review history

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

DB_PATH="$HOME/.devflow/devflow.db"

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo -e "${RED}Error: DevFlow database not found at $DB_PATH${NC}"
    echo "Run a review first to create the database."
    exit 1
fi

# Check if project_id provided
if [ -z "$1" ]; then
    # No project ID - show all projects
    echo -e "${GREEN}DevFlow Projects:${NC}"
    echo ""
    sqlite3 "$DB_PATH" << 'EOF'
.mode column
.headers on
.width 36 25 60
SELECT
    id,
    name,
    path
FROM projects
ORDER BY created_at DESC;
EOF
    echo ""
    echo "Usage: $0 PROJECT_ID [LIMIT]"
    echo "  PROJECT_ID: UUID from above (or 'latest' for most recent project)"
    echo "  LIMIT: Number of reviews to show (default: 10)"
    exit 0
fi

PROJECT_ID="$1"
LIMIT="${2:-10}"

# Handle 'latest' keyword
if [ "$PROJECT_ID" = "latest" ]; then
    PROJECT_ID=$(sqlite3 "$DB_PATH" "SELECT id FROM projects ORDER BY created_at DESC LIMIT 1;")
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}Error: No projects found${NC}"
        exit 1
    fi
fi

# Get project info
PROJECT_INFO=$(sqlite3 "$DB_PATH" "SELECT name, path FROM projects WHERE id='$PROJECT_ID';")
if [ -z "$PROJECT_INFO" ]; then
    echo -e "${RED}Error: Project not found: $PROJECT_ID${NC}"
    exit 1
fi

PROJECT_NAME=$(echo "$PROJECT_INFO" | cut -d'|' -f1)
PROJECT_PATH=$(echo "$PROJECT_INFO" | cut -d'|' -f2)

echo -e "${GREEN}Review History for: $PROJECT_NAME${NC}"
echo "  Path: $PROJECT_PATH"
echo "  Project ID: $PROJECT_ID"
echo ""

# Get review summary
TOTAL_REVIEWS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM reviews WHERE project_id='$PROJECT_ID';")
PASSED_REVIEWS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM reviews WHERE project_id='$PROJECT_ID' AND passed=1;")
PASS_RATE=$(sqlite3 "$DB_PATH" "SELECT ROUND(CAST(SUM(passed) AS FLOAT) / COUNT(*) * 100, 1) FROM reviews WHERE project_id='$PROJECT_ID';")

echo -e "${BLUE}Summary:${NC}"
echo "  Total reviews: $TOTAL_REVIEWS"
echo "  Passed: $PASSED_REVIEWS"
echo "  Pass rate: ${PASS_RATE}%"
echo ""

# Get recent reviews
echo -e "${BLUE}Recent Reviews (last $LIMIT):${NC}"
echo ""

sqlite3 "$DB_PATH" << EOF
.mode column
.headers on
.width 20 10 10 12 40
SELECT
    datetime(created_at, 'localtime') as 'Date',
    CASE WHEN passed = 1 THEN '✓ PASS' ELSE '✗ FAIL' END as 'Status',
    critical_issues as 'Critical',
    high_issues as 'High',
    CASE
        WHEN overall_assessment = 'APPROVED' THEN '✓ Approved'
        WHEN overall_assessment = 'NEEDS_WORK' THEN '⚠ Needs work'
        WHEN overall_assessment = 'BLOCKED' THEN '🛑 Blocked'
        ELSE overall_assessment
    END as 'Assessment'
FROM reviews
WHERE project_id='$PROJECT_ID'
ORDER BY created_at DESC
LIMIT $LIMIT;
EOF

echo ""

# Get issue breakdown for latest review
LATEST_REVIEW_ID=$(sqlite3 "$DB_PATH" "SELECT id FROM reviews WHERE project_id='$PROJECT_ID' ORDER BY created_at DESC LIMIT 1;")

if [ -n "$LATEST_REVIEW_ID" ]; then
    echo -e "${BLUE}Latest Review Issues:${NC}"
    echo ""

    CRITICAL_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM review_issues WHERE review_id='$LATEST_REVIEW_ID' AND severity='CRITICAL';")
    HIGH_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM review_issues WHERE review_id='$LATEST_REVIEW_ID' AND severity='HIGH';")
    MEDIUM_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM review_issues WHERE review_id='$LATEST_REVIEW_ID' AND severity='MEDIUM';")
    LOW_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM review_issues WHERE review_id='$LATEST_REVIEW_ID' AND severity='LOW';")

    echo -e "  🔴 CRITICAL: $CRITICAL_COUNT"
    echo -e "  🟠 HIGH: $HIGH_COUNT"
    echo -e "  🟡 MEDIUM: $MEDIUM_COUNT"
    echo -e "  🔵 LOW: $LOW_COUNT"

    # Show critical issues if any
    if [ "$CRITICAL_COUNT" -gt 0 ]; then
        echo ""
        echo -e "${RED}Critical Issues:${NC}"
        sqlite3 "$DB_PATH" << EOF
.mode list
SELECT '  • ' || file_path || ':' || line_number || ' - ' || message
FROM review_issues
WHERE review_id='$LATEST_REVIEW_ID' AND severity='CRITICAL'
LIMIT 5;
EOF
        if [ "$CRITICAL_COUNT" -gt 5 ]; then
            echo "  ... and $(($CRITICAL_COUNT - 5)) more"
        fi
    fi

    # Show high issues if any
    if [ "$HIGH_COUNT" -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}High Priority Issues:${NC}"
        sqlite3 "$DB_PATH" << EOF
.mode list
SELECT '  • ' || file_path || ':' || line_number || ' - ' || message
FROM review_issues
WHERE review_id='$LATEST_REVIEW_ID' AND severity='HIGH'
LIMIT 3;
EOF
        if [ "$HIGH_COUNT" -gt 3 ]; then
            echo "  ... and $(($HIGH_COUNT - 3)) more"
        fi
    fi
fi

echo ""

# Show trend
echo -e "${BLUE}Quality Trend:${NC}"
echo ""

sqlite3 "$DB_PATH" << EOF
.mode column
.headers on
.width 20 10 10 10 10
SELECT
    datetime(created_at, 'localtime') as 'Date',
    critical_issues as 'Critical',
    high_issues as 'High',
    medium_issues as 'Medium',
    low_issues as 'Low'
FROM reviews
WHERE project_id='$PROJECT_ID'
ORDER BY created_at DESC
LIMIT 5;
EOF

echo ""
echo "Database location: $DB_PATH"
echo ""
echo "Commands:"
echo "  View all projects: $0"
echo "  View specific project: $0 PROJECT_ID"
echo "  View more reviews: $0 PROJECT_ID 20"
