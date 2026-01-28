import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from RestaurantDatabaseManager import RestaurantDatabaseManager


class Dashboard(tk.Frame):
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

        tk.Label(header, text="Dashboard", bg=c['background'],
                 fg=c['text_primary'], font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Real-time sales performance and revenue insights",
                 bg=c['background'], fg=c['text_secondary'],
                 font=("Segoe UI", 11)).pack(anchor="w", pady=(4, 0))

        # Smart Insights
        self.build_smart_insights()

        # KPI Cards
        self.build_kpi_section()

        # Charts row
        charts_frame = tk.Frame(self, bg=c['background'])
        charts_frame.pack(fill="both", expand=True, pady=(20, 0))

        # Revenue chart card
        self.revenue_card = self._make_card(charts_frame, "Revenue Trend")
        self.revenue_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Chart controls
        ctrl = tk.Frame(self.revenue_card, bg=c['surface'])
        ctrl.pack(fill="x", padx=20, pady=(0, 8))

        tk.Label(ctrl, text="Timeframe:", bg=c['surface'], fg=c['text_secondary'],
                 font=("Segoe UI", 9)).pack(side="right", padx=(0, 6))

        self.revenue_trend_var = tk.StringVar(value="Daily (Last 30 Days)")
        combo = ttk.Combobox(ctrl, textvariable=self.revenue_trend_var, state="readonly",
                             font=("Segoe UI", 9), width=22)
        combo['values'] = ["Daily (Last 30 Days)", "Monthly (Last 12 Months)", "Yearly (All Time)"]
        combo.bind("<<ComboboxSelected>>", self.update_revenue_chart)
        combo.pack(side="right")

        self.revenue_canvas_frame = tk.Frame(self.revenue_card, bg=c['surface'])
        self.revenue_canvas_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.update_revenue_chart()

        # Category chart card
        cat_card = self._make_card(charts_frame, "Sales by Category")
        cat_card.pack(side="right", fill="both", expand=True, padx=(10, 0))

        cat_canvas = tk.Frame(cat_card, bg=c['surface'])
        cat_canvas.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.create_category_chart(cat_canvas)

    def _make_card(self, parent, title):
        c = self.colors
        card = tk.Frame(parent, bg=c['surface'], bd=1, relief="solid",
                        highlightbackground=c['border'], highlightthickness=1)

        tk.Label(card, text=title, bg=c['surface'], fg=c['text_primary'],
                 font=("Segoe UI", 12, "bold"), anchor="w").pack(
            fill="x", padx=20, pady=(16, 8))

        return card

    # Smart Insights

    def build_smart_insights(self):
        c = self.colors
        insights = self._generate_insights()
        if not insights:
            return

        card = tk.Frame(self, bg=c['surface'], bd=1, relief="solid",
                        highlightbackground=c['border'], highlightthickness=1)
        card.pack(fill="x", pady=(0, 20))

        tk.Label(card, text="Smart Insights", bg=c['surface'], fg=c['text_primary'],
                 font=("Segoe UI", 12, "bold"), anchor="w").pack(
            fill="x", padx=20, pady=(16, 10))

        for insight in insights:
            row = tk.Frame(card, bg=c['surface'])
            row.pack(fill="x", padx=16, pady=(0, 10))

            type_colors = {
                'Insight': (c['accent'], '#ffffff'),
                'Tip': (c['success'], '#ffffff'),
                'Warning': (c['warning'], '#ffffff'),
            }
            bg_c, fg_c = type_colors.get(insight['type'], (c['accent'], '#ffffff'))

            badge = tk.Label(row, text="  " + insight['type'].upper() + "  ", bg=bg_c, fg=fg_c,
                             font=("Segoe UI", 8, "bold"))
            badge.pack(side="left", padx=(4, 12), pady=6)

            tk.Label(row, text=insight['text'], bg=c['surface'], fg=c['text_primary'],
                     font=("Segoe UI", 10), wraplength=750, justify="left",
                     anchor="w").pack(side="left", fill="x", expand=True, padx=(0, 8), pady=6)

    def _generate_insights(self):
        insights = []
        try:
            seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            today = datetime.now().strftime("%Y-%m-%d")
            sales_data = self.db.get_sales_data(date_range=[seven_days_ago, today])

            daily_totals = {}
            if sales_data:
                for sale in sales_data:
                    day_key = sale[8] + " (" + sale[6] + ")"
                    daily_totals[day_key] = daily_totals.get(day_key, 0) + sale[5]

            if len(daily_totals) > 1:
                best_key, best_val = max(daily_totals.items(), key=lambda x: x[1])
                slow_key, slow_val = min(daily_totals.items(), key=lambda x: x[1])
                if best_key != slow_key:
                    text = "This past week, {} was your best day with ${:.2f} in sales. {} was your slowest at ${:.2f}.".format(
                        best_key, best_val, slow_key, slow_val)
                    insights.append({"type": "Insight", "text": text})
        except Exception:
            pass

        try:
            hourly_data = self.db.get_hourly_sales_pattern()
            if hourly_data:
                peak = max(hourly_data, key=lambda x: x[1])
                hour = int(peak[0])
                ampm = "PM" if hour >= 12 else "AM"
                hour_str = str(hour % 12 or 12) + " " + ampm
                text = "Your peak hour for orders is around {}. Consider adding extra staff or pre-stocking popular items.".format(hour_str)
                insights.append({"type": "Tip", "text": text})
        except Exception:
            pass

        try:
            low_stock = self.db.get_inventory(low_stock_only=True)
            if low_stock:
                names = [item[1] for item in low_stock[:3]]
                more = "..." if len(low_stock) > 3 else ""
                text = "Low stock on: {}{}. Check your inventory!".format(", ".join(names), more)
                insights.append({"type": "Warning", "text": text})
        except Exception:
            pass

        return insights

    # KPI Cards

    def build_kpi_section(self):
        c = self.colors
        kpi_frame = tk.Frame(self, bg=c['background'])
        kpi_frame.pack(fill="x", pady=(0, 4))

        summary = self.db.get_sales_summary()
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday_sales = self.db.get_sales_data([yesterday, yesterday])
        yesterday_rev = sum(s[5] for s in yesterday_sales) if yesterday_sales else 0

        today_rev = summary['today']['revenue']
        change = ((today_rev - yesterday_rev) / yesterday_rev * 100) if yesterday_rev > 0 else 0

        cards = [
            ("Today's Revenue", "${:.2f}".format(today_rev),
             "{:+.1f}% vs yesterday".format(change),
             c['success'] if change >= 0 else c['error'],
             c['success_light'] if change >= 0 else c['error_light']),
            ("Orders Today", str(summary['today']['count']),
             "Active", c['success'], c['success_light']),
            ("Monthly Revenue", "${:.2f}".format(summary['month']['revenue']),
             "{} orders".format(summary['month']['count']), c['accent'], c['accent_light']),
            ("Top Selling Item", summary['popular_item'][:20],
             "Most popular", c['warning'], c['warning_light']),
        ]

        for i, (title, value, sub, sub_color, badge_bg) in enumerate(cards):
            card = tk.Frame(kpi_frame, bg=c['surface'], bd=1, relief="solid",
                            highlightbackground=c['border'], highlightthickness=1)
            card.pack(side="left", fill="both", expand=True,
                      padx=(0, 12) if i < len(cards) - 1 else (0, 0), pady=4)

            inner = tk.Frame(card, bg=c['surface'])
            inner.pack(fill="both", expand=True, padx=20, pady=18)

            tk.Label(inner, text=title, bg=c['surface'], fg=c['text_secondary'],
                     font=("Segoe UI", 10), anchor="w").pack(fill="x")

            tk.Label(inner, text=value, bg=c['surface'], fg=c['text_primary'],
                     font=("Segoe UI", 20, "bold"), anchor="w").pack(fill="x", pady=(6, 4))

            badge_frame = tk.Frame(inner, bg=c['surface'])
            badge_frame.pack(anchor="w")
            tk.Label(badge_frame, text=" " + sub + " ", bg=badge_bg, fg=sub_color,
                     font=("Segoe UI", 9)).pack(side="left")

    # Revenue Chart

    def update_revenue_chart(self, event=None):
        c = self.colors
        for w in self.revenue_canvas_frame.winfo_children():
            w.destroy()

        period = self.revenue_trend_var.get()
        fig = Figure(figsize=(6, 3), dpi=100)
        fig.patch.set_facecolor(c['surface'])
        ax = fig.add_subplot(111)
        ax.set_facecolor(c['surface'])
        data_found = False

        try:
            if period == "Daily (Last 30 Days)":
                daily = self.db.get_daily_sales_trend(30)
                if daily:
                    dates = [datetime.strptime(r[0], "%Y-%m-%d") for r in daily]
                    revs = [r[2] for r in daily]
                    ax.plot(dates, revs, color=c['accent'], linewidth=2.5, marker='o', markersize=4)
                    ax.fill_between(dates, revs, alpha=0.10, color=c['accent'])
                    fig.autofmt_xdate()
                    data_found = True

            elif period == "Monthly (Last 12 Months)":
                end = datetime.now()
                start = end - timedelta(days=365)
                raw = self.db.get_sales_data(
                    date_range=[start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")])
                agg = self._aggregate(raw, 'monthly')
                if agg:
                    dates = [datetime.strptime(d[0], "%Y-%m") for d in agg]
                    revs = [d[1] for d in agg]
                    ax.plot(dates, revs, color=c['accent'], linewidth=2.5, marker='o', markersize=4)
                    ax.fill_between(dates, revs, alpha=0.10, color=c['accent'])
                    fig.autofmt_xdate()
                    data_found = True

            elif period == "Yearly (All Time)":
                raw = self.db.get_sales_data(
                    date_range=["2000-01-01", datetime.now().strftime("%Y-%m-%d")])
                agg = self._aggregate(raw, 'yearly')
                if agg:
                    labels = [d[0] for d in agg]
                    revs = [d[1] for d in agg]
                    bars = ax.bar(labels, revs, color=c['accent'], width=0.5)
                    for bar in bars:
                        h = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width() / 2, h + h * 0.02,
                                "${:,.0f}".format(h), ha='center', va='bottom', fontsize=8,
                                color=c['text_secondary'])
                    data_found = True
        except Exception:
            data_found = False

        if not data_found:
            tk.Label(self.revenue_canvas_frame, text="No sales data for this period",
                     bg=c['surface'], fg=c['text_muted'],
                     font=("Segoe UI", 11)).pack(expand=True, pady=40)
            return

        ax.set_ylabel("Revenue ($)", fontsize=9, color=c['text_secondary'])
        ax.tick_params(axis='both', labelsize=8, colors=c['text_muted'])
        ax.grid(True, alpha=0.15, color=c['text_muted'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(c['border'])
        ax.spines['bottom'].set_color(c['border'])
        fig.tight_layout(pad=2)

        canvas = FigureCanvasTkAgg(fig, self.revenue_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _aggregate(self, raw_data, period):
        if not raw_data:
            return []
        fmt = "%Y-%m" if period == 'monthly' else "%Y" if period == 'yearly' else ""
        if not fmt:
            return []
        agg = {}
        for sale in raw_data:
            try:
                key = datetime.strptime(sale[6], "%Y-%m-%d").strftime(fmt)
                agg[key] = agg.get(key, 0) + sale[5]
            except (ValueError, TypeError, IndexError):
                continue
        return sorted(agg.items())

    # Category Chart

    def create_category_chart(self, parent):
        c = self.colors
        cat_data = self.db.get_category_performance()
        if not cat_data:
            tk.Label(parent, text="No category data available",
                     bg=c['surface'], fg=c['text_muted'],
                     font=("Segoe UI", 11)).pack(expand=True, pady=40)
            return

        fig = Figure(figsize=(6, 3), dpi=100)
        fig.patch.set_facecolor(c['surface'])
        ax = fig.add_subplot(111)
        ax.set_facecolor(c['surface'])

        categories = [r[0] for r in cat_data]
        revenues = [r[3] for r in cat_data]
        palette = ['#3b82f6', '#059669', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
        bars = ax.bar(categories, revenues, color=palette[:len(categories)], width=0.5)

        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + h * 0.02,
                    "${:,.0f}".format(h), ha='center', va='bottom', fontsize=8,
                    color=c['text_secondary'])

        ax.set_ylabel("Revenue ($)", fontsize=9, color=c['text_secondary'])
        ax.tick_params(axis='both', labelsize=8, colors=c['text_muted'])
        ax.grid(True, alpha=0.15, axis='y', color=c['text_muted'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(c['border'])
        ax.spines['bottom'].set_color(c['border'])
        fig.tight_layout(pad=2)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
