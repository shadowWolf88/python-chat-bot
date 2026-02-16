#!/bin/bash
# =============================================================================
# Healing Space - Test Runner Script
# =============================================================================
# Usage:
#   ./run_tests.sh              # Run all tests
#   ./run_tests.sh backend      # Backend unit tests only
#   ./run_tests.sh e2e          # E2E journey tests only
#   ./run_tests.sh coverage     # All tests with coverage report
#   ./run_tests.sh quick        # Fast run (parallel, no coverage)
#   ./run_tests.sh security     # Security-focused tests only
#   ./run_tests.sh clinical     # Clinical safety tests only
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Healing Space Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

MODE="${1:-all}"

case "$MODE" in
    backend)
        echo -e "${YELLOW}Running backend unit tests...${NC}"
        python -m pytest tests/backend/ -v --tb=short
        ;;
    e2e)
        echo -e "${YELLOW}Running E2E journey tests...${NC}"
        python -m pytest tests/e2e/ -v --tb=short
        ;;
    coverage)
        echo -e "${YELLOW}Running all tests with coverage...${NC}"
        python -m pytest tests/ -v --tb=short \
            --cov=api --cov-config=.coveragerc \
            --cov-report=term-missing \
            --cov-report=html:tests/coverage_html
        echo ""
        echo -e "${GREEN}Coverage HTML report: tests/coverage_html/index.html${NC}"
        ;;
    quick)
        echo -e "${YELLOW}Running quick parallel tests...${NC}"
        python -m pytest tests/backend/ -x --tb=line -q -n auto 2>/dev/null || \
        python -m pytest tests/backend/ -x --tb=line -q
        ;;
    security)
        echo -e "${YELLOW}Running security-focused tests...${NC}"
        python -m pytest tests/backend/test_auth.py tests/backend/test_security.py -v --tb=short
        ;;
    clinical)
        echo -e "${YELLOW}Running clinical safety tests...${NC}"
        python -m pytest tests/backend/test_safety.py -v --tb=short
        ;;
    all)
        echo -e "${YELLOW}Running all tests...${NC}"
        python -m pytest tests/ -v --tb=short
        ;;
    *)
        echo -e "${RED}Unknown mode: $MODE${NC}"
        echo "Usage: ./run_tests.sh [all|backend|e2e|coverage|quick|security|clinical]"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Test run complete!${NC}"
echo -e "${GREEN}========================================${NC}"
