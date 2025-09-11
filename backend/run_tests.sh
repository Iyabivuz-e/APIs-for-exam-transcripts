#!/bin/bash
# Test runner script for Exam Transcripts API

set -e

echo "🧪 Running Exam Transcripts API Tests"
echo "===================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in a virtual environment or have pytest available
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}⚠️  pytest not found. Installing dependencies...${NC}"
    pip install -r requirements.txt
fi

# Set environment variables for testing
export ENVIRONMENT=testing
export SECRET_KEY=test-secret-key
export DATABASE_URL=sqlite:///./test_exam_transcripts.db

# Run tests
echo -e "\n${YELLOW}Running unit tests...${NC}"
pytest tests/unit/ -v

echo -e "\n${YELLOW}Running integration tests...${NC}"
pytest tests/integration/ -v

echo -e "\n${YELLOW}Running all tests with coverage...${NC}"
pytest tests/ --cov=app --cov-report=term-missing

# Cleanup test database
if [ -f "test_exam_transcripts.db" ]; then
    rm test_exam_transcripts.db
fi

echo -e "\n${GREEN}✅ All tests completed!${NC}"
