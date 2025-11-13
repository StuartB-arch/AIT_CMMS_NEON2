"""
Responsive Design Utilities for AIT CMMS Application

This module provides utilities for making the Tkinter application
responsive across different screen sizes and resolutions.
"""

import tkinter as tk
from typing import Tuple, Dict, Optional


# Define responsive breakpoints (in pixels)
BREAKPOINTS = {
    'small': 1024,      # Small laptop screens
    'medium': 1366,     # Medium laptop screens
    'large': 1920,      # Large desktop screens
    'xlarge': 2560      # Extra large desktop screens
}


class ResponsiveManager:
    """Manages responsive sizing and scaling throughout the application"""

    def __init__(self, root_window):
        self.root = root_window
        self.current_width = root_window.winfo_screenwidth()
        self.current_height = root_window.winfo_screenheight()
        self.breakpoint = self._calculate_breakpoint(self.current_width)

    def _calculate_breakpoint(self, width: int) -> str:
        """Determine current breakpoint based on width"""
        if width < BREAKPOINTS['small']:
            return 'small'
        elif width < BREAKPOINTS['medium']:
            return 'medium'
        elif width < BREAKPOINTS['large']:
            return 'large'
        else:
            return 'xlarge'

    def update_dimensions(self, width: int, height: int):
        """Update current dimensions and recalculate breakpoint"""
        self.current_width = width
        self.current_height = height
        self.breakpoint = self._calculate_breakpoint(width)

    def get_chart_size(self, container_width: Optional[int] = None,
                      container_height: Optional[int] = None,
                      aspect_ratio: float = 1.78) -> Tuple[float, float]:
        """
        Calculate appropriate chart size based on container dimensions

        Args:
            container_width: Width of container in pixels (optional)
            container_height: Height of container in pixels (optional)
            aspect_ratio: Width to height ratio (default 16:9 = 1.78)

        Returns:
            Tuple of (width_inches, height_inches) for matplotlib figsize
        """
        dpi = 100

        # Use container dimensions or fall back to window dimensions
        width = container_width or self.current_width
        height = container_height or self.current_height

        # Calculate based on breakpoint
        if self.breakpoint == 'small':
            # Smaller charts for small screens
            width_ratio = 0.40
            height_ratio = 0.30
        elif self.breakpoint == 'medium':
            width_ratio = 0.45
            height_ratio = 0.35
        elif self.breakpoint == 'large':
            width_ratio = 0.45
            height_ratio = 0.35
        else:  # xlarge
            width_ratio = 0.40
            height_ratio = 0.35

        width_inches = (width * width_ratio) / dpi
        height_inches = (height * height_ratio) / dpi

        # Ensure minimum size
        width_inches = max(4.0, width_inches)
        height_inches = max(3.0, height_inches)

        # Ensure maximum size
        width_inches = min(10.0, width_inches)
        height_inches = min(7.0, height_inches)

        return (width_inches, height_inches)

    def get_compact_chart_size(self, container_width: Optional[int] = None,
                              container_height: Optional[int] = None) -> Tuple[float, float]:
        """
        Get a more compact chart size for pages with multiple charts

        Returns:
            Tuple of (width_inches, height_inches) for matplotlib figsize
        """
        base_size = self.get_chart_size(container_width, container_height)
        # Return 75% of base size for compact charts
        return (base_size[0] * 0.75, base_size[1] * 0.75)

    def get_dialog_size(self, width_ratio: float = 0.7,
                       height_ratio: float = 0.7) -> Tuple[int, int]:
        """
        Calculate responsive dialog window size

        Args:
            width_ratio: Percentage of screen width (0.0 to 1.0)
            height_ratio: Percentage of screen height (0.0 to 1.0)

        Returns:
            Tuple of (width_pixels, height_pixels)
        """
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        width = int(screen_width * width_ratio)
        height = int(screen_height * height_ratio)

        # Adjust based on breakpoint
        if self.breakpoint == 'small':
            # Use more screen space on small displays
            width = int(screen_width * min(width_ratio + 0.1, 0.95))
            height = int(screen_height * min(height_ratio + 0.1, 0.95))

        # Set minimums
        width = max(600, width)
        height = max(400, height)

        return (width, height)

    def get_column_widths(self, total_width: int,
                         column_weights: Dict[str, float]) -> Dict[str, int]:
        """
        Calculate responsive column widths for Treeview

        Args:
            total_width: Total available width in pixels
            column_weights: Dict mapping column names to weight ratios

        Returns:
            Dict mapping column names to pixel widths
        """
        # Reserve space for scrollbar and padding
        available_width = total_width - 20

        # Calculate total weight
        total_weight = sum(column_weights.values())

        # Calculate widths proportionally
        widths = {}
        for col, weight in column_weights.items():
            col_width = int((available_width * weight) / total_weight)
            # Set minimum column width
            widths[col] = max(50, col_width)

        return widths

    def get_font_size(self, base_size: int = 10) -> int:
        """
        Get responsive font size based on screen size

        Args:
            base_size: Base font size for medium screens

        Returns:
            Adjusted font size
        """
        if self.breakpoint == 'small':
            return max(8, base_size - 1)
        elif self.breakpoint == 'medium':
            return base_size
        elif self.breakpoint == 'large':
            return base_size + 1
        else:  # xlarge
            return base_size + 2

    def get_padding(self, base_padding: int = 5) -> int:
        """
        Get responsive padding based on screen size

        Args:
            base_padding: Base padding for medium screens

        Returns:
            Adjusted padding
        """
        if self.breakpoint == 'small':
            return max(2, base_padding - 2)
        elif self.breakpoint == 'medium':
            return base_padding
        else:  # large or xlarge
            return base_padding + 2


def calculate_chart_size_for_multi_chart_layout(screen_width: int,
                                               screen_height: int,
                                               num_charts: int = 4,
                                               dpi: int = 100) -> Tuple[float, float]:
    """
    Calculate chart size optimized for layouts with multiple charts inside a notebook tab

    Args:
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels
        num_charts: Number of charts to display
        dpi: DPI for matplotlib

    Returns:
        Tuple of (width_inches, height_inches)
    """
    # For 4 charts in a tabbed notebook with scrollable frame
    # We need much smaller sizes since they're in a constrained container
    if num_charts == 4:
        # Reduced from 40% to 25% for better fit in notebook tabs
        width_inches = (screen_width * 0.25) / dpi
        height_inches = (screen_height * 0.25) / dpi
    # For 2 charts side by side
    elif num_charts == 2:
        width_inches = (screen_width * 0.35) / dpi
        height_inches = (screen_height * 0.35) / dpi
    # Single chart
    else:
        width_inches = (screen_width * 0.50) / dpi
        height_inches = (screen_height * 0.45) / dpi

    # Apply constraints - smaller max sizes for notebook tabs
    width_inches = max(4.0, min(6.5, width_inches))
    height_inches = max(3.0, min(4.5, height_inches))

    return (width_inches, height_inches)


def center_window(window, width: int, height: int):
    """
    Center a window on the screen

    Args:
        window: Tkinter window/toplevel to center
        width: Window width
        height: Window height
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    window.geometry(f"{width}x{height}+{x}+{y}")


def make_treeview_responsive(tree, parent, column_weights: Dict[str, float]):
    """
    Make a Treeview widget responsive to parent width changes

    Args:
        tree: ttk.Treeview widget
        parent: Parent widget
        column_weights: Dict mapping column names to relative weights
    """
    def resize_columns(event=None):
        """Resize columns when parent widget size changes"""
        try:
            parent_width = parent.winfo_width()
            if parent_width > 1:  # Ensure parent has been rendered
                available_width = parent_width - 20  # Account for scrollbar
                total_weight = sum(column_weights.values())

                for col, weight in column_weights.items():
                    col_width = int((available_width * weight) / total_weight)
                    tree.column(col, width=max(50, col_width))
        except:
            pass

    # Bind to parent configure event
    parent.bind('<Configure>', resize_columns)

    # Do initial resize after a short delay
    parent.after(100, resize_columns)


def create_responsive_dialog(parent, title: str,
                            width_ratio: float = 0.7,
                            height_ratio: float = 0.7,
                            min_width: int = 600,
                            min_height: int = 400) -> tk.Toplevel:
    """
    Create a responsive dialog window

    Args:
        parent: Parent window
        title: Dialog title
        width_ratio: Percentage of screen width (0.0 to 1.0)
        height_ratio: Percentage of screen height (0.0 to 1.0)
        min_width: Minimum dialog width
        min_height: Minimum dialog height

    Returns:
        tk.Toplevel dialog window
    """
    dialog = tk.Toplevel(parent)
    dialog.title(title)

    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()

    width = int(screen_width * width_ratio)
    height = int(screen_height * height_ratio)

    # Apply minimum constraints
    width = max(min_width, width)
    height = max(min_height, height)

    # Apply maximum constraints (90% of screen)
    width = min(int(screen_width * 0.9), width)
    height = min(int(screen_height * 0.9), height)

    center_window(dialog, width, height)

    # Set minimum size and make resizable
    dialog.minsize(min_width, min_height)
    dialog.resizable(True, True)

    return dialog


def bind_resize_event(widget, callback):
    """
    Bind a callback to widget resize events with debouncing

    Args:
        widget: Widget to monitor
        callback: Function to call on resize (receives width, height)
    """
    resize_timer = None

    def on_configure(event):
        nonlocal resize_timer
        # Cancel previous timer
        if resize_timer is not None:
            widget.after_cancel(resize_timer)

        # Set new timer to call callback after 100ms of no resize events
        resize_timer = widget.after(100, lambda: callback(event.width, event.height))

    widget.bind('<Configure>', on_configure)
