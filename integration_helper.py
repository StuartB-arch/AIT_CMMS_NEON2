"""
Integration Helper for AIT CMMS Modular Features
This file shows exactly what to add to your AIT_CMMS_REV3.py to integrate the new features
"""

# ==============================================================================
# STEP 1: Add these imports at the top of AIT_CMMS_REV3.py (after existing imports)
# ==============================================================================

IMPORTS_TO_ADD = """
# New modular features
from equipment_manager import EquipmentManager
from backup_manager import BackupManager
from equipment_history import show_equipment_history, EquipmentHistory
from kpi_auto_collector import KPIAutoCollector
from kpi_trend_analyzer import show_kpi_trends, KPITrendAnalyzer
"""

# ==============================================================================
# STEP 2: Add these to the __init__ method of your main class
# ==============================================================================

INIT_CODE_TO_ADD = """
    # Initialize new modules (add this in __init__ after self.conn is established)
    try:
        self.equipment_manager = EquipmentManager(self.conn)
        self.kpi_collector = KPIAutoCollector(self.conn)
        self.kpi_trend_analyzer = KPITrendAnalyzer(self.conn)
        print("New modules initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize new modules: {e}")
"""

# ==============================================================================
# STEP 3: Add these menu items to your existing menu system
# ==============================================================================

MENU_ITEMS_TO_ADD = """
# Find where you create your menus (usually in setup_menus() or __init__)
# Add these items to appropriate menus:

# ============ Add to KPI Menu ============
# Find the KPI menu creation (might be called kpi_menu or similar)
# Add these commands:

kpi_menu.add_separator()
kpi_menu.add_command(
    label="Auto-Collect KPIs",
    command=self.auto_collect_kpis_dialog,
    font=('Arial', 10)
)
kpi_menu.add_command(
    label="KPI Trends & Alerts",
    command=self.show_kpi_trends_dialog,
    font=('Arial', 10)
)

# ============ Add to Equipment/View Menu ============
# Find your equipment or view menu
# Add this command:

equipment_menu.add_separator()
equipment_menu.add_command(
    label="View Equipment History",
    command=self.show_equipment_history_dialog,
    font=('Arial', 10)
)

# ============ Add to Tools Menu (or create one if needed) ============
# If you have a Tools menu, add this. Otherwise create one:

tools_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Tools", menu=tools_menu, font=('Arial', 10))

tools_menu.add_command(
    label="Backup Manager",
    command=self.show_backup_manager_dialog,
    font=('Arial', 10)
)
tools_menu.add_command(
    label="Equipment Manager",
    command=self.show_equipment_manager_dialog,
    font=('Arial', 10)
)
"""

# ==============================================================================
# STEP 4: Add these callback methods to your main class
# ==============================================================================

CALLBACK_METHODS_TO_ADD = """
    def auto_collect_kpis_dialog(self):
        \"\"\"Auto-collect KPIs for selected period\"\"\"
        try:
            # Create dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Auto-Collect KPIs")
            dialog.geometry("500x400")
            dialog.transient(self.root)
            dialog.grab_set()

            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (250)
            y = (dialog.winfo_screenheight() // 2) - (200)
            dialog.geometry(f"500x400+{x}+{y}")

            # Header
            header = ttk.Label(dialog, text="Auto-Collect KPIs from Database",
                              font=('Arial', 14, 'bold'))
            header.pack(pady=20)

            # Info
            info = ttk.Label(dialog, text="Automatically calculate KPIs from existing maintenance data.\\n"
                           "This eliminates manual data entry and improves accuracy.",
                           justify='center')
            info.pack(pady=10)

            # Period selection
            period_frame = ttk.LabelFrame(dialog, text="Select Period", padding=10)
            period_frame.pack(pady=20, padx=20, fill='x')

            ttk.Label(period_frame, text="Month:").grid(row=0, column=0, padx=5, pady=5, sticky='e')

            # Generate last 12 months
            from datetime import datetime, timedelta
            months = []
            for i in range(12):
                date = datetime.now() - timedelta(days=30*i)
                months.append(date.strftime('%Y-%m'))

            period_var = tk.StringVar(value=months[0])
            period_combo = ttk.Combobox(period_frame, textvariable=period_var,
                                       values=months, width=15, state='readonly')
            period_combo.grid(row=0, column=1, padx=5, pady=5)

            # Preview button
            preview_text = tk.Text(dialog, height=8, width=60, wrap='word')
            preview_text.pack(pady=10, padx=20)

            def preview():
                try:
                    preview_text.delete('1.0', 'end')
                    preview_text.insert('1.0', f"Previewing KPIs for {period_var.get()}...\\n\\n")
                    dialog.update()

                    result = self.kpi_collector.preview_auto_collection(period_var.get())

                    if 'error' in result:
                        preview_text.insert('end', f"Error: {result['error']}")
                    else:
                        preview_text.insert('end', f"Found {len(result['kpis'])} auto-collectible KPIs:\\n\\n")
                        for kpi in result['kpis']:
                            preview_text.insert('end', f"{kpi['name']}: {kpi['value']} {kpi['unit']}\\n")
                except Exception as e:
                    preview_text.delete('1.0', 'end')
                    preview_text.insert('1.0', f"Error: {str(e)}")

            # Buttons
            button_frame = ttk.Frame(dialog)
            button_frame.pack(pady=20)

            ttk.Button(button_frame, text="Preview",
                      command=preview).pack(side='left', padx=5)

            def save():
                if messagebox.askyesno("Confirm",
                    f"Auto-collect and save KPIs for {period_var.get()}?\\n\\n"
                    "This will update the KPI database."):
                    try:
                        result = self.kpi_collector.save_auto_collected_kpis(
                            period_var.get(),
                            user_id=self.current_user
                        )

                        if result['success']:
                            messagebox.showinfo("Success",
                                f"Successfully auto-collected {result['saved_count']} KPIs!\\n\\n"
                                f"Period: {result['period']}")
                            dialog.destroy()
                        else:
                            messagebox.showerror("Error", f"Error: {result.get('error', 'Unknown error')}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Error saving KPIs: {str(e)}")

            ttk.Button(button_frame, text="Save to Database",
                      command=save, style='Accent.TButton').pack(side='left', padx=5)

            ttk.Button(button_frame, text="Close",
                      command=dialog.destroy).pack(side='left', padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"Error opening KPI collector: {str(e)}")

    def show_kpi_trends_dialog(self):
        \"\"\"Show KPI trends and alerts window\"\"\"
        try:
            show_kpi_trends(self.root, self.conn)
        except Exception as e:
            messagebox.showerror("Error", f"Error opening KPI trends: {str(e)}")

    def show_equipment_history_dialog(self):
        \"\"\"Show equipment history for selected equipment\"\"\"
        try:
            # You need to get the selected equipment BFM number
            # This depends on how your UI is structured
            # Example: if you have a treeview with equipment:

            # Try to find selected equipment from various possible sources
            bfm_no = None

            # Option 1: If you have an equipment treeview
            if hasattr(self, 'equipment_tree'):
                selected = self.equipment_tree.selection()
                if selected:
                    bfm_no = self.equipment_tree.item(selected[0])['values'][0]

            # Option 2: If you have a selected_equipment attribute
            if not bfm_no and hasattr(self, 'selected_equipment'):
                bfm_no = self.selected_equipment

            # Option 3: Ask user to enter BFM number
            if not bfm_no:
                from tkinter import simpledialog
                bfm_no = simpledialog.askstring(
                    "Equipment History",
                    "Enter Equipment BFM Number:",
                    parent=self.root
                )

            if bfm_no:
                show_equipment_history(self.root, self.conn, str(bfm_no))
            else:
                messagebox.showinfo("No Selection",
                    "Please select an equipment or enter a BFM number")

        except Exception as e:
            messagebox.showerror("Error", f"Error opening equipment history: {str(e)}")

    def show_backup_manager_dialog(self):
        \"\"\"Show backup manager dialog\"\"\"
        try:
            # Create dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Backup Manager")
            dialog.geometry("800x600")
            dialog.transient(self.root)

            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (400)
            y = (dialog.winfo_screenheight() // 2) - (300)
            dialog.geometry(f"800x600+{x}+{y}")

            # Header
            header = ttk.Label(dialog, text="Database Backup Manager",
                              font=('Arial', 14, 'bold'))
            header.pack(pady=20)

            # Info text
            info_text = tk.Text(dialog, height=20, width=90, wrap='word')
            info_text.pack(pady=10, padx=20, fill='both', expand=True)

            info_text.insert('1.0',
                "DATABASE BACKUP MANAGER\\n"
                "=" * 80 + "\\n\\n"
                "The backup manager provides automated database backups with:\\n"
                "  - Scheduled backups (daily/weekly/monthly)\\n"
                "  - Automatic retention and cleanup\\n"
                "  - Backup verification\\n"
                "  - Easy restore capabilities\\n\\n"
                "To set up automated backups:\\n"
                "  1. Configure backup schedule and retention policy\\n"
                "  2. Start automatic backup service\\n"
                "  3. Backups will run in background\\n\\n"
                "Note: This feature requires PostgreSQL command-line tools\\n"
                "(pg_dump and pg_restore) to be installed and accessible.\\n\\n"
                "Manual backups can be created anytime using the button below.\\n\\n"
                "For full configuration, see backup_manager.py module."
            )
            info_text.config(state='disabled')

            # Buttons
            button_frame = ttk.Frame(dialog)
            button_frame.pack(pady=20)

            def create_manual_backup():
                if messagebox.askyesno("Create Backup",
                    "Create a manual database backup now?\\n\\n"
                    "This may take a few minutes."):
                    try:
                        # Show progress
                        progress = tk.Toplevel(dialog)
                        progress.title("Creating Backup...")
                        progress.geometry("400x100")
                        ttk.Label(progress, text="Creating database backup...\\nPlease wait.",
                                 font=('Arial', 10)).pack(pady=20)
                        progress.transient(dialog)
                        progress.update()

                        # This is a placeholder - actual backup requires db_config
                        messagebox.showinfo("Backup Manager",
                            "To use automated backups, initialize BackupManager in your application:\\n\\n"
                            "from backup_manager import BackupManager\\n"
                            "backup_mgr = BackupManager(db_config, './backups')\\n"
                            "backup_mgr.create_backup()\\n\\n"
                            "See MODULAR_ARCHITECTURE_GUIDE.md for details.")

                        progress.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"Error creating backup: {str(e)}")

            ttk.Button(button_frame, text="Create Manual Backup",
                      command=create_manual_backup,
                      style='Accent.TButton').pack(side='left', padx=5)

            ttk.Button(button_frame, text="Close",
                      command=dialog.destroy).pack(side='left', padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"Error opening backup manager: {str(e)}")

    def show_equipment_manager_dialog(self):
        \"\"\"Show equipment manager statistics\"\"\"
        try:
            # Create dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Equipment Manager")
            dialog.geometry("700x500")
            dialog.transient(self.root)

            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (350)
            y = (dialog.winfo_screenheight() // 2) - (250)
            dialog.geometry(f"700x500+{x}+{y}")

            # Header
            header = ttk.Label(dialog, text="Equipment Manager",
                              font=('Arial', 14, 'bold'))
            header.pack(pady=20)

            # Statistics
            stats_text = tk.Text(dialog, height=25, width=80, wrap='word', font=('Courier', 10))
            stats_text.pack(pady=10, padx=20, fill='both', expand=True)

            # Load statistics
            stats = self.equipment_manager.get_equipment_statistics()
            attention = self.equipment_manager.get_equipment_requiring_attention()

            report = f\"\"\"
EQUIPMENT STATISTICS
{'=' * 70}

OVERALL COUNTS:
  Total Equipment: {stats['total']}
  Active: {stats['active']}
  Run to Failure: {stats['run_to_failure']}
  Missing: {stats['missing']}

PM CONFIGURATION:
  With Monthly PM: {stats['monthly_pm']}
  With Annual PM: {stats['annual_pm']}

{'=' * 70}
EQUIPMENT REQUIRING ATTENTION
{'=' * 70}

OVERDUE MONTHLY PMs: {len(attention['overdue_monthly'])}
\"\"\"

            for eq in attention['overdue_monthly'][:10]:
                report += f"  - {eq['bfm_no']}: {eq['description'][:40]} ({eq['days_overdue']} days overdue)\\n"

            report += f"\\nOVERDUE ANNUAL PMs: {len(attention['overdue_annual'])}\\n"

            for eq in attention['overdue_annual'][:10]:
                report += f"  - {eq['bfm_no']}: {eq['description'][:40]} ({eq['days_overdue']} days overdue)\\n"

            report += f"\\nMISSING EQUIPMENT: {len(attention['missing'])}\\n"

            for eq in attention['missing'][:10]:
                report += f"  - {eq['bfm_no']}: {eq['description'][:40]}\\n"

            report += f"\\nNO PM HISTORY: {len(attention['no_pm_history'])}\\n"

            for eq in attention['no_pm_history'][:10]:
                report += f"  - {eq['bfm_no']}: {eq['description'][:40]}\\n"

            stats_text.insert('1.0', report)
            stats_text.config(state='disabled')

            # Button
            ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Error opening equipment manager: {str(e)}")
"""

# ==============================================================================
# INSTRUCTIONS
# ==============================================================================

print("""
================================================================================
AIT CMMS - INTEGRATION INSTRUCTIONS
================================================================================

To see the new features in your application, follow these steps:

STEP 1: Add Imports
--------------------
""" + IMPORTS_TO_ADD + """

STEP 2: Initialize Modules in __init__
---------------------------------------
Find your __init__ method (where you set up self.conn and other variables)
Add after self.conn is established:
""" + INIT_CODE_TO_ADD + """

STEP 3: Add Menu Items
----------------------
Find where you create your menus (look for tk.Menu or menubar)
""" + MENU_ITEMS_TO_ADD + """

STEP 4: Add Callback Methods
----------------------------
Add these methods to your main class (same level as other methods):
""" + CALLBACK_METHODS_TO_ADD + """

================================================================================
After adding these, restart your application and you should see:
  - "Auto-Collect KPIs" and "KPI Trends & Alerts" in your KPI menu
  - "View Equipment History" in your equipment/view menu
  - "Backup Manager" and "Equipment Manager" in your Tools menu

These will open the new modular features!
================================================================================
""")
