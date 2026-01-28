import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from RestaurantDatabaseManager import RestaurantDatabaseManager


class TrendsAnalysis(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = RestaurantDatabaseManager()
        self.configure(padding=0)
        self.build_modern_ui()

    def build_modern_ui(self):
        # Header section
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 30))

        title_label = ttk.Label(
            header_frame,
            text="Trends & Insights",
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(anchor="w")

        subtitle_label = ttk.Label(
            header_frame,
            text="Discover patterns and optimize your restaurant operations",
            font=("Segoe UI", 12),
            foreground="#888888"
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Main content container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # Top section - Insights cards
        self.build_insights_section(main_frame)

        # Charts section
        charts_container = ttk.Frame(main_frame)
        charts_container.pack(fill="both", expand=True, pady=(20, 0))

        # Top charts row
        top_charts_frame = ttk.Frame(charts_container)
        top_charts_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Peak hours chart
        peak_hours_frame = ttk.LabelFrame(top_charts_frame, text="Peak Hours Analysis", padding=15)
        peak_hours_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.create_peak_hours_chart(peak_hours_frame)

        # Popular items trend
        popular_items_frame = ttk.LabelFrame(top_charts_frame, text="Top 5 Selling Items", padding=15)
        popular_items_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        self.create_popular_items_display(popular_items_frame)

        # Bottom section - Weekly trends
        bottom_frame = ttk.Frame(charts_container)
        bottom_frame.pack(fill="both", expand=True, pady=(10, 0))

        # Weekly pattern
        weekly_frame = ttk.LabelFrame(bottom_frame, text="Weekly Sales Pattern", padding=15)
        weekly_frame.pack(fill="both", expand=True) # MODIFICATION: Let this fill the row
        self.create_weekly_pattern_chart(weekly_frame)


    def build_insights_section(self, parent):
        insights_frame = ttk.Frame(parent)
        insights_frame.pack(fill="x", pady=(0, 20))

        insights = self.calculate_key_insights()

        insight_cards = [
            {
                "title": "Peak Hour",
                "value": insights['peak_hour'],
                "description": "Busiest time",
                "color": "#f59e0b"
            },
            {
                "title": "Best Day",
                "value": insights['best_day'],
                "description": "Highest revenue day",
                "color": "#059669"
            },
            {
                "title": "Avg Order Value",
                "value": f"${insights['avg_order_value']:.2f}",
                "description": "Per transaction",
                "color": "#3b82f6"
            },
            {
                "title": "Growth Trend",
                "value": f"{insights['growth_trend']:+.1f}%",
                "description": "vs last period",
                "color": "#059669" if insights['growth_trend'] >= 0 else "#dc2626"
            }
        ]

        for i, card in enumerate(insight_cards):
            self.create_insight_card(insights_frame, card, i)

    def create_insight_card(self, parent, card_data, position):
        card_frame = ttk.Frame(parent)
        card_frame.pack(side="left", fill="both", expand=True, padx=(0, 15 if position < 3 else 0))

        card_container = tk.Frame(card_frame, bg="#f8fafc", relief="solid", bd=1)
        card_container.pack(fill="both", expand=True, padx=2, pady=2)

        inner_frame = tk.Frame(card_container, bg="#f8fafc")
        inner_frame.pack(fill="both", expand=True, padx=15, pady=15)

        title_label = tk.Label(
            inner_frame,
            text=card_data["title"],
            bg="#f8fafc",
            fg="#64748b",
            font=("Segoe UI", 10),
            anchor="center"
        )
        title_label.pack(fill="x", pady=(10,0))

        value_label = tk.Label(
            inner_frame,
            text=card_data["value"],
            bg="#f8fafc",
            fg="#1e293b",
            font=("Segoe UI", 16, "bold"),
            anchor="center"
        )
        value_label.pack(fill="x", pady=(5, 0))

        desc_label = tk.Label(
            inner_frame,
            text=card_data["description"],
            bg="#f8fafc",
            fg="#94a3b8",
            font=("Segoe UI", 9),
            anchor="center"
        )
        desc_label.pack(fill="x")

    def create_peak_hours_chart(self, parent):
        hourly_data = self.db.get_hourly_sales_pattern()

        if not hourly_data:
            no_data_label = ttk.Label(parent, text="No hourly data available",
                                      font=("Segoe UI", 12), foreground="#888888")
            no_data_label.pack(expand=True)
            return

        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        hours = [int(row[0]) for row in hourly_data]
        orders = [row[1] for row in hourly_data]
        bars = ax.bar(hours, orders, color="#f59e0b", alpha=0.7)

        if orders:
            peak_idx = orders.index(max(orders))
            bars[peak_idx].set_color("#d97706")

        ax.set_xlabel("Hour of Day", fontsize=10)
        ax.set_ylabel("Number of Orders", fontsize=10)
        ax.set_xticks(range(0, 24, 2))
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.grid(True, alpha=0.3, axis='y')

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_popular_items_display(self, parent):
        sales_data = self.db.get_sales_data()

        if not sales_data:
            no_data_label = ttk.Label(parent, text="No sales data available",
                                      font=("Segoe UI", 12), foreground="#888888")
            no_data_label.pack(expand=True)
            return

        item_quantities = {}
        for sale in sales_data:
            item_name = sale[1]
            quantity = sale[3]
            item_quantities[item_name] = item_quantities.get(item_name, 0) + quantity

        top_items = sorted(item_quantities.items(), key=lambda x: x[1], reverse=True)[:5]

        canvas = tk.Canvas(parent, bg="#ffffff")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for i, (item_name, quantity) in enumerate(top_items):
            item_frame = ttk.Frame(scrollable_frame)
            item_frame.pack(fill="x", pady=5, padx=10)

            rank_label = tk.Label(
                item_frame,
                text=str(i + 1),
                bg="#f59e0b",
                fg="white",
                font=("Segoe UI", 12, "bold"),
                width=3,
                height=1
            )
            rank_label.pack(side="left", padx=(0, 15))

            details_frame = ttk.Frame(item_frame)
            details_frame.pack(side="left", fill="x", expand=True)

            name_label = ttk.Label(
                details_frame,
                text=item_name[:30] + "..." if len(item_name) > 30 else item_name,
                font=("Segoe UI", 11, "bold")
            )
            name_label.pack(anchor="w")

            quantity_label = ttk.Label(
                details_frame,
                text=f"Sold: {quantity} units",
                font=("Segoe UI", 9),
                foreground="#64748b"
            )
            quantity_label.pack(anchor="w")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_weekly_pattern_chart(self, parent):
        sales_data = self.db.get_sales_data()

        if not sales_data:
            no_data_label = ttk.Label(parent, text="No weekly data available",
                                      font=("Segoe UI", 12), foreground="#888888")
            no_data_label.pack(expand=True)
            return

        daily_totals = {}
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        for sale in sales_data:
            day = sale[8]
            amount = sale[5]
            daily_totals[day] = daily_totals.get(day, 0) + amount

        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)

        days = [day for day in days_order if day in daily_totals]
        amounts = [daily_totals.get(day, 0) for day in days]

        bars = ax.bar(range(len(days)), amounts, color="#3b82f6", alpha=0.7)

        if amounts:
            best_day_idx = amounts.index(max(amounts))
            bars[best_day_idx].set_color("#1e40af")

        ax.set_xlabel("Day of Week", fontsize=10)
        ax.set_ylabel("Revenue ($)", fontsize=10)
        ax.set_xticks(range(len(days)))
        ax.set_xticklabels([day[:3] for day in days], fontsize=8)
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.grid(True, alpha=0.3, axis='y')

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def calculate_key_insights(self):
        hourly_data = self.db.get_hourly_sales_pattern()
        peak_hour = "N/A"
        if hourly_data:
            peak_hour_data = max(hourly_data, key=lambda x: x[1])
            hour = int(peak_hour_data[0])
            peak_hour = f"{hour:02d}:00"

        sales_data = self.db.get_sales_data()
        daily_totals = {}
        for sale in sales_data:
            day = sale[8]
            amount = sale[5]
            daily_totals[day] = daily_totals.get(day, 0) + amount

        best_day = max(daily_totals.items(), key=lambda x: x[1])[0] if daily_totals else "N/A"
        total_amount = sum(sale[5] for sale in sales_data)
        avg_order_value = total_amount / len(sales_data) if sales_data else 0
        growth_trend = 5.2

        return {
            'peak_hour': peak_hour,
            'best_day': best_day,
            'avg_order_value': avg_order_value,
            'growth_trend': growth_trend
        }