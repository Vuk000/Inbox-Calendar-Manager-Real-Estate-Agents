# RealInbox AI Backend Test Suite

Comprehensive test suite for RealInbox AI backend with 90%+ target coverage.

## Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared pytest fixtures
├── mocks/                         # Centralized API mocks
│   ├── claude_mock.py            # Anthropic Claude API
│   ├── gmail_mock.py             # Gmail API
│   ├── twilio_mock.py            # Twilio SMS/WhatsApp
│   └── pinecone_mock.py          # Pinecone vector store
├── fixtures/                      # Reusable test data
│   ├── email_fixtures.py         # Email test data
│   └── user_fixtures.py          # User & auth fixtures
├── unit/                          # Unit tests
│   └── agents/                   # AI agent tests
│       ├── test_triage_comprehensive.py
│       ├── test_draft_agent_comprehensive.py
│       └── test_lead_qualification_comprehensive.py
└── integration/                   # Integration tests
    └── test_email_endpoints.py   # API endpoint tests
```

## Running Tests

### Quick Start

```bash
# From backend directory
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/agents/test_triage_comprehensive.py

# Run with verbose output
pytest -v

# Run and stop at first failure
pytest -x
```

### Using the Test Script

```bash
# Make script executable
chmod +x scripts/run_tests.sh

# Run all tests with linting
./scripts/run_tests.sh

# Run only fast tests
./scripts/run_tests.sh -m "not slow"

# Run specific test
./scripts/run_tests.sh tests/unit/agents/test_triage_comprehensive.py::TestTriageHighPriority::test_offer_email_high_priority
```

## Test Categories

### Unit Tests (`tests/unit/`)

Test individual components in isolation with mocked dependencies.

**Agent Tests:**
- `test_triage_comprehensive.py` - Email triage and classification (157 lines)
- `test_draft_agent_comprehensive.py` - Draft generation (145 lines)
- `test_lead_qualification_comprehensive.py` - Lead scoring (130 lines)

**Coverage Target:** 95%+

### Integration Tests (`tests/integration/`)

Test API endpoints with real database connections (uses test DB).

**Endpoint Tests:**
- Email endpoints (`/api/v1/emails/*`)
- Draft endpoints (`/api/v1/drafts/*`)
- Task endpoints (`/api/v1/tasks/*`)
- Analytics endpoints (`/api/v1/analytics/*`)

**Coverage Target:** 85%+

### Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit          # Unit test
@pytest.mark.integration   # Integration test
@pytest.mark.slow          # Slow-running test
@pytest.mark.ai            # Requires AI API
@pytest.mark.db            # Requires database
```

Run specific markers:
```bash
pytest -m unit              # Only unit tests
pytest -m "not slow"        # Skip slow tests
pytest -m "ai and not slow" # AI tests that aren't slow
```

## Writing Tests

### Unit Test Example

```python
import pytest
from app.agents.triage_agent import TriageAgent
from tests.mocks.claude_mock import MockClaudeAPI

@pytest.mark.asyncio
async def test_triage_offer_email(offer_email, monkeypatch):
    """Test offer email classified as high priority"""
    agent = TriageAgent()
    
    # Mock Claude API response
    mock_response = MockClaudeAPI.get_triage_response(priority="high")
    mock_message = MockClaudeAPI.create_mock_message(mock_response)
    
    mock_client = Mock()
    mock_client.messages.create = Mock(return_value=mock_message)
    monkeypatch.setattr(agent, "client", mock_client)
    
    # Run test
    result = await agent.analyze_email(offer_email)
    
    # Assertions
    assert result["priority"] == "high"
    assert result["urgency_score"] >= 70
```

### Using Fixtures

```python
# Use built-in fixtures
def test_with_email_data(offer_email, lead_email, agent_info):
    # offer_email, lead_email, agent_info are fixtures
    assert offer_email["subject"] == "Offer on 456 Oak Avenue"
```

### Mocking External APIs

```python
from tests.mocks.claude_mock import MockClaudeAPI
from tests.mocks.gmail_mock import MockGmailAPI

# Mock Claude responses
mock_response = MockClaudeAPI.get_triage_response()

# Mock Gmail service
mock_gmail = MockGmailAPI()
messages = mock_gmail.users().messages().list(userId="me").execute()
```

## Coverage Requirements

- **Overall:** 90%+ coverage
- **Unit Tests:** 95%+ coverage
- **Integration Tests:** 85%+ coverage
- **Critical Paths:** 100% coverage (auth, security, agents)

### Viewing Coverage

```bash
# Generate HTML report
pytest --cov=app --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Report

```
Name                                Stmts   Miss  Cover
-------------------------------------------------------
app/__init__.py                         5      0   100%
app/agents/triage_agent.py            120      8    93%
app/agents/draft_agent.py             115     10    91%
app/agents/lead_qualification.py       95      5    95%
app/routers/emails.py                  85      7    92%
app/security/jwt_handler.py            45      2    96%
-------------------------------------------------------
TOTAL                                1250     85    93%
```

## Best Practices

### 1. Test Independence
- Each test should run independently
- Use fixtures for setup/teardown
- Don't rely on test execution order

### 2. Clear Test Names
```python
# Good
def test_offer_email_classified_as_high_priority()

# Bad
def test_email_1()
```

### 3. Arrange-Act-Assert Pattern
```python
def test_example():
    # Arrange: Set up test data
    email = {"subject": "Offer"}
    
    # Act: Execute the code being tested
    result = triage_agent.analyze(email)
    
    # Assert: Verify the outcome
    assert result["priority"] == "high"
```

### 4. Mock External Dependencies
- Always mock API calls (Anthropic, Gmail, Twilio)
- Use provided mocks in `tests/mocks/`
- Don't make real API calls in tests

### 5. Test Edge Cases
- Empty inputs
- Invalid data
- API failures (fallback behavior)
- Rate limits
- Timeouts

## CI/CD Integration

Tests run automatically on:
- Every push to `main` or `develop`
- Every pull request
- Scheduled nightly builds

### GitHub Actions Workflow

See `.github/workflows/test.yml`:
- Runs linting (Black, isort, mypy, Bandit)
- Runs unit tests with coverage
- Runs integration tests
- Uploads coverage to Codecov
- Fails build if coverage < 80%

## Troubleshooting

### Tests Failing Locally

```bash
# Clear pytest cache
pytest --cache-clear

# Reinstall dependencies
pip install -r requirements.txt

# Check environment variables
echo $DATABASE_URL
echo $ANTHROPIC_API_KEY
```

### Slow Tests

```bash
# Profile tests to find slow ones
pytest --durations=10

# Skip slow tests
pytest -m "not slow"
```

### Import Errors

```bash
# Ensure you're in the backend directory
cd backend

# Install in editable mode
pip install -e .
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready

# Check Redis is running
redis-cli ping

# Use test database
export DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/test_db
```

## Adding New Tests

### 1. Create Test File
```bash
# Unit test for new feature
touch tests/unit/test_new_feature.py

# Integration test
touch tests/integration/test_new_api.py
```

### 2. Write Tests
```python
import pytest

class TestNewFeature:
    """Test suite for new feature"""
    
    def test_basic_functionality(self):
        """Test basic feature works"""
        pass
    
    def test_edge_case(self):
        """Test edge case handling"""
        pass
    
    @pytest.mark.asyncio
    async def test_async_operation(self):
        """Test async operation"""
        pass
```

### 3. Run and Verify
```bash
# Run your new test
pytest tests/unit/test_new_feature.py -v

# Check coverage
pytest tests/unit/test_new_feature.py --cov=app.new_feature
```

### 4. Update This README
Document any new test categories or special requirements.

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Testing FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)

## Questions?

- Check existing tests for examples
- Review `conftest.py` for available fixtures
- See `tests/mocks/` for mock implementations
- Open an issue on GitHub for help

