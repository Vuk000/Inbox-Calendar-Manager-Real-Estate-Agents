#!/bin/bash
# Frontend test runner script

set -e

echo "🧪 Running RealInbox AI Frontend Tests..."
echo "========================================="

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Run linting first
echo ""
echo "🔍 Running ESLint..."
npm run lint || true

# Run type checking
echo ""
echo "🔍 Running TypeScript type check..."
npx tsc --noEmit || true

# Run tests
echo ""
echo "🧪 Running Vitest with coverage..."
npx vitest run --coverage "$@"

# Show coverage summary
echo ""
echo "📊 Test Coverage Summary:"
echo "Coverage report available at: coverage/index.html"

echo ""
echo "✅ Frontend tests completed!"

