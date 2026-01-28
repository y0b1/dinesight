import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from RestaurantDatabaseManager import RestaurantDatabaseManager


class TrendsAnalysis(tk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors['background'])
        self.db = RestaurantDatabaseManager()
        self.colors = colors
        self.build_ui()

    def build_ui(self):
        c = self.colors

        # Header
        header = tk.Frame(self, bg=c['background'])
        header.pack(fill="x", pady=(0, 24))

        tk.Label(header, text="Trends & Insights", bg=c['background'],
                 fg=c['text_primary'], font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Discover patterns and optimize your restaurant operations",
                 bg=c['background'], fg=c['text_secondary'],
                 font=("Segoe UI", 11)).pack(anchor="w", pady=(4, 0))

        # Insight cards row
        self.build_insights_row()

        # Charts grid
        charts = tk.Frame(self, bg=c['background'])
        charts.pack(fill="both", expand=True, pady=(20, 0))

        # Top row: peak hours + top items
        top_row = tk.Frame(charts, bg=c['background'])
        top_row.pack(fill="both", expand=True, pady=(0, 12))

        self.build_peak_hours_card(top_row)
        self.build_top_items_card(top_row)

        # Bottom row: weekly pattern
        self.build_weekly_card(charts)

    # Insight Cards

    def build_insights_row(self):
        c = self.colors
        insights = self._calculate_insights()

        row = tk.Frame(self, bg=c['background'])
        row.pack(fill="x")

        cards = [
            ("Peak Hour", insights['peak_hour'], "Busiest time", c['warning']),
            ("Best Day", insights['best_day'], "Highest revenue", c['success']),
            ("Avg Order Value", "${:.2f}".format(insights['avg_order']), "Per transaction", c['accent']),
            ("Growth Trend", "{:+.1f}%".format(insights['growth']), "vs previous period",
             c['success'] if insights['growth'] >= 0 else c['error']),
        ]

        for i, (title, value, desc, color) in enumerate(cards):
            card = tk.Frame(row, bg=c['surface'], bd=1, relief="solid",
                            highlightbackground=c['border'], highlightthickness=1)
            card.pack(side="left", fill="both", expand=True,
                      padx=(0, 12) if i < len(cards) - 1 else (0, 0), pady=4)

            inner = tk.Frame(card, bg=c['surface'])
            inner.pack(fill="both", expand=True, padx=16, pady=16)

            # Color accent bar at top
            accent = tk.Frame(card, bg=color, height=3)
            accent.place(x=0, y=0, relwidth=1.0)

            tk.Label(inner, text=title, bg=c['surface'], fg=c['text_secondary'],
                     font=("Segoe UI", 9), anchor="center").pack(fill="x", pady=(6, 2))
            tk.Label(inner, text=value, bg=c['surface'], fg=c['text_primary'],
                     font=("Segoe UI", 18, "bold"), anchor="center").pack(fill="x", pady=(0, 2))
            tk.Label(inner, text=desc, bg=c['surface'], fg=c['text_muted'],
                     font=("Segoe UI", 9), anchor="center").pack(fill="x")

    def _calculate_insights(self):
        # Peak hour
        hourly = self.db.get_hourly_sales_pattern()
        peak_hour = "N/A"
        if hourly:
            best = max(hourly, key=lambda x: x[1])
            h = int(best[0])
            ampm = "PM" if h >= 12 else "AM"
            peak_hour = str(h % 12 or 12) + " " + ampm

        # Best day
        sales = self.db.get_sales_data()
        daily_totals = {}
        for s in sales:
            daily_totals[s[8]] = daily_totals.get(s[8], 0) + s[5]
        best_day = max(daily_totals.items(), key=lambda x: x[1])[0] if daily_totals else "N/A"

        # Avg order value
        total = sum(s[5] for s in sales)
        avg_order = total / len(sales) if sales else 0

        # Growth trend: compare last 30 days vs previous 30 days
        growth = 0.0
        try:
            now = datetime.now()
            d30 = (now - timedelta(days=30)).strftime("%Y-%m-%d")
            d60 = (now - timedelta(days=60)).strftime("%Y-%m-%d")
            today = now.strftime("%Y-%m-%d")

            recent = self.db.get_sales_data(date_range=[d30, today])
            previous = self.db.get_sales_data(date_range=[d60, d30])

            recent_rev = sum(s[5] for s in recent) if recent else 0
            prev_rev = sum(s[5] for s in previous) if previous else 0

            if prev_rev > 0:
                growth = ((recent_rev - prev_rev) / prev_rev) * 100
        except Exception:
            pass

        return {
            'peak_hour': peak_hour,
            'best_day': best_day,
            'avg_order': avg_order,
            'growth': growth,
        }

    # Peak Hours Chart

    def build_peak_hours_card(self, parent):
        c = self.colors
        card = tk.Frame(parent, bg=c['surface'], bd=1, relief="solid",
                        highlightbackground=c['border'], highlightthickness=1)
        card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(card, text="Peak Hours Analysis", bg=c['surface'], fg=c['text_primary'],
                 font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x", padx=20, pady=(16, 8))

        canvas_frame = tk.Frame(card, bg=c['surface'])
        canvas_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        hourly = self.db.get_hourly_sales_pattern()
        if not hourly:
            tk.Label(canvas_frame, text="No hourly data available",
                     bg=c['surface'], fg=c['text_muted'],
                     font=("Segoe UI", 11)).pack(expand=True, pady=40)
            return

        fig = Figure(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor(c['surface'])
        ax = fig.add_subplot(111)
        ax.set_facecolor(c['surface'])

        hours = [int(r[0]) for r in hourly]
        orders = [r[1] for r in hourly]
        colors_list = [c['warning']] * len(hours)

        if orders:
            peak_idx = orders.index(max(orders))
            colors_list[peak_idx] = '#b45309'

        ax.bar(hours, orders, color=colors_list, width=0.7)
        ax.set_xlabel("Hour of Day", fontsize=9, color=c['text_secondary'])
        ax.set_ylabel("Orders", fontsize=9, color=c['text_secondary'])
        ax.set_xticks(range(0, 24, 3))
        ax.tick_params(axis='both', labelsize=8, colors=c['text_muted'])
        ax.grid(True, alpha=0.15, axis='y', color=c['text_muted'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(c['border'])
        ax.spines['bottom'].set_color(c['border'])
        fig.tight_layout(pad=2)

        canvas = FigureCanvasTkAgg(fig, canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # Top Items

    def build_top_items_card(self, parent):
        c = self.colors
        card = tk.Frame(parent, bg=c['surface'], bd=1, relief="solid",
                        highlightbackground=c['border'], highlightthickness=1)
        card.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(card, text="Top 5 Selling Items", bg=c['surface'], fg=c['text_primary'],
                 font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x", padx=20, pady=(16, 12))

        content = tk.Frame(card, bg=c['surface'])
        content.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        sales = self.db.get_sales_data()
        if not sales:
            tk.Label(content, text="No sales data yet",
                     bg=c['surface'], fg=c['text_muted'],
                     font=("Segoe UI", 11)).pack(expand=True, pady=40)
            return

        quantities = {}
        for s in sales:
            quantities[s[1]] = quantities.get(s[1], 0) + s[3]

        top = sorted(quantities.items(), key=lambda x: x[1], reverse=True)[:5]
        max_qty = top[0][1] if top else 1

        medal_colors = ['#f59e0b', '#94a3b8', '#b45309']

        for i, (name, qty) in enumerate(top):
            row_frame = tk.Frame(content, bg=c['surface'])
            row_frame.pack(fill="x", pady=6)

            # Rank badge
            badge_bg = medal_colors[i] if i < 3 else c['text_muted']
            rank = tk.Label(row_frame, text=str(i + 1), bg=badge_bg, fg='#ffffff',
                            font=("Segoe UI", 10, "bold"), width=3)
            rank.pack(side="left", padx=(0, 12))

            # Info
            info = tk.Frame(row_frame, bg=c['surface'])
            info.pack(side="left", fill="x", expand=True)

            tk.Label(info, text=name[:28], bg=c['surface'], fg=c['text_primary'],
                     font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x")

            # Progress bar
            bar_bg = tk.Frame(info, bg=c['border'], height=6)
            bar_bg.pack(fill="x", pady=(3, 0))
            pct = qty / max_qty if max_qty else 0
            bar_fill = tk.Frame(bar_bg, bg=c['accent'], height=6,
                                width=max(int(pct * 300), 4))
            bar_fill.place(x=0, y=0, height=6)

            # Count
            tk.Label(row_frame, text="{} sold".format(qty), bg=c['surface'], fg=c['text_secondary'],
                     font=("Segoe UI", 9)).pack(side="right")

    # Weekly Pattern

    def build_weekly_card(self, parent):
        c = self.colors
        card = tk.Frame(parent, bg=c['surface'], bd=1, relief="solid",
                        highlightbackground=c['border'], highlightthickness=1)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Weekly Sales Pattern", bg=c['surface'], fg=c['text_primary'],
                 font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x", padx=20, pady=(16, 8))

        canvas_frame = tk.Frame(card, bg=c['surface'])
        canvas_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        sales = self.db.get_sales_data()
        if not sales:
            tk.Label(canvas_frame, text="No weekly data available",
                     bg=c['surface'], fg=c['text_muted'],
                     font=("Segoe UI", 11)).pack(expand=True, pady=40)
            return

        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily = {}
        for s in sales:
            daily[s[8]] = daily.get(s[8], 0) + s[5]

        days = [d for d in days_order if d in daily]
        amounts = [daily.get(d, 0) for d in days]

        fig = Figure(figsize=(10, 3), dpi=100)
        fig.patch.set_facecolor(c['surface'])
        ax = fig.add_subplot(111)
        ax.set_facecolor(c['surface'])

        colors_list = [c['accent']] * len(days)
        if amounts:
            best_idx = amounts.index(max(amounts))
            colors_list[best_idx] = c['accent_hover']

        bars = ax.bar(range(len(days)), amounts, color=colors_list, width=0.5)

        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + h * 0.02,
                        "${:,.0f}".format(h), ha='center', va='bottom', fontsize=8,
                        color=c['text_secondary'])

        ax.set_ylabel("Revenue ($)", fontsize=9, color=c['text_secondary'])
        ax.set_xticks(range(len(days)))
        ax.set_xticklabels([d[:3] for d in days], fontsize=9)
        ax.tick_params(axis='both', labelsize=8, colors=c['text_muted'])
        ax.grid(True, alpha=0.15, axis='y', color=c['text_muted'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(c['border'])
        ax.spines['bottom'].set_color(c['border'])
        fig.tight_layout(pad=2)

        canvas = FigureCanvasTkAgg(fig, canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
