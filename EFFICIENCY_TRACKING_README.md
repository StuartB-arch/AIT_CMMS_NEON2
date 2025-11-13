# Efficiency Tracking Module - User Guide

## Overview

The **Efficiency Tracking** module is a comprehensive labor and productivity reporting system for the AIT CMMS. It provides detailed insights into technician performance, work hours distribution, and efficiency metrics against established targets.

## Key Features

### 1. Comprehensive Efficiency Metrics
- **Individual Technician Performance**: Track each technician's PM and CM hours
- **Efficiency Calculations**: Automatically calculate efficiency rates based on available hours
- **Target Comparison**: Compare actual performance against 80% efficiency target
- **Status Indicators**: Visual color-coding for above/at/below target performance

### 2. Interactive Visualizations
Four chart types provide different perspectives on efficiency data:

- **Efficiency Comparison Chart**: Bar chart showing each technician's efficiency percentage
- **Hours Breakdown Chart**: Stacked bars displaying PM vs CM hours per technician
- **Workload Distribution**: Pie charts showing hours and task distribution across the team
- **Efficiency vs Target Analysis**: Line chart comparing actual efficiency to target

### 3. Flexible Date Range Selection
- Quick select buttons: Last 7/30/90 Days, This Month, Last Month, Year to Date
- Custom date range input for any period
- Automatic recalculation when date range changes

### 4. Multiple Export Options
- **Excel Export**: Detailed spreadsheet with summary and technician data
- **PDF Export**: Professional formatted report ready for printing
- **Print Function**: Direct printing with formatting guidance

## System Parameters

The module is configured with the following operational parameters:

```
Annual Hours per Technician: 1,980 hours
Total Technicians: 9
Weekly Team Availability: 342.69 hours
Target Efficiency: 80%
```

## Efficiency Calculation Methodology

### Available Hours Calculation
```
Hours per Technician per Day = 342.69 / 9 / 5 = 7.616 hours/day
Available Hours for Period = 7.616 × Number of Working Days
```

### Efficiency Formula
```
Efficiency % = (Total Worked Hours / Total Available Hours) × 100
```

Where:
- **Total Worked Hours** = PM Hours + CM Hours (from completed work orders)
- **PM Hours** = Sum of labor_hours + (labor_minutes/60) from pm_completions table
- **CM Hours** = Sum of labor_hours from closed corrective_maintenance records

### Status Thresholds
- **Above Target** (Green): Efficiency ≥ 85%
- **At Target** (Yellow): Efficiency 75-84%
- **Below Target** (Red): Efficiency < 75%

## Data Sources

The module pulls accurate, real-time data from:

1. **pm_completions table**
   - Technician name
   - Completion date
   - Labor hours and minutes

2. **corrective_maintenance table**
   - Assigned technician
   - Status (Closed)
   - Labor hours
   - Closed date

3. **users table**
   - Active technician list
   - Full names

## How to Use

### Accessing the Efficiency Tab
1. Log in as a **Manager** (efficiency tracking is manager-only)
2. Navigate to the **⚡ Efficiency** tab in the main application
3. The report auto-generates on tab open with Last 30 Days data

### Generating Reports
1. **Select Date Range**:
   - Use quick select buttons for common periods
   - OR enter custom start/end dates in YYYY-MM-DD format

2. **Click "🔄 Generate Report"**:
   - Calculates all metrics
   - Updates summary statistics
   - Refreshes technician detail table
   - Regenerates all charts

3. **Review Results**:
   - Check overall efficiency summary at top
   - Review individual technician performance in table
   - Explore visualizations in chart tabs

### Exporting Reports

#### Excel Export
1. Click **"💾 Export to Excel"** button
2. Choose save location and filename
3. Opens spreadsheet with:
   - Report title and date range
   - Overall summary section
   - Detailed technician performance table
   - Auto-sized columns for readability

**Requirements**: `openpyxl` library (included in requirements.txt)

#### PDF Export
1. Click **"📄 Export to PDF"** button
2. Choose save location and filename
3. Generates professional PDF with:
   - Formatted title and headers
   - Summary metrics table
   - Detailed technician performance table
   - Report methodology notes
   - Color-coded formatting

**Requirements**: `reportlab` library (included in requirements.txt)

#### Printing
1. Click **"🖨️ Print Report"** button
2. Follow instructions to:
   - Export to PDF first
   - Open PDF in viewer
   - Print with your system's print dialog

## Interpreting the Data

### Summary Metrics
- **Total Available Hours**: Theoretical maximum hours for all technicians in period
- **Total Worked Hours**: Actual documented PM + CM hours
- **Overall Efficiency**: Team-wide efficiency percentage
- **PM Hours**: Total preventive maintenance hours
- **CM Hours**: Total corrective maintenance hours

### Technician Detail Table
Each row shows:
- **Technician Name**: Full name from user account
- **Available Hrs**: Calculated available hours for this tech in period
- **PM Hours**: Total preventive maintenance time
- **CM Hours**: Total corrective maintenance time
- **Total Hours**: Sum of PM and CM hours
- **PM Count**: Number of PMs completed
- **CM Count**: Number of CMs closed
- **Efficiency %**: Percentage of available hours utilized
- **vs Target**: Difference from 80% target (+/- format)
- **Status**: Above/At/Below Target indicator

### Understanding Low Efficiency
Low efficiency could indicate:
- Insufficient work scheduled
- Unrecorded labor hours
- Technician on leave/training
- Equipment waiting for parts
- Administrative duties not captured

### Understanding High Efficiency
High efficiency (>100%) could indicate:
- Overtime hours
- Highly productive technician
- Underestimated available hours
- Efficient work practices

## Best Practices

1. **Regular Review**: Generate efficiency reports weekly or monthly
2. **Consistent Data Entry**: Ensure technicians record hours accurately in PM/CM records
3. **Investigate Trends**: Look for patterns in efficiency changes over time
4. **Fair Comparison**: Consider workload type, complexity when comparing technicians
5. **Action Plans**: Use data to identify training needs or workload imbalances
6. **Document Insights**: Export reports to track improvements over time

## Troubleshooting

### No Data Displayed
- **Check date range**: Ensure dates are within periods with completed work
- **Verify technician names**: Must match exactly with user accounts
- **Confirm labor hours**: PMs and CMs must have hours recorded

### Charts Not Showing
- **Install matplotlib**: Run `pip install matplotlib>=3.5.0`
- **Restart application**: Close and reopen CMMS after installing

### Export Failures
- **Excel**: Install openpyxl with `pip install openpyxl>=3.0.9`
- **PDF**: Install reportlab with `pip install reportlab>=3.6.8`
- **Check permissions**: Ensure write access to save location

### Efficiency Seems Wrong
- **Review calculation**: Check formula in Report Notes section
- **Verify available hours**: Confirm working days calculation
- **Check data completeness**: Ensure all labor hours recorded in database
- **Consider timeframe**: Short periods may show skewed results

## Technical Notes

### Database Queries
The module executes read-only queries against:
- `pm_completions` table (completion_date range filter)
- `corrective_maintenance` table (closed_date range filter, status = 'Closed')
- `users` table (is_active = TRUE, role = 'Technician')

### Performance
- Queries optimized with date range filters
- Uses database connection pool for efficiency
- Chart generation uses matplotlib with Agg backend (non-blocking)
- Typical report generation: < 2 seconds for 90-day period

### Dependencies
```
matplotlib>=3.5.0  # Charts and visualizations
openpyxl>=3.0.9    # Excel export
reportlab>=3.6.8   # PDF export
tkinter            # GUI (included with Python)
```

## Future Enhancements

Potential additions for future versions:
- Trend analysis over multiple periods
- Efficiency forecasting
- Automated weekly email reports
- Integration with scheduling to show planned vs actual
- Equipment-specific efficiency tracking
- Cost analysis (labor hours × labor rates)

## Support

For questions, issues, or feature requests:
1. Check database connectivity
2. Verify all dependencies installed
3. Review application logs for errors
4. Contact system administrator

## Version History

**Version 1.0** (2025-11-13)
- Initial release
- Basic efficiency tracking and reporting
- Four visualization types
- Excel and PDF export
- Configurable date ranges
- Integration with existing CMMS data

---

**Module**: `efficiency_manager.py`
**Author**: CMMS Development Team
**Last Updated**: 2025-11-13
