# Developer Dashboard Integration Guide

## Overview

The Developer Dashboard is now integrated into the existing Flask API. It provides comprehensive testing, monitoring, and administration capabilities through a single unified web interface.

**Access Point**: `/api/developer/dashboard`

## Architecture

### Backend Components

#### New API Endpoints

1. **Test Execution** - `/api/developer/tests/run` (POST)
   - Executes the full pytest suite
   - Returns: test output, pass/fail counts, exit code
   - Stores results in `developer_test_runs` table

2. **Test Results History** - `/api/developer/tests/results` (GET)
   - Retrieves last 10 test run results
   - Shows: passed/failed/error counts, timestamps

3. **Performance Testing** - `/api/developer/performance/run` (POST)
   - Tests critical endpoints (health, auth, stats)
   - Measures response times in milliseconds
   - Returns detailed performance metrics

4. **System Monitoring** - `/api/developer/monitoring/status` (GET)
   - Database health and connection status
   - User statistics (total, patients, clinicians)
   - Recent activity (logins in last 24h, high-risk alerts)
   - API status and route count

5. **Test Data Generation** - `/api/developer/test-data/generate` (POST)
   - Creates realistic test patients and clinicians
   - Generates sample mood logs and messages
   - Configurable count of test users
   - Returns creation summary

6. **Backup Management** - `/api/developer/backups/list` (GET)
   - Lists available database backups
   - Shows backup filename, size, creation date
   - Reads from `backups/` directory

### New Database Tables

```sql
-- Stores test execution results
CREATE TABLE developer_test_runs (
    id SERIAL PRIMARY KEY,
    username TEXT,
    test_output TEXT,
    exit_code INTEGER,
    passed_count INTEGER,
    failed_count INTEGER,
    error_count INTEGER,
    created_at TIMESTAMP
);

-- Logs terminal command executions
CREATE TABLE dev_terminal_logs (
    id SERIAL PRIMARY KEY,
    username TEXT,
    command TEXT,
    output TEXT,
    exit_code INTEGER,
    duration_ms INTEGER,
    created_at TIMESTAMP
);

-- Stores AI assistant chat history
CREATE TABLE dev_ai_chats (
    id SERIAL PRIMARY KEY,
    username TEXT,
    session_id TEXT,
    role TEXT,
    message TEXT,
    created_at TIMESTAMP
);

-- Developer messaging system
CREATE TABLE dev_messages (
    id SERIAL PRIMARY KEY,
    from_username TEXT,
    to_username TEXT,
    message TEXT,
    message_type TEXT,
    read INTEGER,
    parent_message_id INTEGER,
    created_at TIMESTAMP
);
```

### Frontend Components

#### Dashboard Layout

The developer dashboard includes 6 main cards:

1. **Test Suite Card** 🧪
   - Run all tests button
   - View test results button
   - Real-time test output display
   - Recent test results history

2. **Performance Testing Card** ⚡
   - Run performance tests button
   - Response time metrics
   - Endpoint status indicators

3. **System Monitoring Card** 📊
   - Database status and health
   - User count breakdown
   - Activity metrics (logins, alerts)
   - API status and route count

4. **Test Data Generation Card** 📝
   - Input fields for number of test patients/clinicians
   - Generate test data button
   - Creation summary results

5. **Backups & Maintenance Card** 💾
   - List backups button
   - Backup file browser
   - Size and timestamp display

6. **Admin Tools Card** 🔧
   - Clear sessions button
   - Reset test data button
   - Advanced operations

## Usage

### 1. Access the Dashboard

```bash
# Start the Flask server
python3 api.py

# Navigate to:
# http://localhost:5000/api/developer/dashboard
```

### 2. Authenticate

- Enter developer username (default: `admin`)
- Enter developer password
- Enter 4-digit PIN
- Click "Authenticate"

Status will update to `✅ Authenticated as [username]`

### 3. Run Test Suite

```
1. Click "Run All Tests" button
2. Wait for execution (may take 2-3 minutes)
3. View detailed output in the output box
4. Check passed/failed/error counts
5. Click "View Results" to see history
```

**Output Example**:
```
test_auth.py::test_login PASSED
test_auth.py::test_register PASSED
test_cbt.py::test_mood_log PASSED
...
= 45 passed, 2 failed, 1 error in 120s =
```

### 4. Performance Testing

```
1. Click "Run Performance Tests" button
2. View response times for critical endpoints
3. Identify slow endpoints (>500ms is warning threshold)
4. Investigate and optimize as needed
```

### 5. Monitor System Health

```
1. Click "Refresh Status" button
2. Check database connection status
3. View user counts by role
4. Monitor 24h login activity
5. Check for active high-risk alerts
```

### 6. Generate Test Data

```
1. Enter number of test patients (e.g., 10)
2. Enter number of test clinicians (e.g., 3)
3. Click "Generate Test Data"
4. Wait for creation to complete
5. View summary: X patients, Y clinicians created
6. Test data is immediately available for testing
```

**Credentials for Generated Test Users**:
- Username: `patient_test_0_[timestamp]`
- Password: `TestPass123!@#`
- PIN: `1234`

### 7. View Backups

```
1. Click "List Backups" button
2. See all available backups
3. View file size and creation date
4. Check for recent backups
```

## Security Features

### Authentication
- Developer role required for all dashboard endpoints
- Session-based authentication (httponly cookies)
- PIN-based 2FA for enhanced security

### Authorization
- Only users with `role='developer'` can access endpoints
- Database queries check role on each request
- Role-based access control for all operations

### Audit Logging
- All test executions logged to database
- Command execution tracked with user and timestamp
- Terminal commands whitelist prevents shell injection
- All results stored for historical review

## Integration with Existing Features

### Compatible with Current Architecture
- ✅ Uses existing Flask session authentication
- ✅ Respects existing role-based access control
- ✅ Compatible with PostgreSQL database
- ✅ Integrates with existing logging system (`audit.py`)
- ✅ Uses existing get_db_connection() and cursor wrapper

### Existing Developer Endpoints Preserved
- `/api/developer/terminal/execute` - Terminal command execution
- `/api/developer/ai/chat` - AI assistant chat
- `/api/developer/stats` - Statistics endpoint
- `/api/developer/users/list` - User listing
- `/api/developer/users/delete` - User deletion

### Enhanced Components
- Existing diagnostic.html unchanged
- Existing admin-wipe.html unchanged
- New developer-dashboard.html added alongside existing templates

## Deployment Checklist

- [ ] API changes merged to main branch
- [ ] Database migration applied (new tables created)
- [ ] Test suite passing (`pytest -v tests/`)
- [ ] Developer user account created (with DEVELOPER_REGISTRATION_KEY)
- [ ] Dashboard accessible at `/api/developer/dashboard`
- [ ] Tests runnable from dashboard UI
- [ ] Performance tests showing response times
- [ ] System monitoring showing correct stats
- [ ] Test data generation working
- [ ] Backups list showing files
- [ ] Logging entries in database

## Example Workflows

### Workflow 1: Pre-Release Testing

```
1. Go to Developer Dashboard
2. Authenticate with dev credentials
3. Click "Run All Tests"
4. Wait for completion
5. Review test results
6. If all pass (✅), proceed to release
7. If failures, check output for details
```

### Workflow 2: Performance Investigation

```
1. Open Performance Testing card
2. Click "Run Performance Tests"
3. Identify slow endpoints
4. Compare response times with baseline
5. Profile code for bottlenecks
6. Implement optimizations
7. Re-run tests to verify improvement
```

### Workflow 3: Load Testing

```
1. Generate test data (100+ test users)
2. Monitor system status
3. Run performance tests
4. Check response times under load
5. Identify scaling issues
6. Optimize database queries/indexes
7. Verify improvements in next run
```

### Workflow 4: Database Maintenance

```
1. Check System Monitoring stats
2. List available backups
3. Verify backup freshness (daily recommended)
4. If backup old, create new one
5. Review database health indicators
6. Check for high-risk alert count
```

## Troubleshooting

### Tests Won't Run
- **Issue**: "pytest not installed"
- **Solution**: `pip install pytest` in venv
- **Verify**: `.venv/bin/python -m pytest --version`

### Performance Tests Fail
- **Issue**: "Connection refused"
- **Solution**: Flask server must be running on localhost:5000
- **Alternative**: Update hardcoded URLs in performance endpoint

### Test Data Generation Fails
- **Issue**: "Database error"
- **Solution**: Check PostgreSQL connection and credentials
- **Verify**: `getMonitoringStatus()` shows healthy database

### Dashboard Won't Load
- **Issue**: 404 Not Found
- **Solution**: Ensure `/api/developer/dashboard` route is registered
- **Verify**: Check api.py has the route definition

### Authentication Fails
- **Issue**: "Developer role required"
- **Solution**: User account must have `role='developer'`
- **Verify**: Check users table for developer account

## Future Enhancements

- [ ] Real-time WebSocket updates for test progress
- [ ] Test result visualization (charts/graphs)
- [ ] Performance trending (show improvements over time)
- [ ] Automated backup creation and retention
- [ ] Load test configuration UI
- [ ] Database query profiling tools
- [ ] Error rate alerts and notifications
- [ ] Integration with CI/CD pipeline
- [ ] Test coverage reports
- [ ] Code quality metrics integration

## References

- [Flask API Documentation](api.py)
- [Testing Guide](../tests/)
- [Database Schema](../schema_*.sql)
- [Deployment Guide](../DEPLOYMENT.md)
