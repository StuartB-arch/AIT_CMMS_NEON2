# AIT CMMS Modular Architecture Guide

## Overview

This document describes the new modular architecture implemented in the AIT CMMS system. The system has been refactored from a monolithic design into a modular structure for improved maintainability, testability, and scalability.

## New Modules

### 1. PM Scheduler Module (`pm_scheduler.py`)

**Purpose:** Handles all preventive maintenance scheduling logic

**Key Classes:**
- `PMType` - Enum for PM types (Monthly, Annual)
- `PMStatus` - Enum for PM statuses
- `Equipment` - Data class for equipment information
- `CompletionRecord` - Data class for PM completions
- `PMAssignment` - Data class for PM assignments
- `DateParser` - Handles flexible date parsing
- `CompletionRecordRepository` - Database access for PM records
- `PMEligibilityChecker` - Determines PM eligibility
- `PMAssignmentGenerator` - Generates PM assignments
- `PMSchedulingService` - Main orchestrator for PM scheduling

**Usage:**
```python
from pm_scheduler import PMSchedulingService

# Initialize
scheduler = PMSchedulingService(conn, technicians=['Tech1', 'Tech2'], root=tk_root)

# Generate weekly schedule
assignments = scheduler.generate_weekly_schedule(week_start, max_pms=130)
```

**Benefits:**
- Clean separation of scheduling logic
- Easy to test independently
- Reusable across different interfaces

---

### 2. Equipment Manager Module (`equipment_manager.py`)

**Purpose:** Manages equipment CRUD operations and queries

**Key Classes:**
- `EquipmentManager` - Main equipment management class

**Key Methods:**
- `get_equipment_by_bfm()` - Retrieve equipment by BFM number
- `search_equipment()` - Search equipment by term
- `get_all_equipment()` - Get all equipment with optional filters
- `update_equipment_status()` - Update equipment status
- `get_equipment_statistics()` - Get equipment statistics
- `get_equipment_requiring_attention()` - Get overdue/problem equipment
- `validate_bfm_number()` - Validate BFM number
- `add_equipment()` - Add new equipment
- `delete_equipment()` - Delete equipment

**Usage:**
```python
from equipment_manager import EquipmentManager

# Initialize
eq_manager = EquipmentManager(conn)

# Get equipment
equipment = eq_manager.get_equipment_by_bfm('A220-001')

# Get statistics
stats = eq_manager.get_equipment_statistics()
print(f"Active equipment: {stats['active']}")

# Get equipment needing attention
attention = eq_manager.get_equipment_requiring_attention()
```

**Benefits:**
- Centralized equipment operations
- Consistent error handling
- Audit trail logging

---

### 3. Backup Manager Module (`backup_manager.py`)

**Purpose:** Automated database backup system with scheduling

**Key Classes:**
- `BackupManager` - Main backup management class

**Key Features:**
- Automated scheduled backups (daily, weekly, monthly)
- Backup rotation and retention policies
- Backup verification
- Restore capabilities
- Compression support
- Detailed logging

**Key Methods:**
- `create_backup()` - Create a database backup
- `restore_backup()` - Restore from backup
- `cleanup_old_backups()` - Remove old backups per policy
- `list_backups()` - List all available backups
- `start_automatic_backups()` - Start background backup thread
- `stop_automatic_backups()` - Stop background backups
- `get_status()` - Get backup system status

**Usage:**
```python
from backup_manager import BackupManager

# Initialize
backup_mgr = BackupManager(db_config, backup_dir='./backups')

# Configure
backup_mgr.update_config({
    'enabled': True,
    'schedule': 'daily',
    'backup_time': '02:00',
    'retention_days': 30,
    'max_backups': 50
})

# Start automatic backups
backup_mgr.start_automatic_backups()

# Manual backup
success, path, msg = backup_mgr.create_backup('manual_backup')

# List backups
backups = backup_mgr.list_backups()
for backup in backups:
    print(f"{backup['filename']}: {backup['size_mb']:.2f} MB")

# Get status
status = backup_mgr.get_status()
print(f"Last backup: {status['last_backup']}")
```

**Configuration:**
- `enabled`: Enable/disable automatic backups
- `schedule`: 'daily', 'weekly', or 'monthly'
- `backup_time`: Time to run backup (HH:MM format)
- `retention_days`: Keep backups for N days
- `max_backups`: Maximum number of backups to keep
- `compress`: Enable compression (uses pg_dump -F c)
- `verify_after_backup`: Verify backup after creation

**Benefits:**
- Automated, hands-off backups
- Protection against data loss
- Easy restore process
- Configurable retention policies

---

### 4. Equipment History Module (`equipment_history.py`)

**Purpose:** Comprehensive equipment history tracking and timeline visualization

**Key Classes:**
- `EquipmentHistory` - History data management
- `EquipmentHistoryViewer` - GUI for viewing history

**Key Features:**
- Complete PM history
- Corrective maintenance history
- Parts usage tracking
- Status change tracking
- Timeline visualization
- Equipment health scoring
- Maintenance trend analysis

**Key Methods:**
- `get_complete_history()` - Get all history for equipment
- `get_timeline_events()` - Get timeline events for visualization
- `get_equipment_health_score()` - Calculate health score
- `get_maintenance_trends()` - Get maintenance trends over time

**Usage:**
```python
from equipment_history import EquipmentHistory, show_equipment_history

# Initialize
history = EquipmentHistory(conn)

# Get complete history
history_data = history.get_complete_history('A220-001', start_date='2024-01-01')
print(f"PM completions: {len(history_data['pm_completions'])}")
print(f"CMs: {len(history_data['corrective_maintenance'])}")

# Get health score
health = history.get_equipment_health_score('A220-001')
print(f"Health score: {health['health_score']}/100")
print(f"PM compliance: {health['pm_compliance']}%")

# Show GUI viewer
show_equipment_history(parent_window, conn, 'A220-001')
```

**Health Score Calculation:**
- Based on PM compliance (30% weight)
- CM frequency (20% weight)
- Equipment status (30% weight)
- Results in 0-100 score
- Includes recommendations

**Benefits:**
- Complete equipment lifecycle visibility
- Data-driven maintenance decisions
- Easy identification of problem equipment
- Trend analysis for predictive maintenance

---

### 5. KPI Auto Collector Module (`kpi_auto_collector.py`)

**Purpose:** Automatically collect and calculate KPI data from existing database records

**Key Classes:**
- `KPIAutoCollector` - Automatic KPI data collection

**Key Features:**
- Auto-calculates 8+ KPIs from existing data
- Reduces manual data entry
- Improves accuracy
- Saves to database automatically

**Auto-Collectible KPIs:**
1. PM Adherence - (Completed PMs / Scheduled PMs) * 100
2. Work Orders Opened - Count of CMs opened
3. Work Orders Closed - Count of CMs closed
4. Work Order Backlog - Open CMs at period end
5. Technical Availability - Uptime percentage
6. MTBF - Mean Time Between Failures
7. MTTR - Mean Time To Repair
8. Total Maintenance Labor Hours - Sum of PM + CM hours

**Key Methods:**
- `auto_collect_all_kpis()` - Collect all KPIs for a period
- `save_auto_collected_kpis()` - Collect and save to database
- `preview_auto_collection()` - Preview before saving
- `get_auto_collectable_kpis()` - List of auto-collectible KPIs

**Usage:**
```python
from kpi_auto_collector import KPIAutoCollector

# Initialize
collector = KPIAutoCollector(conn)

# Preview for current month
current_period = '2025-01'
preview = collector.preview_auto_collection(current_period)

for kpi in preview['kpis']:
    print(f"{kpi['name']}: {kpi['value']} {kpi['unit']}")

# Auto-collect and save
result = collector.save_auto_collected_kpis(current_period, user_id='admin')
print(f"Saved {result['saved_count']} KPIs")

# Run for last 6 months
from datetime import datetime, timedelta
for i in range(6):
    date = datetime.now() - timedelta(days=30*i)
    period = date.strftime('%Y-%m')
    collector.save_auto_collected_kpis(period, user_id='system')
```

**Benefits:**
- Eliminates manual KPI data entry
- Ensures data accuracy
- Historical KPI reconstruction
- Real-time KPI updates

---

### 6. KPI Trend Analyzer Module (`kpi_trend_analyzer.py`)

**Purpose:** Trend analysis, forecasting, and alerting for KPIs

**Key Classes:**
- `KPITrendAnalyzer` - Trend analysis and alerts
- `KPITrendViewer` - GUI for viewing trends

**Key Features:**
- Historical trend analysis (6-12 months)
- Target comparison
- Automatic alert generation
- Trend direction detection (improving/declining/stable)
- Volatility calculation
- Dashboard summary
- Export trend reports

**Key Methods:**
- `get_kpi_history()` - Get historical KPI data
- `analyze_trend()` - Analyze trend for a KPI
- `generate_alerts()` - Generate alerts for KPIs below target
- `get_kpi_dashboard_summary()` - Get dashboard summary
- `export_trend_report()` - Export trend analysis report

**Alert Types:**
1. **Below Target** - KPI is below target value
2. **Declining Trend** - KPI showing negative trend
3. **Increasing Trend** - For "lower is better" KPIs
4. **High Volatility** - Unstable KPI performance

**Alert Severity:**
- **High** - Critical issues requiring immediate attention
- **Medium** - Issues to monitor and address
- **Low** - Informational

**Usage:**
```python
from kpi_trend_analyzer import KPITrendAnalyzer, show_kpi_trends

# Initialize
analyzer = KPITrendAnalyzer(conn)

# Analyze specific KPI
analysis = analyzer.analyze_trend('PM Adherence', months=6)
print(f"Trend: {analysis['trend']}")
print(f"Latest: {analysis['latest_value']}%")
print(f"Meets target: {analysis['meets_target']}")

# Generate alerts
alerts = analyzer.generate_alerts(months=3)
for alert in alerts:
    print(f"[{alert['severity'].upper()}] {alert['message']}")

# Get dashboard summary
summary = analyzer.get_kpi_dashboard_summary()
print(f"Meeting target: {summary['meeting_target']}/{summary['total_kpis']}")

# Export report
filename = analyzer.export_trend_report()
print(f"Report saved to: {filename}")

# Show GUI viewer
show_kpi_trends(parent_window, conn)
```

**Target Configuration:**
```python
# Default targets (can be customized)
kpi_targets = {
    'PM Adherence': {'target': 90, 'direction': 'higher', 'unit': '%'},
    'Work Order Backlog': {'target': 20, 'direction': 'lower', 'unit': 'count'},
    'Technical Availability': {'target': 95, 'direction': 'higher', 'unit': '%'},
    'MTBF': {'target': 720, 'direction': 'higher', 'unit': 'hours'},
    'MTTR': {'target': 8, 'direction': 'lower', 'unit': 'hours'},
}
```

**Benefits:**
- Proactive issue identification
- Data-driven decision making
- Performance tracking over time
- Early warning system
- Executive reporting

---

## Integration with Main Application

### Adding to Existing Application

To integrate these modules into the main AIT_CMMS_REV3.py application:

1. **Import the modules:**
```python
from pm_scheduler import PMSchedulingService
from equipment_manager import EquipmentManager
from backup_manager import BackupManager
from equipment_history import show_equipment_history
from kpi_auto_collector import KPIAutoCollector
from kpi_trend_analyzer import show_kpi_trends
```

2. **Initialize in __init__ method:**
```python
def __init__(self, root):
    # ... existing code ...

    # Initialize new modules
    self.equipment_manager = EquipmentManager(self.conn)
    self.kpi_collector = KPIAutoCollector(self.conn)

    # Initialize backup manager
    self.backup_manager = BackupManager(db_config, backup_dir='./backups')
    self.backup_manager.start_automatic_backups()
```

3. **Add menu items:**
```python
# Add to View menu
view_menu.add_command(label="Equipment History",
                      command=self.show_equipment_history_dialog)

# Add to KPI menu
kpi_menu.add_command(label="Auto-Collect KPIs",
                     command=self.auto_collect_kpis)
kpi_menu.add_command(label="KPI Trends & Alerts",
                     command=self.show_kpi_trends)

# Add to Tools menu
tools_menu.add_command(label="Backup Manager",
                       command=self.show_backup_manager)
```

4. **Add callback methods:**
```python
def show_equipment_history_dialog(self):
    """Show equipment history viewer"""
    # Get selected equipment BFM
    selected = self.equipment_tree.selection()
    if not selected:
        messagebox.showinfo("Select Equipment", "Please select an equipment first")
        return

    bfm_no = self.equipment_tree.item(selected[0])['values'][0]
    show_equipment_history(self.root, self.conn, bfm_no)

def auto_collect_kpis(self):
    """Auto-collect KPIs for current month"""
    current_period = datetime.now().strftime('%Y-%m')

    if messagebox.askyesno("Auto-Collect KPIs",
                           f"Auto-collect KPIs for {current_period}?"):
        result = self.kpi_collector.save_auto_collected_kpis(
            current_period,
            user_id=self.current_user
        )

        if result['success']:
            messagebox.showinfo("Success",
                              f"Auto-collected {result['saved_count']} KPIs")
        else:
            messagebox.showerror("Error", result['error'])

def show_kpi_trends(self):
    """Show KPI trends and alerts"""
    show_kpi_trends(self.root, self.conn)

def show_backup_manager(self):
    """Show backup manager dialog"""
    # Create backup manager dialog
    dialog = tk.Toplevel(self.root)
    dialog.title("Backup Manager")
    dialog.geometry("800x600")

    # ... create backup manager UI ...
```

---

## Database Schema Requirements

### New Tables (if not already present)

The KPI auto-collector and trend analyzer require the existing KPI tables:
- `kpi_definitions`
- `kpi_manual_data`
- `kpi_results`

### Backup Storage

Backups are stored in the `./backups` directory by default. Configuration is stored in `backup_config.json`.

---

## Configuration Files

### backup_config.json
```json
{
  "enabled": true,
  "schedule": "daily",
  "backup_time": "02:00",
  "retention_days": 30,
  "max_backups": 50,
  "compress": true,
  "verify_after_backup": true
}
```

---

## Testing

### Unit Testing

Each module can be tested independently:

```python
# Test PM Scheduler
from pm_scheduler import PMSchedulingService
scheduler = PMSchedulingService(conn, ['Tech1', 'Tech2'])
assignments = scheduler.generate_weekly_schedule(datetime.now(), 130)
print(f"Generated {len(assignments)} assignments")

# Test Equipment Manager
from equipment_manager import EquipmentManager
eq_mgr = EquipmentManager(conn)
stats = eq_mgr.get_equipment_statistics()
print(f"Active equipment: {stats['active']}")

# Test KPI Auto Collector
from kpi_auto_collector import KPIAutoCollector
collector = KPIAutoCollector(conn)
preview = collector.preview_auto_collection('2025-01')
print(f"Preview: {len(preview['kpis'])} KPIs")

# Test Backup Manager
from backup_manager import BackupManager
backup_mgr = BackupManager(db_config)
success, path, msg = backup_mgr.create_backup('test_backup')
print(f"Backup: {success}, {msg}")
```

---

## Migration Guide

### Migrating from Monolithic to Modular

1. **Phase 1 - Add Modules (Non-Breaking)**
   - Add all new module files
   - Test modules independently
   - Keep existing code intact

2. **Phase 2 - Integrate Modules**
   - Add imports to main application
   - Add menu items and dialogs
   - Test new features alongside old

3. **Phase 3 - Refactor (Optional)**
   - Gradually replace old code with module calls
   - Remove duplicate code
   - Clean up imports

**Note:** The new modules are designed to work alongside existing code without breaking changes.

---

## Benefits of Modular Architecture

1. **Maintainability**
   - Easier to find and fix bugs
   - Smaller, focused files
   - Clear separation of concerns

2. **Testability**
   - Each module can be tested independently
   - Mock dependencies easily
   - Unit test coverage

3. **Reusability**
   - Modules can be reused in other projects
   - CLI tools can use same modules
   - API endpoints can use modules directly

4. **Scalability**
   - Easy to add new features
   - Parallel development possible
   - Performance optimization per module

5. **Documentation**
   - Each module is self-documenting
   - Clear interfaces and APIs
   - Examples in module docstrings

---

## Future Enhancements

Potential future modules:

1. **Report Generator Module** - Centralized reporting
2. **Notification Module** - Email/SMS notifications
3. **API Module** - REST API for integrations
4. **Mobile Interface Module** - Mobile-optimized UI
5. **Analytics Module** - Advanced analytics and ML
6. **Document Management Module** - Attachment handling
7. **Workflow Module** - Approval workflows

---

## Support

For questions or issues with the modular architecture:

1. Check module docstrings for detailed documentation
2. Review example usage in this guide
3. Test modules independently before integration
4. Check logs for detailed error messages

---

## Version History

- **v1.0** (2025-01-11) - Initial modular architecture
  - PM Scheduler module
  - Equipment Manager module
  - Backup Manager module
  - Equipment History module
  - KPI Auto Collector module
  - KPI Trend Analyzer module

---

## Conclusion

The new modular architecture provides a solid foundation for future development while maintaining backward compatibility with the existing system. Each module is designed to be independent, testable, and reusable, making the system more maintainable and scalable.
