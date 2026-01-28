import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from RestaurantDatabaseManager import RestaurantDatabaseManager


class Dashboard(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = RestaurantDatabaseManager()
        self.configure(padding=0)
        self.build_modern_ui()
        self.refresh_analytics()

    def build_modern_ui(self):
        # Header section
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 30))

        title_label = ttk.Label(
            header_frame,
            text="Dashboard",
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(anchor="w")

        subtitle_label = ttk.Label(
            header_frame,
            text="Real-time sales performance and revenue insights",
            font=("Segoe UI", 12),
            foreground="#888888"
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Main content container
        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True)

        self.build_smart_insights(content_frame)

        # Top section - KPI Cards
        self.build_kpi_section(content_frame)

        # Bottom section - Charts
        charts_frame = ttk.Frame(content_frame)
        charts_frame.pack(fill="both", expand=True, pady=(20, 0))

        # --- MODIFICATION START ---
        # Left chart - Revenue trends
        # Changed title to be more general
        self.revenue_chart_frame = ttk.LabelFrame(charts_frame, text="Revenue Trend", padding=15)
        self.revenue_chart_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Add a frame for controls (dropdown)
        chart_control_frame = ttk.Frame(self.revenue_chart_frame)
        chart_control_frame.pack(fill="x", pady=(0, 10))

        self.revenue_trend_var = tk.StringVar()
        self.revenue_trend_combo = ttk.Combobox(
            chart_control_frame,
            textvariable=self.revenue_trend_var,
            state="readonly"
        )
        self.revenue_trend_combo['values'] = [
            "Daily (Last 30 Days)",
            "Monthly (Last 12 Months)",
            "Yearly (All Time)"
        ]
        self.revenue_trend_combo.set("Daily (Last 30 Days)")
        # Bind the combobox selection to the update function
        self.revenue_trend_combo.bind("<<ComboboxSelected>>", self.update_revenue_chart)
        self.revenue_trend_combo.pack(side="right")

        ttk.Label(chart_control_frame, text="Select Timeframe:").pack(side="right", padx=(0, 5))

        # Add a dedicated frame for the canvas, so we can clear it
        self.revenue_canvas_frame = ttk.Frame(self.revenue_chart_frame)
        self.revenue_canvas_frame.pack(fill="both", expand=True)

        # Call the new update function to draw the initial chart
        self.update_revenue_chart()
        # --- MODIFICATION END ---

        # Right chart - Category performance
        right_chart_frame = ttk.LabelFrame(charts_frame, text="Sales by Category", padding=15)
        right_chart_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.create_category_chart(right_chart_frame)

    def build_smart_insights(self, parent):
        insights = self.generate_dashboard_insights()

        if not insights:
            return

        insights_frame = ttk.LabelFrame(parent, text="Smart Insights", padding=15)
        insights_frame.pack(fill="x", pady=(0, 20))

        for insight in insights:
            self.create_insight_row(insights_frame, insight['type'], insight['text'])

    def create_insight_row(self, parent, insight_type, text):
        insight_row = tk.Frame(parent, bg="#eff6ff")
        insight_row.pack(fill="x", pady=5)

        type_label = tk.Label(
            insight_row,
            text=f" {insight_type.upper()} ",
            bg="#3b82f6",
            fg="#ffffff",
            font=("Segoe UI", 9, "bold")
        )
        type_label.pack(side="left", padx=(10, 15), pady=10)

        text_label = tk.Label(
            insight_row,
            text=text,
            bg="#eff6ff",
            fg="#1e293b",
            font=("Segoe UI", 10),
            wraplength=800,
            justify="left"
        )
        text_label.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=10)

    # MODIFICATION: New function to generate specific, dynamic insights
    def generate_dashboard_insights(self):
        insights = []

        # Insight 1: Best/Worst Day of Last 7 Days
        try:
            seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            today = datetime.now().strftime("%Y-%m-%d")
            sales_data = self.db.get_sales_data(date_range=[seven_days_ago, today])

            daily_totals = {}
            if sales_data:
                for sale in sales_data:
                    day_name = sale[8]  # day_of_week
                    date = sale[6]  # order_date
                    day_key = f"{day_name} ({date})"
                    amount = sale[5]  # total_amount
                    daily_totals[day_key] = daily_totals.get(day_key, 0) + amount

            if len(daily_totals) > 1:
                best_day_key, best_day_revenue = max(daily_totals.items(), key=lambda x: x[1])
                slowest_day_key, slowest_day_revenue = min(daily_totals.items(), key=lambda x: x[1])

                # Check if we have a valid best/worst day that isn't today
                if best_day_key != slowest_day_key:
                    insights.append({
                        "type": "Insight",
                        "text": f"This past week, {best_day_key} was your best day with ${best_day_revenue:.2f} in sales. "
                                f"{slowest_day_key} was your slowest, with ${slowest_day_revenue:.2f}."
                    })
        except Exception as e:
            print(f"Error generating daily insight: {e}")  # Fail silently in UI

        # Insight 2: Peak Hour
        try:
            hourly_data = self.db.get_hourly_sales_pattern()
            if hourly_data:
                peak_hour_data = max(hourly_data, key=lambda x: x[1])  # Find hour with most orders
                hour = int(peak_hour_data[0])
                hour_str = f"{hour % 12 or 12} {'PM' if hour >= 12 else 'AM'}"

                insights.append({
                    "type": "Tip",
                    "text": f"Your peak hour for orders is around {hour_str}. Consider adding extra staff or pre-stocking popular items for this time."
                })
        except Exception as e:
            print(f"Error generating peak hour insight: {e}")

        # Insight 3: Low Stock Warning (Critical)
        try:
            low_stock_items = self.db.get_inventory(low_stock_only=True)
            if low_stock_items:
                item_names = [item[1] for item in low_stock_items[:3]]  # Get first 3
                more_items = "..." if len(low_stock_items) > 3 else ""
                insights.append({
                    "type": "Warning",
                    "text": f"You are running low on: {', '.join(item_names)}{more_items}. Check your inventory!"
                })
        except Exception as e:
            print(f"Error generating low stock insight: {e}")

        return insights

    def build_kpi_section(self, parent):
        kpi_frame = ttk.Frame(parent)
        kpi_frame.pack(fill="x", pady=(0, 20))

        sales_summary = self.db.get_sales_summary()
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        yesterday_sales = self.db.get_sales_data([yesterday, yesterday])
        yesterday_revenue = sum(sale[5] for sale in yesterday_sales) if yesterday_sales else 0

        today_revenue = sales_summary['today']['revenue']
        revenue_change = ((today_revenue - yesterday_revenue) / yesterday_revenue * 100) if yesterday_revenue > 0 else 0

        kpi_cards = [
            {
                "title": "Today's Revenue",
                "value": f"${today_revenue:.2f}",
                "change": f"{revenue_change:+.1f}%",
                "color": "#059669" if revenue_change >= 0 else "#dc2626"
            },
            {
                "title": "Orders Today",
                "value": str(sales_summary['today']['count']),
                "change": "Active",
                "color": "#059669"
            },
            {
                "title": "Monthly Revenue",
                "value": f"${sales_summary['month']['revenue']:.2f}",
                "change": f"{sales_summary['month']['count']} orders",
                "color": "#059669"
            },
            {
                "title": "Top Selling Item",
                "value": sales_summary['popular_item'][:20],
                "change": "Most popular",
                "color": "#f59e0b"
            }
        ]

        for i, card in enumerate(kpi_cards):
            self.create_kpi_card(kpi_frame, card, i)

    def create_kpi_card(self, parent, card_data, position):
        card_frame = ttk.Frame(parent)
        card_frame.pack(side="left", fill="both", expand=True, padx=(0, 15 if position < 3 else 0))

        card_container = tk.Frame(card_frame, bg="#ffffff", relief="solid", bd=1)
        card_container.pack(fill="both", expand=True, padx=2, pady=2)

        inner_frame = tk.Frame(card_container, bg="#ffffff")
        inner_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = tk.Label(
            inner_frame,
            text=card_data["title"],
            bg="#ffffff",
            fg="#64748b",
            font=("Segoe UI", 11),
            anchor="w"
        )
        title_label.pack(fill="x", pady=(0, 10))

        value_label = tk.Label(
            inner_frame,
            text=card_data["value"],
            bg="#ffffff",
            fg="#1e293b",
            font=("Segoe UI", 18, "bold"),
            anchor="w"
        )
        value_label.pack(fill="x", pady=(0, 5))

        change_label = tk.Label(
            inner_frame,
            text=card_data["change"],
            bg="#ffffff",
            fg=card_data["color"],
            font=("Segoe UI", 10),
            anchor="w"
        )
        change_label.pack(fill="x")

    # --- MODIFICATION START ---
    # Replaced create_revenue_chart with update_revenue_chart
    # This function now handles all logic for the revenue trend chart
    def update_revenue_chart(self, event=None):
        """Clears and redraws the revenue chart based on the combobox selection."""

        # 1. Clear the previous chart
        for widget in self.revenue_canvas_frame.winfo_children():
            widget.destroy()

        period_str = self.revenue_trend_var.get()

        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)

        data_found = False

        try:
            if period_str == "Daily (Last 30 Days)":
                # Use the original logic for the 30-day view
                daily_data = self.db.get_daily_sales_trend(30)
                if daily_data:
                    # Assumes row[0] is date string, row[2] is revenue
                    dates = [datetime.strptime(row[0], "%Y-%m-%d") for row in daily_data]
                    revenues = [row[2] for row in daily_data]

                    ax.plot(dates, revenues, color="#f59e0b", linewidth=2, marker='o', markersize=4)
                    ax.fill_between(dates, revenues, alpha=0.3, color="#fef3c7")
                    fig.autofmt_xdate()
                    data_found = True

            elif period_str == "Monthly (Last 12 Months)":
                # Get raw data for the last year and aggregate it
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                raw_data = self.db.get_sales_data(
                    date_range=[start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")])
                aggregated_data = self.aggregate_data(raw_data, 'monthly')

                if aggregated_data:
                    # aggregated_data is [(date_str, revenue)]
                    dates = [datetime.strptime(d[0], "%Y-%m") for d in aggregated_data]
                    revenues = [d[1] for d in aggregated_data]

                    ax.plot(dates, revenues, color="#f59e0b", linewidth=2, marker='o', markersize=4)
                    ax.fill_between(dates, revenues, alpha=0.3, color="#fef3c7")
                    fig.autofmt_xdate()
                    data_found = True

            elif period_str == "Yearly (All Time)":
                # Get all data (using a very old start date) and aggregate
                start_date = datetime(2000, 1, 1)
                end_date = datetime.now()
                raw_data = self.db.get_sales_data(
                    date_range=[start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")])
                aggregated_data = self.aggregate_data(raw_data, 'yearly')

                if aggregated_data:
                    # Use a bar chart for yearly data
                    dates_str = [d[0] for d in aggregated_data]
                    revenues = [d[1] for d in aggregated_data]

                    ax.bar(dates_str, revenues, color="#f59e0b")
                    data_found = True

        except Exception as e:
            print(f"Error updating revenue chart: {e}")
            data_found = False  # Ensure no-data label is shown

        if not data_found:
            no_data_label = ttk.Label(self.revenue_canvas_frame, text="No sales data available for this period",
                                      font=("Segoe UI", 12), foreground="#888888")
            no_data_label.pack(expand=True)
            return

        # Common chart formatting
        ax.set_xlabel("Date", fontsize=10)
        ax.set_ylabel("Revenue ($)", fontsize=10)
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.grid(True, alpha=0.3)

        canvas = FigureCanvasTkAgg(fig, self.revenue_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def aggregate_data(self, raw_data, period):
        """
        Aggregates raw sales data by month or year.
        Assumes raw_data is list of tuples where sale[6] is date ("%Y-%m-%d")
        and sale[5] is total_amount.
        """
        aggregated_data = {}
        if not raw_data:
            return []

        date_format = ""
        if period == 'monthly':
            date_format = "%Y-%m"  # Group by YYYY-MM
        elif period == 'yearly':
            date_format = "%Y"  # Group by YYYY
        else:
            return []  # Invalid period

        for sale in raw_data:
            try:
                # sale[6] is order_date, sale[5] is total_amount
                date_obj = datetime.strptime(sale[6], "%Y-%m-%d")
                amount = sale[5]
                key = date_obj.strftime(date_format)
                aggregated_data[key] = aggregated_data.get(key, 0) + amount
            except (ValueError, TypeError, IndexError) as e:
                print(f"Skipping bad sales data row: {e}")
                continue

        # Sort by key (e.g., "2023-01", "2023-02"...)
        return sorted(aggregated_data.items())

    # --- MODIFICATION END ---

    def create_category_chart(self, parent):
        category_data = self.db.get_category_performance()

        if not category_data:
            no_data_label = ttk.Label(parent, text="No category data available",
                                      font=("Segoe UI", 12), foreground="#888888")
            no_data_label.pack(expand=True)
            return

        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)

        categories = [row[0] for row in category_data]
        revenues = [row[3] for row in category_data]
        colors = ['#f59e0b', '#059669', '#dc2626', '#3b82f6', '#8b5cf6']
        bars = ax.bar(categories, revenues, color=colors[:len(categories)])

        ax.set_xlabel("Category", fontsize=10)
        ax.set_ylabel("Revenue ($)", fontsize=10)
        ax.tick_params(axis='both', which='major', labelsize=8)
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + height * 0.01,
                    f'${height:.0f}', ha='center', va='bottom', fontsize=8)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def refresh_analytics(self):
        # Placeholder
        self.after(5000, self.refresh_analytics)