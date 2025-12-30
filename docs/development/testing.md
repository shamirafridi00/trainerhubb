# Testing Guide for TrainerHubb

This document provides comprehensive information about the testing strategy and how to run tests for the TrainerHubb platform.

## Overview

The TrainerHubb platform has three layers of testing:

1. **Backend Unit Tests** - Test individual components (models, serializers, views, services)
2. **Frontend Component Tests** - Test React components, hooks, and state management
3. **Integration Tests** - Test complete user flows across the system

## Backend Tests

### Running Backend Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.users
python manage.py test apps.trainers
python manage.py test apps.clients
python manage.py test apps.bookings
python manage.py test apps.packages
python manage.py test apps.payments
python manage.py test apps.pages
python manage.py test apps.workflows

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generates HTML coverage report
```

### Backend Test Structure

```
apps/
├── users/tests.py              # User and authentication tests
├── trainers/tests.py           # Trainer profile and white-label tests
├── clients/tests.py            # Client management tests
├── bookings/tests.py           # Booking and availability tests
├── packages/tests.py           # Service and package tests
├── payments/tests.py           # Subscription and payment tracking tests
├── pages/tests.py              # Page builder tests
└── workflows/tests.py          # Workflow automation tests
```

### Test Coverage Goals

- **Target**: 80%+ code coverage
- **Priority Areas**:
  - Authentication and authorization
  - Feature gating logic
  - Payment processing
  - Workflow execution
  - API endpoints

## Frontend Tests

### Running Frontend Tests

```bash
cd trainer-app

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with UI
npm run test:ui

# Run with coverage
npm run test:coverage
```

### Frontend Test Structure

```
trainer-app/src/
├── store/__tests__/
│   └── authStore.test.ts       # Auth store tests
├── pages/__tests__/
│   └── LoginPage.test.tsx      # Page component tests
├── components/__tests__/
│   └── (component tests)       # Component tests
└── hooks/__tests__/
    └── useSubscription.test.ts # Hook tests
```

### Frontend Test Technologies

- **Vitest** - Test runner
- **React Testing Library** - Component testing
- **@testing-library/jest-dom** - DOM matchers
- **@testing-library/user-event** - User interaction simulation

## Integration Tests

### Running Integration Tests

```bash
# Run all integration tests
python manage.py test tests.integration

# Run specific integration test
python manage.py test tests.integration.test_auth_flow
python manage.py test tests.integration.test_subscription_flow
python manage.py test tests.integration.test_booking_flow
python manage.py test tests.integration.test_page_builder_flow
python manage.py test tests.integration.test_workflow_execution
```

### Integration Test Structure

```
tests/integration/
├── __init__.py
├── test_auth_flow.py           # Registration → Login → Dashboard
├── test_subscription_flow.py   # Subscription upgrade → Feature unlock
├── test_booking_flow.py        # Client → Booking → Payment
├── test_page_builder_flow.py  # Page creation → Publishing → Public access
└── test_workflow_execution.py  # Workflow → Trigger → Action execution
```

### Integration Test Scenarios

1. **Authentication Flow**
   - User registration
   - Login/logout
   - Password reset
   - Token authentication

2. **Subscription Flow**
   - Free plan limits
   - Upgrade to Pro/Business
   - Feature unlocking
   - Subscription expiration

3. **Booking Flow**
   - Client creation
   - Booking creation
   - Payment recording
   - Public booking (unauthenticated)
   - Booking cancellation

4. **Page Builder Flow**
   - Template selection
   - Page creation
   - Section management
   - SEO settings
   - Publishing/unpublishing

5. **Workflow Execution**
   - Workflow creation
   - Template application
   - Trigger detection
   - Action execution
   - Workflow activation/deactivation

## Test Best Practices

### Backend Tests

1. **Use setUp and tearDown**
   - Clean database state between tests
   - Create necessary fixtures

2. **Test both success and failure paths**
   - Valid inputs
   - Invalid inputs
   - Edge cases

3. **Use APITestCase for API tests**
   - Provides APIClient
   - Handles authentication
   - Tests complete request/response cycle

4. **Mock external services**
   - Email sending
   - SMS sending
   - Payment processing
   - File uploads

### Frontend Tests

1. **Test user behavior, not implementation**
   - Test what users see and do
   - Avoid testing internal state directly

2. **Use semantic queries**
   - getByRole, getByLabelText
   - Avoid getByTestId when possible

3. **Test accessibility**
   - Ensure components are accessible
   - Use proper ARIA attributes

4. **Mock API calls**
   - Mock axios/fetch
   - Test loading states
   - Test error states

### Integration Tests

1. **Test complete user journeys**
   - Multi-step flows
   - Cross-feature interactions

2. **Use realistic data**
   - Real-world scenarios
   - Edge cases

3. **Test permissions and authorization**
   - Authenticated vs unauthenticated
   - Different user roles

4. **Verify side effects**
   - Email notifications
   - Database updates
   - State changes

## Continuous Integration

### GitHub Actions / GitLab CI

```yaml
# .github/workflows/test.yml (example)
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python manage.py test
      - name: Coverage
        run: |
          pip install coverage
          coverage run --source='.' manage.py test
          coverage report

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: 18
      - name: Install dependencies
        run: cd trainer-app && npm install
      - name: Run tests
        run: cd trainer-app && npm test
```

## Writing New Tests

### Backend Test Template

```python
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

class MyModelTest(TestCase):
    """Tests for MyModel"""
    
    def setUp(self):
        # Create test data
        pass
    
    def test_create_instance(self):
        """Test creating an instance"""
        # Test logic
        self.assertEqual(expected, actual)

class MyAPITest(APITestCase):
    """Tests for My API endpoints"""
    
    def setUp(self):
        # Create test data and authenticate
        self.client.force_authenticate(user=self.user)
    
    def test_list_endpoint(self):
        """Test listing resources"""
        response = self.client.get('/api/endpoint/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

### Frontend Test Template

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';

describe('MyComponent', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  it('handles user interaction', async () => {
    render(<MyComponent />);
    const button = screen.getByRole('button');
    fireEvent.click(button);
    // Assert expected behavior
  });
});
```

## Troubleshooting

### Common Issues

1. **Database conflicts**
   - Use unique email/username in tests
   - Clean up in tearDown

2. **Async test failures**
   - Use `waitFor` for async operations
   - Properly mock promises

3. **Import errors**
   - Check test file structure
   - Verify module paths

4. **Test isolation issues**
   - Tests affecting each other
   - Ensure proper cleanup

### Debug Mode

```bash
# Backend - Print test output
python manage.py test --verbosity=2

# Backend - Keep test database
python manage.py test --keepdb

# Frontend - Run single test file
npm test -- path/to/test.test.tsx

# Frontend - Debug mode
npm test -- --inspect-brk
```

## Coverage Reports

### Backend Coverage

```bash
coverage run --source='.' manage.py test
coverage html
# Open htmlcov/index.html in browser
```

### Frontend Coverage

```bash
npm run test:coverage
# Coverage report displayed in terminal
# HTML report in coverage/ directory
```

## Performance Testing

For performance testing, consider:

1. **Load testing** - Use tools like Locust or JMeter
2. **Profile slow tests** - Identify bottlenecks
3. **Database query optimization** - Use Django Debug Toolbar
4. **Frontend performance** - Use Lighthouse, WebPageTest

## Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Vitest Documentation](https://vitest.dev/)
- [Testing Best Practices](https://testingjavascript.com/)

