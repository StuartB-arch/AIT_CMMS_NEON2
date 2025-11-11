"""
Example Integration Script
Demonstrates how to use the new modular features in the AIT CMMS system

This script shows practical examples of:
1. Using the PM Scheduler
2. Equipment Manager operations
3. Automated Backups
4. Equipment History
5. KPI Auto-Collection
6. KPI Trend Analysis
"""

from datetime import datetime, timedelta
from database_utils import db_pool

# Import new modules
from pm_scheduler import PMSchedulingService
from equipment_manager import EquipmentManager
from backup_manager import BackupManager
from equipment_history import EquipmentHistory
from kpi_auto_collector import KPIAutoCollector
from kpi_trend_analyzer import KPITrendAnalyzer


def example_pm_scheduler():
    """Example: Using the PM Scheduler"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: PM Scheduler")
    print("=" * 80)

    conn = db_pool.get_connection()
    try:
        # Initialize PM scheduler
        technicians = ['Tech1', 'Tech2', 'Tech3', 'Tech4']
        scheduler = PMSchedulingService(conn, technicians)

        # Generate schedule for next week
        next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        print(f"\nGenerating PM schedule for week of {next_monday.strftime('%Y-%m-%d')}")

        assignments = scheduler.generate_weekly_schedule(next_monday, max_pms=130)

        print(f"\nGenerated {len(assignments)} PM assignments")
        print("\nTop 10 Assignments:")
        print("-" * 80)

        for i, assignment in enumerate(assignments[:10], 1):
            print(f"{i}. {assignment.bfm_no} - {assignment.pm_type.value} PM")
            print(f"   Description: {assignment.description}")
            print(f"   Priority Score: {assignment.priority_score}")
            print(f"   Reason: {assignment.reason}")
            print()

    finally:
        db_pool.return_connection(conn)


def example_equipment_manager():
    """Example: Using the Equipment Manager"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Equipment Manager")
    print("=" * 80)

    conn = db_pool.get_connection()
    try:
        eq_manager = EquipmentManager(conn)

        # Get equipment statistics
        print("\nEquipment Statistics:")
        print("-" * 80)
        stats = eq_manager.get_equipment_statistics()
        print(f"Total Equipment: {stats['total']}")
        print(f"Active: {stats['active']}")
        print(f"Run to Failure: {stats['run_to_failure']}")
        print(f"Missing: {stats['missing']}")
        print(f"With Monthly PM: {stats['monthly_pm']}")
        print(f"With Annual PM: {stats['annual_pm']}")

        # Get equipment requiring attention
        print("\n\nEquipment Requiring Attention:")
        print("-" * 80)
        attention = eq_manager.get_equipment_requiring_attention()

        if attention['overdue_monthly']:
            print(f"\nOverdue Monthly PMs: {len(attention['overdue_monthly'])}")
            for eq in attention['overdue_monthly'][:5]:
                print(f"  - {eq['bfm_no']}: {eq['description']} ({eq['days_overdue']} days overdue)")

        if attention['overdue_annual']:
            print(f"\nOverdue Annual PMs: {len(attention['overdue_annual'])}")
            for eq in attention['overdue_annual'][:5]:
                print(f"  - {eq['bfm_no']}: {eq['description']} ({eq['days_overdue']} days overdue)")

        if attention['no_pm_history']:
            print(f"\nEquipment with No PM History: {len(attention['no_pm_history'])}")
            for eq in attention['no_pm_history'][:5]:
                print(f"  - {eq['bfm_no']}: {eq['description']}")

        # Search example
        print("\n\nSearch Example (searching for 'pump'):")
        print("-" * 80)
        results = eq_manager.search_equipment('pump')
        for eq in results[:5]:
            print(f"  - {eq['bfm_no']}: {eq['description']} (Status: {eq['status']})")

    finally:
        db_pool.return_connection(conn)


def example_backup_manager():
    """Example: Using the Backup Manager"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Backup Manager")
    print("=" * 80)

    # Database configuration (use your actual config)
    db_config = {
        'host': 'your-neon-host.neon.tech',
        'port': 5432,
        'database': 'neondb',
        'user': 'your-username',
        'password': 'your-password'
    }

    backup_mgr = BackupManager(db_config, backup_dir='./backups')

    # Configure backup settings
    print("\nConfiguring Backup Manager:")
    print("-" * 80)
    backup_mgr.update_config({
        'enabled': True,
        'schedule': 'daily',
        'backup_time': '02:00',
        'retention_days': 30,
        'max_backups': 50,
        'verify_after_backup': True
    })

    config = backup_mgr.get_config()
    print(f"Schedule: {config['schedule']}")
    print(f"Backup Time: {config['backup_time']}")
    print(f"Retention: {config['retention_days']} days")
    print(f"Max Backups: {config['max_backups']}")

    # Get backup status
    print("\n\nBackup Status:")
    print("-" * 80)
    status = backup_mgr.get_status()
    print(f"Enabled: {status['enabled']}")
    print(f"Automatic Running: {status['automatic_running']}")
    print(f"Total Backups: {status['total_backups']}")
    print(f"Total Size: {status['total_size_mb']:.2f} MB")
    if status['last_backup']:
        print(f"Last Backup: {status['last_backup']}")

    # List recent backups
    print("\n\nRecent Backups:")
    print("-" * 80)
    backups = backup_mgr.list_backups()
    for backup in backups[:5]:
        print(f"  - {backup['filename']}")
        print(f"    Size: {backup['size_mb']:.2f} MB")
        print(f"    Created: {backup['created']}")
        print(f"    Age: {backup['age_days']} days")
        print()

    # Create a manual backup (commented out to avoid actual backup)
    # print("\n\nCreating Manual Backup:")
    # print("-" * 80)
    # success, path, msg = backup_mgr.create_backup('example_manual_backup')
    # if success:
    #     print(f"Success: {msg}")
    #     print(f"Backup saved to: {path}")
    # else:
    #     print(f"Failed: {msg}")


def example_equipment_history():
    """Example: Using the Equipment History"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Equipment History")
    print("=" * 80)

    conn = db_pool.get_connection()
    try:
        history = EquipmentHistory(conn)

        # Get first active equipment (for demonstration)
        cursor = conn.cursor()
        cursor.execute("SELECT bfm_equipment_no FROM equipment WHERE status = 'Active' LIMIT 1")
        result = cursor.fetchone()

        if not result:
            print("No active equipment found for demonstration")
            return

        bfm_no = result[0]
        print(f"\nAnalyzing Equipment: {bfm_no}")
        print("-" * 80)

        # Get complete history for last 6 months
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        history_data = history.get_complete_history(bfm_no, start_date=start_date)

        print(f"\nHistory Summary (Last 6 Months):")
        print(f"  PM Completions: {len(history_data['pm_completions'])}")
        print(f"  Corrective Maintenance: {len(history_data['corrective_maintenance'])}")
        print(f"  Parts Used: {len(history_data['parts_used'])}")
        print(f"  Status Changes: {len(history_data['status_changes'])}")

        # Get timeline events
        print("\n\nRecent Timeline Events:")
        print("-" * 80)
        events = history.get_timeline_events(bfm_no, days=90)

        for event in events[:10]:
            print(f"{event['date']} - {event['category']}")
            print(f"  {event['title']}")
            print(f"  {event['details']}")
            print()

        # Get equipment health score
        print("\n\nEquipment Health Score:")
        print("-" * 80)
        health = history.get_equipment_health_score(bfm_no)

        print(f"Health Score: {health['health_score']}/100")
        print(f"Status: {health['status']}")
        print(f"PM Compliance: {health['pm_compliance']}%")
        print(f"CM Frequency: {health['cm_frequency']} per month")
        print(f"Labor Hours (12 months): {health['labor_hours']:.1f}")
        print(f"Parts Cost (12 months): ${health['parts_cost']:.2f}")

        if health['recommendations']:
            print("\nRecommendations:")
            for rec in health['recommendations']:
                print(f"  - {rec}")

    finally:
        db_pool.return_connection(conn)


def example_kpi_auto_collector():
    """Example: Using the KPI Auto Collector"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: KPI Auto Collector")
    print("=" * 80)

    conn = db_pool.get_connection()
    try:
        collector = KPIAutoCollector(conn)

        # Preview auto-collection for current month
        current_period = datetime.now().strftime('%Y-%m')
        print(f"\nPreviewing Auto-Collection for {current_period}")
        print("-" * 80)

        preview = collector.preview_auto_collection(current_period)

        if 'error' in preview:
            print(f"Error: {preview['error']}")
        else:
            print(f"\nAuto-Collectible KPIs:")
            for kpi in preview['kpis']:
                print(f"\n{kpi['name']}: {kpi['value']} {kpi['unit']}")
                if kpi['details']:
                    print(f"  Details:")
                    for key, value in kpi['details'].items():
                        if key not in ['auto_calculated', 'calculation_date', 'note']:
                            print(f"    {key}: {value}")

        # List auto-collectible KPIs
        print("\n\nAll Auto-Collectible KPIs:")
        print("-" * 80)
        kpi_list = collector.get_auto_collectable_kpis()
        for i, kpi_name in enumerate(kpi_list, 1):
            print(f"{i}. {kpi_name}")

        # Save auto-collected KPIs (commented out to avoid modifying database)
        # print(f"\n\nSaving Auto-Collected KPIs:")
        # print("-" * 80)
        # result = collector.save_auto_collected_kpis(current_period, user_id='system')
        # if result['success']:
        #     print(f"Successfully saved {result['saved_count']} KPIs")
        # else:
        #     print(f"Error: {result['error']}")

    finally:
        db_pool.return_connection(conn)


def example_kpi_trend_analyzer():
    """Example: Using the KPI Trend Analyzer"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: KPI Trend Analyzer")
    print("=" * 80)

    conn = db_pool.get_connection()
    try:
        analyzer = KPITrendAnalyzer(conn)

        # Analyze specific KPI
        print("\nAnalyzing PM Adherence Trend:")
        print("-" * 80)
        analysis = analyzer.analyze_trend('PM Adherence', months=6)

        if analysis['trend'] not in ['no_data', 'insufficient_data']:
            print(f"Trend: {analysis['trend'].upper()}")
            print(f"Latest Value: {analysis['latest_value']} {analysis['unit']}")
            print(f"Average Value: {analysis['average_value']} {analysis['unit']}")
            print(f"Min/Max: {analysis['min_value']}/{analysis['max_value']} {analysis['unit']}")
            print(f"Volatility: {analysis['volatility']} {analysis['unit']}")
            print(f"Data Points: {analysis['data_points']}")

            if analysis['target_value'] is not None:
                print(f"\nTarget: {analysis['target_value']} {analysis['unit']}")
                print(f"Meets Target: {'Yes' if analysis['meets_target'] else 'No'}")
                print(f"Gap: {analysis['target_gap']} {analysis['unit']}")
        else:
            print(f"Status: {analysis['message']}")

        # Generate alerts
        print("\n\nKPI Alerts:")
        print("-" * 80)
        alerts = analyzer.generate_alerts(months=3)

        if alerts:
            print(f"Found {len(alerts)} alerts:\n")
            for alert in alerts:
                print(f"[{alert['severity'].upper()}] {alert['kpi_name']}")
                print(f"  Type: {alert['alert_type']}")
                print(f"  Message: {alert['message']}")
                print()
        else:
            print("No alerts - all KPIs are performing well!")

        # Dashboard summary
        print("\n\nKPI Dashboard Summary:")
        print("-" * 80)
        summary = analyzer.get_kpi_dashboard_summary()

        print(f"Total KPIs: {summary['total_kpis']}")
        print(f"Meeting Target: {summary['meeting_target']}")
        print(f"Below Target: {summary['below_target']}")
        print(f"No Target Set: {summary['no_target']}")
        print(f"No Data: {summary['no_data']}")

        print(f"\nTrends:")
        print(f"  Improving: {summary['trending_up']}")
        print(f"  Declining: {summary['trending_down']}")
        print(f"  Stable: {summary['stable']}")

        # Export trend report (commented out to avoid creating file)
        # print("\n\nExporting Trend Report:")
        # print("-" * 80)
        # filename = analyzer.export_trend_report()
        # print(f"Report exported to: {filename}")

    finally:
        db_pool.return_connection(conn)


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print(" AIT CMMS - Modular Features Integration Examples")
    print("=" * 80)

    try:
        # Initialize database pool (use your actual config)
        db_config = {
            'host': 'your-neon-host.neon.tech',
            'port': 5432,
            'database': 'neondb',
            'user': 'your-username',
            'password': 'your-password',
            'sslmode': 'require'
        }

        db_pool.initialize(db_config, min_conn=2, max_conn=10)

        # Run examples
        example_pm_scheduler()
        example_equipment_manager()
        example_backup_manager()
        example_equipment_history()
        example_kpi_auto_collector()
        example_kpi_trend_analyzer()

        print("\n" + "=" * 80)
        print(" All examples completed successfully!")
        print("=" * 80)
        print("\nRefer to MODULAR_ARCHITECTURE_GUIDE.md for detailed documentation")
        print()

    except Exception as e:
        print(f"\nError running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # Note: Update the database configuration above before running
    print("\nIMPORTANT: Update the database configuration in this file before running!")
    print("Look for 'db_config' dictionary and update with your actual credentials.\n")

    # Uncomment to run:
    # main()
