# Sleep Chart & Custom Date Ranges Feature

## Overview
Added comprehensive sleep tracking visualization and custom date range filtering to both patient and clinician dashboards.

## Patient Features

### Insights Tab - Sleep Chart
- **Location**: Patient Dashboard → Insights Tab
- **Chart Type**: Line chart showing sleep hours over time
- **Scale**: 0-12 hours (vertical axis)
- **Color**: Blue (#3498db) to differentiate from mood chart
- **Data Source**: `sleep_val` from `mood_logs` table

### Date Range Selector
**Location**: Top of Insights tab

**Options**:
- **Quick Select Buttons**:
  - 7 Days
  - 30 Days
  - 90 Days
- **Custom Range**:
  - From Date picker
  - To Date picker

**Behavior**:
- Defaults to last 7 entries if no date range specified
- Clicking quick select buttons auto-fills date pickers and refreshes charts
- Both mood and sleep charts update together when range changes

### Chart Features
- **Empty State**: Shows "No sleep data available" when no data exists
- **Grid Lines**: Horizontal lines every hour (0h to 12h)
- **Data Points**: Blue circles on each data point
- **X-Axis Labels**: Date format MM/DD
- **Responsive**: Handles any number of data points (1 to thousands)

## Clinician Features

### Professional Dashboard - Patient Detail View
- **Location**: Professional Dashboard → Select Patient → Charts Section
- **Charts**: Both Mood Trend and Sleep Hours Trend displayed
- **Date Range Controls**: Same UI as patient insights

### Date Range Selector
**Location**: Above charts in patient detail section

**Options**: Identical to patient view
- 7 Days, 30 Days, 90 Days buttons
- Custom date range pickers
- "Refresh" button to reload charts

### Chart Integration
- **Initial Load**: Defaults to last 30 days when viewing patient
- **Real-time Updates**: Clicking date range buttons instantly refreshes both charts
- **Data Accuracy**: Uses same API endpoint as patient view for consistency

## API Updates

### Endpoint: `/api/insights`
**Method**: GET

**Parameters**:
- `username` (required): Patient username
- `from_date` (optional): Start date (YYYY-MM-DD format)
- `to_date` (optional): End date (YYYY-MM-DD format)

**Query Behavior**:
- If no dates specified: Returns last 7 entries
- If `from_date` only: Returns all entries from that date forward
- If `to_date` only: Returns all entries up to that date
- If both dates: Returns entries within the range

**Response Format**:
```json
{
  "insight": "Your average mood over 14 entries from 2026-01-11 to 2026-01-17 is 5.9/10...",
  "mood_data": [
    {"value": 5, "timestamp": "2026-01-11 18:26:48"},
    {"value": 6, "timestamp": "2026-01-12 18:26:48"}
  ],
  "sleep_data": [
    {"value": 7.0, "timestamp": "2026-01-11 18:26:48"},
    {"value": 8.0, "timestamp": "2026-01-12 18:26:48"}
  ],
  "avg_mood": 5.9,
  "avg_sleep": 7.4,
  "trend": "stable"
}
```

## JavaScript Functions

### Patient Functions

#### `setInsightsRange(days)`
Sets date range and triggers `loadInsights()`
```javascript
setInsightsRange(7)  // Last 7 days
setInsightsRange(30) // Last 30 days
setInsightsRange(90) // Last 90 days
```

#### `loadInsights()`
Fetches data from API and renders both charts
- Reads date range from input fields
- Calls API with optional from_date/to_date
- Updates stats (avg mood, avg sleep, trend)
- Calls `drawMoodChart()` and `drawSleepChart()`

#### `drawSleepChart(sleepData)`
Renders sleep chart on canvas
- Canvas ID: `sleepChart`
- Max scale: 12 hours
- Color: #3498db (blue)
- Handles empty data gracefully

### Clinician Functions

#### `setPatientChartRange(days)`
Sets date range for patient charts
```javascript
setPatientChartRange(7)  // Last 7 days
setPatientChartRange(30) // Last 30 days
setPatientChartRange(90) // Last 90 days
```

#### `loadPatientCharts()`
Fetches and renders charts for selected patient
- Uses `currentPatientData.username`
- Reads date range from clinician date pickers
- Calls API with patient username + date range
- Renders both mood and sleep charts

#### `drawPatientMoodChart(moods)`
Renders mood chart in professional dashboard
- Canvas ID: `moodChart`
- Scale: 0-10
- Color: #667eea (purple)

#### `drawPatientSleepChart(sleepData)`
Renders sleep chart in professional dashboard
- Canvas ID: `sleepChart`
- Scale: 0-12 hours
- Color: #3498db (blue)

## Database Integration

### Tables Used
- **mood_logs**: Contains both mood_val and sleep_val columns
  - `mood_val`: Integer 0-10
  - `sleep_val`: Float (hours)
  - `entrestamp`: Timestamp for filtering

### SQL Query Example
```sql
SELECT mood_val, sleep_val, entrestamp 
FROM mood_logs 
WHERE username=? 
  AND date(entrestamp) >= date(?) 
  AND date(entrestamp) <= date(?)
ORDER BY entrestamp DESC
```

## UI Layout

### Patient Insights Tab
```
┌─────────────────────────────────────────────┐
│ 📅 Date Range                               │
│ ┌─────────────┐ ┌─────────────┐            │
│ │ From Date   │ │ To Date     │            │
│ └─────────────┘ └─────────────┘            │
│ [7 Days] [30 Days] [90 Days]               │
├─────────────────────────────────────────────┤
│ [Generate Insights] [Export CSV] [Export PDF]│
├─────────────────────────────────────────────┤
│ 📊 Stats Dashboard                          │
│ Avg Mood: 5.9  |  Avg Sleep: 7.4h          │
├─────────────────────────────────────────────┤
│ 📊 Mood Trend                               │
│ [Line chart canvas]                         │
├─────────────────────────────────────────────┤
│ 😴 Sleep Hours Trend                        │
│ [Line chart canvas]                         │
└─────────────────────────────────────────────┘
```

### Clinician Patient Detail
```
┌─────────────────────────────────────────────┐
│ 📅 Chart Date Range                         │
│ ┌─────────────┐ ┌─────────────┐            │
│ │ From Date   │ │ To Date     │            │
│ └─────────────┘ └─────────────┘            │
│ [7 Days] [30 Days] [90 Days] [Refresh]     │
├─────────────────────────────────────────────┤
│ 📊 Mood Trend                               │
│ [Line chart canvas]                         │
├─────────────────────────────────────────────┤
│ 😴 Sleep Hours Trend                        │
│ [Line chart canvas]                         │
└─────────────────────────────────────────────┘
```

## Testing

### Test API Endpoint
```bash
# Test with date range
curl "http://localhost:5000/api/insights?username=testuser&from_date=2026-01-11&to_date=2026-01-17"

# Test without date range (last 7 entries)
curl "http://localhost:5000/api/insights?username=testuser"
```

### Expected Behavior
1. **Patient logs in** → Goes to Insights
2. **Clicks "7 Days"** → Date pickers auto-fill
3. **Clicks "Generate Insights"** → Both charts render
4. **Clinician selects patient** → Charts default to 30 days
5. **Clinician clicks "90 Days"** → Charts update to 90-day view

## Browser Compatibility
- **Canvas Support**: Required (all modern browsers)
- **Date Input**: HTML5 date pickers (fallback to text input on older browsers)
- **JavaScript**: ES6+ features used (async/await)

## Known Limitations
1. **Maximum data points**: Charts can handle unlimited points, but X-axis labels skip points for readability when >10 entries
2. **Date validation**: No frontend validation for invalid date ranges (e.g., from > to)
3. **Time zones**: All timestamps stored in database timezone, no timezone conversion

## Future Enhancements
- Add CSV export filtered by date range
- Add chart zoom/pan functionality
- Add chart type toggle (line vs bar)
- Add comparison view (current vs previous period)
- Add annotations for significant events
- Add sleep quality indicator (not just hours)

## Files Modified
- **api.py** (lines 2545-2610): Added date range parameters to insights endpoint
- **templates/index.html**:
  - Lines 1460-1510: Patient insights date range UI and sleep chart
  - Lines 1710-1750: Clinician charts date range UI and sleep chart
  - Lines 3440-3550: JavaScript functions for patient charts
  - Lines 3760-4050: JavaScript functions for clinician charts

## Commit
- **Hash**: 16b75a5
- **Date**: 2026-01-17
- **Message**: "Feature: Add sleep chart and custom date ranges to insights"
