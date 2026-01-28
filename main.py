import tkinter as tk
from tkinter import ttk
import sv_ttk
import os
from MenuTracker import MenuTracker
from Dashboard import Dashboard
from SalesLogger import SalesLogger
from InventoryManagement import InventoryManagement
from TrendsAnalysis import TrendsAnalysis


class DineSightApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DineSight")
        self.center_window(1200, 700)

        self.colors = {
            'background': '#ffffff',
            'surface': '#ffffff',
            'surface_hover': '#fafbfc',
            'surface_pressed': '#f4f6f8',
            'border': '#e1e5e9',
            'border_subtle': '#f0f3f6',
            'text_primary': '#1a1d21',
            'text_secondary': '#6b7280',
            'text_muted': '#9ca3af',
            'text_disabled': '#d1d5db',
            'accent': '#3b82f6',
            'accent_light': '#eff6ff',
            'accent_lighter': '#f8faff',
            'accent_hover': '#2563eb',
            'accent_pressed': '#1d4ed8',
            'success': '#10b981',
            'success_light': '#ecfdf5',
            'warning': '#f59e0b',
            'warning_light': '#fffbeb',
            'error': '#ef4444',
            'error_light': '#fef2f2',
            'sidebar_bg': '#ffffff',
            'sidebar_border': '#f0f3f6',
        }

        self.configure(bg=self.colors['background'])
        self.load_icon()
        self.setup_theme()
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill="both", expand=True)

        self.setup_sidebar()
        self.setup_content_area()

        self.current_frame = None
        self.active_button = None
        self.current_indicator = None

        self.show_dashboard()

    def load_icon(self):
        icon_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "DineSight.ico"),
            "DineSight.ico"
        ]
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    self.iconbitmap(icon_path)
                    return
                except tk.TclError:
                    continue

    def setup_theme(self):
        try:
            sv_ttk.set_theme("light")
        except:
            pass

        self.style = ttk.Style()
        self.style.configure('Modern.TButton', font=('Segoe UI', 10), padding=(20, 12))
        self.style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'), padding=(20, 12))
        self.style.configure('Card.TFrame', background=self.colors['surface'], relief='flat', borderwidth=1)

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_sidebar(self):
        self.sidebar = tk.Frame(self.main_container, bg=self.colors['sidebar_bg'], width=280)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        border = tk.Frame(self.sidebar, bg=self.colors['border_subtle'], width=1)
        border.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")

        self.create_sidebar_header()
        self.create_navigation()
        self.create_sidebar_footer()

    def create_sidebar_header(self):
        header_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar_bg'], height=140)
        header_frame.pack(fill="x", pady=(40, 30))
        header_frame.pack_propagate(False)

        brand_container = tk.Frame(header_frame, bg=self.colors['sidebar_bg'])
        brand_container.pack(expand=True)

        title_label = tk.Label(
            brand_container, text="DineSight", bg=self.colors['sidebar_bg'],
            fg=self.colors['accent'], font=("Segoe UI", 26, "bold")
        )
        title_label.pack()

        subtitle_label = tk.Label(
            brand_container, text="Restaurant Analytics",
            bg=self.colors['sidebar_bg'], fg=self.colors['text_secondary'], font=("Segoe UI", 12)
        )
        subtitle_label.pack(pady=(8, 0))

    def create_navigation(self):
        nav_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar_bg'])
        nav_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.nav_buttons = []
        self.nav_containers = []

        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Menu Tracker", self.show_menu_tracker),
            ("Inventory", self.show_inventory),
            ("Sales Logger", self.show_sales_logger),
            ("Trends & Insights", self.show_trends)
        ]

        for text, command in nav_items:
            btn_container = tk.Frame(nav_frame, bg=self.colors['sidebar_bg'])
            btn_container.pack(fill="x", pady=4)
            self.nav_containers.append(btn_container)

            btn = tk.Button(
                btn_container,
                text=text,
                bg=self.colors['sidebar_bg'],
                fg=self.colors['text_primary'],
                font=("Segoe UI", 12),
                bd=0,
                padx=24,
                pady=16,
                anchor="w",
                cursor="hand2",
                relief="flat",
                highlightthickness=0,
                takefocus=0
            )
            btn.pack(fill="x")
            self.nav_buttons.append(btn)

            btn.configure(command=lambda c=command, b=btn: self.on_nav_select(c, b))
            btn.bind("<Enter>", lambda e, b=btn: self.on_nav_hover_enter(b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_nav_hover_leave(b))

    def on_nav_hover_enter(self, button):
        if button != self.active_button:
            button.configure(bg=self.colors['surface_hover'], fg=self.colors['accent'])

    def on_nav_hover_leave(self, button):
        if button != self.active_button:
            button.configure(bg=self.colors['sidebar_bg'], fg=self.colors['text_primary'])

    def on_nav_select(self, command, button):
        command()
        self.set_active_button(button)

    def set_active_button(self, button):
        for btn in self.nav_buttons:
            if btn != button:
                btn.configure(
                    bg=self.colors['sidebar_bg'],
                    fg=self.colors['text_primary'],
                    font=("Segoe UI", 12)
                )
        button.configure(
            bg=self.colors['accent_light'],
            fg=self.colors['accent'],
            font=("Segoe UI", 12, "bold")
        )
        self.highlight_active_nav(button)
        self.active_button = button

    def highlight_active_nav(self, button):
        if self.current_indicator:
            self.current_indicator.destroy()
            self.current_indicator = None

        button_container = button.master
        button_container.update_idletasks()

        self.current_indicator = tk.Frame(
            button_container,
            bg=self.colors['accent'],
            width=4
        )
        self.current_indicator.place(x=0, y=0, relheight=1.0)

    def create_sidebar_footer(self):
        footer_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar_bg'], height=120)
        footer_frame.pack(side="bottom", fill="x")
        footer_frame.pack_propagate(False)

        divider = tk.Frame(footer_frame, bg=self.colors['border_subtle'], height=1)
        divider.pack(fill="x", padx=20, pady=(0, 25))

        status_container = tk.Frame(footer_frame, bg=self.colors['sidebar_bg'])
        status_container.pack(pady=10)

        status_dot = tk.Label(status_container, text="●", bg=self.colors['sidebar_bg'],
                              fg=self.colors['success'], font=("Segoe UI", 14))
        status_dot.pack(side="left")

        status_label = tk.Label(status_container, text=" System Online", bg=self.colors['sidebar_bg'],
                                fg=self.colors['text_secondary'], font=("Segoe UI", 11))
        status_label.pack(side="left")

        version_label = tk.Label(
            footer_frame, text="v1.0.0", bg=self.colors['sidebar_bg'],
            fg=self.colors['text_muted'], font=("Segoe UI", 10)
        )
        version_label.pack(pady=(8, 20))

    def setup_content_area(self):
        self.content_container = tk.Frame(self.main_container, bg=self.colors['background'])
        self.content_container.pack(side="right", fill="both", expand=True)

        self.canvas = tk.Canvas(self.content_container, bg=self.colors['background'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.content_container, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        def set_frame_width(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)

        self.canvas.bind("<Configure>", set_frame_width)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if self.scrollbar.winfo_manager():  # Only scroll if scrollbar is visible
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = ttk.Frame(self.scrollable_frame, padding=(40, 40))
        self.current_frame.pack(fill="x", expand=True, anchor="n")

    def show_sales_logger(self):
        self.clear_frame()
        content = SalesLogger(self.current_frame)
        content.pack(fill="both", expand=True)
        if self.nav_buttons:
            self.set_active_button(self.nav_buttons[3])

    def show_dashboard(self):
        self.clear_frame()
        content = Dashboard(self.current_frame)
        content.pack(fill="both", expand=True)
        if self.nav_buttons:
            self.set_active_button(self.nav_buttons[0])

    def show_menu_tracker(self):
        self.clear_frame()
        content = MenuTracker(self.current_frame)
        content.pack(fill="both", expand=True)
        if self.nav_buttons:
            self.set_active_button(self.nav_buttons[1])

    def show_inventory(self):
        self.clear_frame()
        content = InventoryManagement(self.current_frame)
        content.pack(fill="both", expand=True)
        if self.nav_buttons:
            self.set_active_button(self.nav_buttons[2])

    def show_trends(self):
        self.clear_frame()
        content = TrendsAnalysis(self.current_frame)
        content.pack(fill="both", expand=True)
        if self.nav_buttons:
            self.set_active_button(self.nav_buttons[4])


if __name__ == "__main__":
    app = DineSightApp()
    app.mainloop()