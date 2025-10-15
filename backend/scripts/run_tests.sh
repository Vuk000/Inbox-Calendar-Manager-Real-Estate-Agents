#!/bin/bash
# Backend test runner script

set -e

echo "🧪 Running RealInbox AI Backend Tests..."
echo "========================================"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Set test environment
export APP_ENV=testing
export DEBUG=false

# Run linting first
echo ""
echo "🔍 Running Black formatter check..."
black --check app/ tests/ || true

echo ""
echo "🔍 Running isort check..."
isort --check-only app/ tests/ || true

echo ""
echo "🔍 Running mypy type check..."
mypy app/ || true

# Run tests
echo ""
echo "🧪 Running pytest with coverage..."
pytest \
    --verbose \
    --cov=app \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-report=xml \
    --tb=short \
    -m "not slow" \
    "$@"

# Generate coverage badge (optional)
echo ""
echo "📊 Test Coverage Report:"
coverage report --show-missing

# Check minimum coverage
echo ""
echo "✅ Tests completed!"
echo "📁 HTML coverage report: htmlcov/index.html"

