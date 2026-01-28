import os
import tkinter as tk
from tkinter import ttk

import sv_ttk

from Dashboard import Dashboard
from InventoryManagement import InventoryManagement
from MenuTracker import MenuTracker
from SalesLogger import SalesLogger
from TrendsAnalysis import TrendsAnalysis


class DineSightApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DineSight")
        self.center_window(1280, 780)
        self.minsize(1100, 650)

        self.colors = {
            "background": "#f5f7fa",
            "surface": "#ffffff",
            "surface_alt": "#f8fafc",
            "surface_hover": "#f1f5f9",
            "surface_pressed": "#e2e8f0",
            "border": "#e2e8f0",
            "border_subtle": "#f1f5f9",
            "text_primary": "#0f172a",
            "text_secondary": "#475569",
            "text_muted": "#94a3b8",
            "text_disabled": "#cbd5e1",
            "accent": "#2563eb",
            "accent_light": "#eff6ff",
            "accent_lighter": "#f8faff",
            "accent_hover": "#1d4ed8",
            "accent_pressed": "#1e40af",
            "success": "#059669",
            "success_light": "#ecfdf5",
            "warning": "#d97706",
            "warning_light": "#fffbeb",
            "error": "#dc2626",
            "error_light": "#fef2f2",
            "sidebar_bg": "#0f172a",
            "sidebar_text": "#94a3b8",
            "sidebar_text_active": "#ffffff",
            "sidebar_hover": "#1e293b",
            "sidebar_active": "#1e293b",
            "sidebar_accent": "#3b82f6",
            "card_shadow": "#e2e8f0",
        }

        self.configure(bg=self.colors["background"])
        self.load_icon()
        self.setup_theme()
        self.main_container = tk.Frame(self, bg=self.colors["background"])
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
            "DineSight.ico",
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
        except Exception:
            pass

        self.style = ttk.Style()

        # General widget fonts
        self.style.configure(".", font=("Segoe UI", 10))
        self.style.configure("TLabel", font=("Segoe UI", 10))
        self.style.configure("TEntry", font=("Segoe UI", 10))
        self.style.configure("TCombobox", font=("Segoe UI", 10))

        # Button styles
        self.style.configure("Modern.TButton", font=("Segoe UI", 10), padding=(16, 10))
        self.style.configure(
            "Accent.TButton", font=("Segoe UI", 10, "bold"), padding=(16, 10)
        )
        self.style.configure("Danger.TButton", font=("Segoe UI", 10), padding=(16, 10))

        # Card frame
        self.style.configure("Card.TFrame", background=self.colors["surface"])
        self.style.configure("CardInner.TFrame", background=self.colors["surface"])

        # Treeview styling
        self.style.configure(
            "Treeview",
            font=("Segoe UI", 10),
            rowheight=36,
            background=self.colors["surface"],
            fieldbackground=self.colors["surface"],
            borderwidth=0,
        )
        self.style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            background=self.colors["surface_alt"],
            foreground=self.colors["text_secondary"],
            borderwidth=0,
            relief="flat",
            padding=(10, 8),
        )
        self.style.map(
            "Treeview",
            background=[("selected", self.colors["accent_light"])],
            foreground=[("selected", self.colors["accent"])],
        )

        # LabelFrame
        self.style.configure(
            "TLabelframe",
            background=self.colors["surface"],
            foreground=self.colors["text_primary"],
            borderwidth=1,
            relief="solid",
        )
        self.style.configure(
            "TLabelframe.Label",
            font=("Segoe UI", 11, "bold"),
            foreground=self.colors["text_primary"],
            background=self.colors["surface"],
        )

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_sidebar(self):
        self.sidebar = tk.Frame(
            self.main_container, bg=self.colors["sidebar_bg"], width=260
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.create_sidebar_header()
        self.create_navigation()
        self.create_sidebar_footer()

    def create_sidebar_header(self):
        header_frame = tk.Frame(self.sidebar, bg=self.colors["sidebar_bg"], height=100)
        header_frame.pack(fill="x", pady=(28, 24))
        header_frame.pack_propagate(False)

        brand_container = tk.Frame(header_frame, bg=self.colors["sidebar_bg"])
        brand_container.pack(expand=True)

        title_label = tk.Label(
            brand_container,
            text="DineSight",
            bg=self.colors["sidebar_bg"],
            fg="#ffffff",
            font=("Segoe UI", 22, "bold"),
        )
        title_label.pack()

        subtitle_label = tk.Label(
            brand_container,
            text="Restaurant Management",
            bg=self.colors["sidebar_bg"],
            fg=self.colors["sidebar_text"],
            font=("Segoe UI", 10),
        )
        subtitle_label.pack(pady=(4, 0))

        # Divider
        divider = tk.Frame(self.sidebar, bg="#1e293b", height=1)
        divider.pack(fill="x", padx=24, pady=(0, 8))

    def create_navigation(self):
        nav_frame = tk.Frame(self.sidebar, bg=self.colors["sidebar_bg"])
        nav_frame.pack(fill="both", expand=True, padx=16, pady=8)

        # Section label
        section_label = tk.Label(
            nav_frame,
            text="NAVIGATION",
            bg=self.colors["sidebar_bg"],
            fg="#475569",
            font=("Segoe UI", 8, "bold"),
            anchor="w",
        )
        section_label.pack(fill="x", padx=8, pady=(4, 12))

        self.nav_buttons = []
        self.nav_containers = []

        nav_items = [
            ("\u2302  Dashboard", self.show_dashboard),
            ("\u2630  Menu Tracker", self.show_menu_tracker),
            ("\u2699  Inventory", self.show_inventory),
            ("\u2696  Sales Logger", self.show_sales_logger),
            ("\u2197  Trends & Insights", self.show_trends),
        ]

        for text, command in nav_items:
            btn_container = tk.Frame(nav_frame, bg=self.colors["sidebar_bg"])
            btn_container.pack(fill="x", pady=2)
            self.nav_containers.append(btn_container)

            btn = tk.Button(
                btn_container,
                text=text,
                bg=self.colors["sidebar_bg"],
                fg=self.colors["sidebar_text"],
                font=("Segoe UI", 11),
                bd=0,
                padx=16,
                pady=12,
                anchor="w",
                cursor="hand2",
                relief="flat",
                highlightthickness=0,
                activebackground=self.colors["sidebar_hover"],
                activeforeground="#ffffff",
                takefocus=0,
            )
            btn.pack(fill="x")
            self.nav_buttons.append(btn)

            btn.configure(command=lambda c=command, b=btn: self.on_nav_select(c, b))
            btn.bind("<Enter>", lambda e, b=btn: self.on_nav_hover_enter(b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_nav_hover_leave(b))

    def on_nav_hover_enter(self, button):
        if button != self.active_button:
            button.configure(bg=self.colors["sidebar_hover"], fg="#e2e8f0")

    def on_nav_hover_leave(self, button):
        if button != self.active_button:
            button.configure(
                bg=self.colors["sidebar_bg"], fg=self.colors["sidebar_text"]
            )

    def on_nav_select(self, command, button):
        command()
        self.set_active_button(button)

    def set_active_button(self, button):
        # Reset all buttons
        for btn in self.nav_buttons:
            if btn != button:
                btn.configure(
                    bg=self.colors["sidebar_bg"],
                    fg=self.colors["sidebar_text"],
                    font=("Segoe UI", 11),
                )

        # Remove old indicator
        if self.current_indicator:
            self.current_indicator.destroy()
            self.current_indicator = None

        # Set active button
        button.configure(
            bg=self.colors["sidebar_active"],
            fg=self.colors["sidebar_text_active"],
            font=("Segoe UI", 11, "bold"),
        )

        # Add left accent bar
        button_container = button.master
        button_container.update_idletasks()
        self.current_indicator = tk.Frame(
            button_container, bg=self.colors["sidebar_accent"], width=3
        )
        self.current_indicator.place(x=0, y=2, relheight=0.85)

        self.active_button = button

    def create_sidebar_footer(self):
        footer_frame = tk.Frame(self.sidebar, bg=self.colors["sidebar_bg"], height=90)
        footer_frame.pack(side="bottom", fill="x")
        footer_frame.pack_propagate(False)

        divider = tk.Frame(footer_frame, bg="#1e293b", height=1)
        divider.pack(fill="x", padx=24, pady=(0, 16))

        status_container = tk.Frame(footer_frame, bg=self.colors["sidebar_bg"])
        status_container.pack(padx=24, anchor="w")

        status_dot = tk.Label(
            status_container,
            text="\u25cf",
            bg=self.colors["sidebar_bg"],
            fg=self.colors["success"],
            font=("Segoe UI", 10),
        )
        status_dot.pack(side="left")

        status_label = tk.Label(
            status_container,
            text=" System Online",
            bg=self.colors["sidebar_bg"],
            fg=self.colors["sidebar_text"],
            font=("Segoe UI", 9),
        )
        status_label.pack(side="left")

        version_label = tk.Label(
            footer_frame,
            text="v1.0.0",
            bg=self.colors["sidebar_bg"],
            fg="#475569",
            font=("Segoe UI", 9),
        )
        version_label.pack(padx=24, anchor="w", pady=(4, 16))

    def setup_content_area(self):
        self.content_container = tk.Frame(
            self.main_container, bg=self.colors["background"]
        )
        self.content_container.pack(side="right", fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.content_container,
            bg=self.colors["background"],
            highlightthickness=0,
            bd=0,
        )
        self.scrollbar = ttk.Scrollbar(
            self.content_container, orient="vertical", command=self.canvas.yview
        )

        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors["background"])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        def set_frame_width(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)

        self.canvas.bind("<Configure>", set_frame_width)

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if self.scrollbar.winfo_manager():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(
            self.scrollable_frame, bg=self.colors["background"]
        )
        self.current_frame.pack(fill="x", expand=True, anchor="n", padx=32, pady=28)

        # Reset scroll position to top
        self.canvas.yview_moveto(0)

    def show_sales_logger(self):
        self.clear_frame()
        content = SalesLogger(self.current_frame, self.colors)
        content.pack(fill="both", expand=True)
        if self.nav_buttons:
            self.set_active_button(self.nav_buttons[3])

    def show_dashboard(self):
        self.clear_frame()
        content = Dashboard(self.current_frame, self.colors)
        content.pack(fill="both", expand=True)
        if self.nav_buttons:
            self.set_active_button(self.nav_buttons[0])

    def show_menu_tracker(self):
        self.clear_frame()
        content = MenuTracker(self.current_frame, self.colors)
        content.pack(fill="both", expand=True)
        if self.nav_buttons:
            self.set_active_button(self.nav_buttons[1])

    def show_inventory(self):
        self.clear_frame()
        content = InventoryManagement(self.current_frame, self.colors)
        content.pack(fill="both", expand=True)
        if self.nav_buttons:
            self.set_active_button(self.nav_buttons[2])

    def show_trends(self):
        self.clear_frame()
        content = TrendsAnalysis(self.current_frame, self.colors)
        content.pack(fill="both", expand=True)
        if self.nav_buttons:
            self.set_active_button(self.nav_buttons[4])


if __name__ == "__main__":
    app = DineSightApp()
    app.mainloop()
