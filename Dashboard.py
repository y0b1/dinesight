import os
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from RestaurantDatabaseManager import RestaurantDatabaseManager

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def _load_tk_image(filename, size=None):
    """Load a PNG from assets/ and return a PhotoImage, or None on failure."""
    try:
        from PIL import Image as PILImage
        from PIL import ImageTk

        path = os.path.join(ASSETS_DIR, filename)
        if not os.path.exists(path):
            return None
        img = PILImage.open(path).convert("RGBA")
        if size:
            img = img.resize(size, PILImage.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


class Dashboard(tk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors["background"])
        self.db = RestaurantDatabaseManager()
        self.colors = colors
        self._images = []  # prevent garbage collection
        self.build_ui()

    def _keep(self, img):
        if img:
            self._images.append(img)
        return img

    def build_ui(self):
        c = self.colors

        # Banner image
        self._build_banner()

        # Smart Insights
        self.build_smart_insights()

        # KPI Cards (responsive grid)
        self.build_kpi_section()

        # Quick POS section
        self._build_pos_section()

        # Charts row
        charts_frame = tk.Frame(self, bg=c["background"])
        charts_frame.pack(fill="both", expand=True, pady=(20, 0))

        # Revenue chart card
        self.revenue_card = self._make_card(charts_frame, "Revenue Trend")
        self.revenue_card.pack(fill="both", expand=True, pady=(0, 10))

        ctrl = tk.Frame(self.revenue_card, bg=c["surface"])
        ctrl.pack(fill="x", padx=20, pady=(0, 8))

        tk.Label(
            ctrl,
            text="Timeframe:",
            bg=c["surface"],
            fg=c["text_secondary"],
            font=("Segoe UI", 9),
        ).pack(side="right", padx=(0, 6))

        self.revenue_trend_var = tk.StringVar(value="Daily (Last 30 Days)")
        combo = ttk.Combobox(
            ctrl,
            textvariable=self.revenue_trend_var,
            state="readonly",
            font=("Segoe UI", 9),
            width=22,
        )
        combo["values"] = [
            "Daily (Last 30 Days)",
            "Monthly (Last 12 Months)",
            "Yearly (All Time)",
        ]
        combo.bind("<<ComboboxSelected>>", self.update_revenue_chart)
        combo.pack(side="right")

        self.revenue_canvas_frame = tk.Frame(self.revenue_card, bg=c["surface"])
        self.revenue_canvas_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.update_revenue_chart()

        # Category chart card
        cat_card = self._make_card(self, "Sales by Category")
        cat_card.pack(fill="both", expand=True, pady=(0, 10))

        cat_canvas = tk.Frame(cat_card, bg=c["surface"])
        cat_canvas.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.create_category_chart(cat_canvas)

    # ── Banner ──────────────────────────────────────────────────

    def _build_banner(self):
        c = self.colors
        banner_img = self._keep(_load_tk_image("dashboard_banner.png"))

        if banner_img:
            banner = tk.Label(self, image=banner_img, bg=c["background"])
            banner.pack(fill="x", pady=(0, 20))
        else:
            # Fallback styled banner
            banner = tk.Frame(self, bg=c["accent"], height=120)
            banner.pack(fill="x", pady=(0, 20))
            banner.pack_propagate(False)
            inner = tk.Frame(banner, bg=c["accent"])
            inner.pack(fill="both", expand=True, padx=32, pady=20)
            tk.Label(
                inner,
                text="\U0001f37d  Welcome to DineSight",
                bg=c["accent"],
                fg="#ffffff",
                font=("Segoe UI", 20, "bold"),
            ).pack(anchor="w")
            tk.Label(
                inner,
                text="Your restaurant command center",
                bg=c["accent"],
                fg="#c7d2fe",
                font=("Segoe UI", 11),
            ).pack(anchor="w", pady=(4, 0))

    def _make_card(self, parent, title):
        c = self.colors
        card = tk.Frame(
            parent,
            bg=c["surface"],
            bd=1,
            relief="solid",
            highlightbackground=c["border"],
            highlightthickness=1,
        )

        tk.Label(
            card,
            text=title,
            bg=c["surface"],
            fg=c["text_primary"],
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        ).pack(fill="x", padx=20, pady=(16, 8))

        return card

    # ── Smart Insights ──────────────────────────────────────────

    def build_smart_insights(self):
        c = self.colors
        insights = self._generate_insights()
        if not insights:
            return

        card = tk.Frame(
            self,
            bg=c["surface"],
            bd=1,
            relief="solid",
            highlightbackground=c["border"],
            highlightthickness=1,
        )
        card.pack(fill="x", pady=(0, 20))

        tk.Label(
            card,
            text="\U0001f4a1  Smart Insights",
            bg=c["surface"],
            fg=c["text_primary"],
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        ).pack(fill="x", padx=20, pady=(16, 10))

        for insight in insights:
            row = tk.Frame(card, bg=c["surface"])
            row.pack(fill="x", padx=16, pady=(0, 10))

            type_colors = {
                "Insight": (c["accent"], "#ffffff"),
                "Tip": (c["success"], "#ffffff"),
                "Warning": (c["warning"], "#ffffff"),
            }
            bg_c, fg_c = type_colors.get(insight["type"], (c["accent"], "#ffffff"))

            badge = tk.Label(
                row,
                text="  " + insight["type"].upper() + "  ",
                bg=bg_c,
                fg=fg_c,
                font=("Segoe UI", 8, "bold"),
            )
            badge.pack(side="left", padx=(4, 12), pady=6)

            tk.Label(
                row,
                text=insight["text"],
                bg=c["surface"],
                fg=c["text_primary"],
                font=("Segoe UI", 10),
                wraplength=700,
                justify="left",
                anchor="w",
            ).pack(side="left", fill="x", expand=True, padx=(0, 8), pady=6)

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
                        best_key, best_val, slow_key, slow_val
                    )
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
                text = "Your peak hour for orders is around {}. Consider adding extra staff or pre-stocking popular items.".format(
                    hour_str
                )
                insights.append({"type": "Tip", "text": text})
        except Exception:
            pass

        try:
            low_stock = self.db.get_inventory(low_stock_only=True)
            if low_stock:
                names = [item[1] for item in low_stock[:3]]
                more = "..." if len(low_stock) > 3 else ""
                text = "Low stock on: {}{}. Check your inventory!".format(
                    ", ".join(names), more
                )
                insights.append({"type": "Warning", "text": text})
        except Exception:
            pass

        return insights

    # ── KPI Cards ───────────────────────────────────────────────

    def build_kpi_section(self):
        c = self.colors
        kpi_frame = tk.Frame(self, bg=c["background"])
        kpi_frame.pack(fill="x", pady=(0, 4))

        summary = self.db.get_sales_summary()
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday_sales = self.db.get_sales_data([yesterday, yesterday])
        yesterday_rev = sum(s[5] for s in yesterday_sales) if yesterday_sales else 0

        today_rev = summary["today"]["revenue"]
        change = (
            ((today_rev - yesterday_rev) / yesterday_rev * 100)
            if yesterday_rev > 0
            else 0
        )

        stat_icons = [
            "revenue_icon.png",
            "orders_icon.png",
            "monthly_icon.png",
            "top_item_icon.png",
        ]

        cards_data = [
            (
                "Today's Revenue",
                "${:.2f}".format(today_rev),
                "{:+.1f}% vs yesterday".format(change),
                c["success"] if change >= 0 else c["error"],
                c["success_light"] if change >= 0 else c["error_light"],
            ),
            (
                "Orders Today",
                str(summary["today"]["count"]),
                "Active",
                c["success"],
                c["success_light"],
            ),
            (
                "Monthly Revenue",
                "${:.2f}".format(summary["month"]["revenue"]),
                "{} orders".format(summary["month"]["count"]),
                c["accent"],
                c["accent_light"],
            ),
            (
                "Top Selling Item",
                summary["popular_item"][:20],
                "Most popular",
                c["warning"],
                c["warning_light"],
            ),
        ]

        # Use grid for responsive wrapping
        kpi_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="kpi")

        for i, (title, value, sub, sub_color, badge_bg) in enumerate(cards_data):
            card = tk.Frame(
                kpi_frame,
                bg=c["surface"],
                bd=1,
                relief="solid",
                highlightbackground=c["border"],
                highlightthickness=1,
            )
            card.grid(
                row=0,
                column=i,
                sticky="nsew",
                padx=(0, 12) if i < 3 else (0, 0),
                pady=4,
            )

            inner = tk.Frame(card, bg=c["surface"])
            inner.pack(fill="both", expand=True, padx=16, pady=14)

            # Top row: icon + title
            top_row = tk.Frame(inner, bg=c["surface"])
            top_row.pack(fill="x")

            icon = self._keep(_load_tk_image(stat_icons[i], size=(32, 32)))
            if icon:
                tk.Label(top_row, image=icon, bg=c["surface"]).pack(
                    side="left", padx=(0, 10)
                )

            tk.Label(
                top_row,
                text=title,
                bg=c["surface"],
                fg=c["text_secondary"],
                font=("Segoe UI", 9),
                anchor="w",
            ).pack(side="left", fill="x")

            tk.Label(
                inner,
                text=value,
                bg=c["surface"],
                fg=c["text_primary"],
                font=("Segoe UI", 18, "bold"),
                anchor="w",
            ).pack(fill="x", pady=(6, 4))

            badge_frame = tk.Frame(inner, bg=c["surface"])
            badge_frame.pack(anchor="w")
            tk.Label(
                badge_frame,
                text=" " + sub + " ",
                bg=badge_bg,
                fg=sub_color,
                font=("Segoe UI", 9),
            ).pack(side="left")

    # ── Quick POS ───────────────────────────────────────────────

    def _build_pos_section(self):
        c = self.colors

        pos_card = tk.Frame(
            self,
            bg=c["surface"],
            bd=1,
            relief="solid",
            highlightbackground=c["border"],
            highlightthickness=1,
        )
        pos_card.pack(fill="x", pady=(16, 0))

        # Header
        hdr = tk.Frame(pos_card, bg=c["surface"])
        hdr.pack(fill="x", padx=20, pady=(16, 12))

        pos_icon = self._keep(_load_tk_image("pos_icon.png", size=(36, 36)))
        if pos_icon:
            tk.Label(hdr, image=pos_icon, bg=c["surface"]).pack(
                side="left", padx=(0, 12)
            )

        hdr_text = tk.Frame(hdr, bg=c["surface"])
        hdr_text.pack(side="left", fill="x", expand=True)
        tk.Label(
            hdr_text,
            text="Quick POS",
            bg=c["surface"],
            fg=c["text_primary"],
            font=("Segoe UI", 14, "bold"),
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            hdr_text,
            text="Tap an item to add to the order",
            bg=c["surface"],
            fg=c["text_secondary"],
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(fill="x")

        # Category filter
        filter_frame = tk.Frame(pos_card, bg=c["surface"])
        filter_frame.pack(fill="x", padx=20, pady=(0, 8))

        tk.Label(
            filter_frame,
            text="Category:",
            bg=c["surface"],
            fg=c["text_secondary"],
            font=("Segoe UI", 9),
        ).pack(side="left", padx=(0, 8))

        self._pos_cat_var = tk.StringVar(value="All")
        cat_combo = ttk.Combobox(
            filter_frame,
            textvariable=self._pos_cat_var,
            state="readonly",
            font=("Segoe UI", 9),
            width=16,
        )
        cat_combo["values"] = [
            "All",
            "Appetizer",
            "Main Course",
            "Dessert",
            "Beverage",
            "Special",
        ]
        cat_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_pos_grid())
        cat_combo.pack(side="left")

        # Content: left = menu grid, right = order summary
        content = tk.Frame(pos_card, bg=c["surface"])
        content.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # Menu grid (scrollable)
        left = tk.Frame(content, bg=c["surface"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self._pos_grid_canvas = tk.Canvas(
            left, bg=c["surface"], highlightthickness=0, height=260
        )
        self._pos_grid_frame = tk.Frame(self._pos_grid_canvas, bg=c["surface"])
        self._pos_grid_canvas.create_window(
            (0, 0), window=self._pos_grid_frame, anchor="nw", tags="inner"
        )
        self._pos_grid_frame.bind(
            "<Configure>",
            lambda e: self._pos_grid_canvas.configure(
                scrollregion=self._pos_grid_canvas.bbox("all")
            ),
        )
        self._pos_grid_canvas.bind(
            "<Configure>",
            lambda e: self._pos_grid_canvas.itemconfig("inner", width=e.width),
        )
        self._pos_grid_canvas.pack(fill="both", expand=True)

        # Mouse wheel scroll for POS grid
        def _pos_scroll(event):
            self._pos_grid_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self._pos_grid_canvas.bind("<MouseWheel>", _pos_scroll)
        self._pos_grid_frame.bind("<MouseWheel>", _pos_scroll)

        # Order summary (right side)
        right = tk.Frame(
            content,
            bg=c["surface_alt"],
            width=280,
            bd=1,
            relief="solid",
            highlightbackground=c["border"],
            highlightthickness=1,
        )
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        tk.Label(
            right,
            text="\U0001f4cb  Current Order",
            bg=c["surface_alt"],
            fg=c["text_primary"],
            font=("Segoe UI", 11, "bold"),
        ).pack(fill="x", padx=12, pady=(12, 8))

        self._order_list_frame = tk.Frame(right, bg=c["surface_alt"])
        self._order_list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        self._order_empty_label = tk.Label(
            self._order_list_frame,
            text="No items added yet\nTap items on the left",
            bg=c["surface_alt"],
            fg=c["text_muted"],
            font=("Segoe UI", 9),
            justify="center",
        )
        self._order_empty_label.pack(expand=True)

        # Divider
        tk.Frame(right, bg=c["border"], height=1).pack(fill="x", padx=12)

        # Total
        total_frame = tk.Frame(right, bg=c["surface_alt"])
        total_frame.pack(fill="x", padx=12, pady=(8, 4))

        tk.Label(
            total_frame,
            text="Total:",
            bg=c["surface_alt"],
            fg=c["text_primary"],
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")
        self._pos_total_var = tk.StringVar(value="$0.00")
        tk.Label(
            total_frame,
            textvariable=self._pos_total_var,
            bg=c["surface_alt"],
            fg=c["accent"],
            font=("Segoe UI", 16, "bold"),
        ).pack(side="right")

        # Action buttons
        btn_frame = tk.Frame(right, bg=c["surface_alt"])
        btn_frame.pack(fill="x", padx=12, pady=(4, 12))

        self._pos_checkout_btn = tk.Button(
            btn_frame,
            text="\u2713  Complete Sale",
            bg=c["success"],
            fg="#ffffff",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            padx=16,
            pady=10,
            cursor="hand2",
            relief="flat",
            activebackground="#047857",
            activeforeground="#ffffff",
            command=self._pos_checkout,
        )
        self._pos_checkout_btn.pack(fill="x", pady=(0, 6))

        clear_btn = tk.Button(
            btn_frame,
            text="Clear Order",
            bg=c["surface"],
            fg=c["text_secondary"],
            font=("Segoe UI", 9),
            bd=1,
            padx=12,
            pady=6,
            cursor="hand2",
            relief="solid",
            highlightbackground=c["border"],
            command=self._pos_clear_order,
        )
        clear_btn.pack(fill="x")

        # Internal order state
        self._pos_order = {}  # {item_id: {"name", "category", "price", "qty"}}
        self._refresh_pos_grid()

    def _refresh_pos_grid(self):
        c = self.colors
        for w in self._pos_grid_frame.winfo_children():
            w.destroy()

        items = self.db.get_menu_items(available_only=True)
        cat_filter = self._pos_cat_var.get()
        if cat_filter != "All":
            items = [i for i in items if i[2] == cat_filter]

        cat_colors = {
            "Appetizer": "#f59e0b",
            "Main Course": "#ef4444",
            "Dessert": "#ec4899",
            "Beverage": "#3b82f6",
            "Special": "#8b5cf6",
        }
        cat_icons = {
            "Appetizer": "cat_appetizer.png",
            "Main Course": "cat_main.png",
            "Dessert": "cat_dessert.png",
            "Beverage": "cat_beverage.png",
            "Special": "cat_special.png",
        }

        if not items:
            empty_img = self._keep(_load_tk_image("empty_plate.png", size=(100, 100)))
            empty_frame = tk.Frame(self._pos_grid_frame, bg=c["surface"])
            empty_frame.pack(expand=True, pady=30)
            if empty_img:
                tk.Label(empty_frame, image=empty_img, bg=c["surface"]).pack()
            tk.Label(
                empty_frame,
                text="No available items",
                bg=c["surface"],
                fg=c["text_muted"],
                font=("Segoe UI", 11),
            ).pack(pady=(8, 0))
            return

        cols = 3
        for idx, item in enumerate(items):
            row_num = idx // cols
            col_num = idx % cols

            item_id, name, category, desc, price = (
                item[0],
                item[1],
                item[2],
                item[3],
                item[4],
            )
            accent = cat_colors.get(category, c["accent"])

            btn_frame = tk.Frame(
                self._pos_grid_frame,
                bg=c["surface"],
                bd=1,
                relief="solid",
                highlightbackground=c["border"],
                highlightthickness=1,
                cursor="hand2",
            )
            btn_frame.grid(row=row_num, column=col_num, padx=4, pady=4, sticky="nsew")
            self._pos_grid_frame.columnconfigure(col_num, weight=1, uniform="pos")

            # Color accent at top
            tk.Frame(btn_frame, bg=accent, height=4).pack(fill="x")

            inner = tk.Frame(btn_frame, bg=c["surface"])
            inner.pack(fill="both", expand=True, padx=10, pady=8)

            # Category icon
            icon = self._keep(
                _load_tk_image(cat_icons.get(category, ""), size=(32, 32))
            )
            if icon:
                tk.Label(inner, image=icon, bg=c["surface"]).pack(anchor="w")

            tk.Label(
                inner,
                text=name[:22],
                bg=c["surface"],
                fg=c["text_primary"],
                font=("Segoe UI", 10, "bold"),
                anchor="w",
            ).pack(fill="x", pady=(4, 0))

            if category:
                tk.Label(
                    inner,
                    text=category,
                    bg=c["surface"],
                    fg=accent,
                    font=("Segoe UI", 8),
                    anchor="w",
                ).pack(fill="x")

            tk.Label(
                inner,
                text="${:.2f}".format(price),
                bg=c["surface"],
                fg=c["accent"],
                font=("Segoe UI", 12, "bold"),
                anchor="w",
            ).pack(fill="x", pady=(4, 0))

            # Qty badge (if in order)
            qty = self._pos_order.get(item_id, {}).get("qty", 0)
            if qty > 0:
                badge = tk.Label(
                    btn_frame,
                    text=" {} ".format(qty),
                    bg=c["accent"],
                    fg="#ffffff",
                    font=("Segoe UI", 9, "bold"),
                )
                badge.place(relx=1.0, rely=0.0, anchor="ne", x=-4, y=8)

            # Click to add
            def _on_click(e, iid=item_id, nm=name, cat=category, pr=price):
                self._pos_add_item(iid, nm, cat, pr)

            for widget in [btn_frame, inner] + inner.winfo_children():
                widget.bind("<Button-1>", _on_click)

            # Hover effect
            def _hover_in(e, f=btn_frame):
                f.configure(highlightbackground=c["accent"], highlightthickness=2)

            def _hover_out(e, f=btn_frame):
                f.configure(highlightbackground=c["border"], highlightthickness=1)

            btn_frame.bind("<Enter>", _hover_in)
            btn_frame.bind("<Leave>", _hover_out)

    def _pos_add_item(self, item_id, name, category, price):
        if item_id in self._pos_order:
            self._pos_order[item_id]["qty"] += 1
        else:
            self._pos_order[item_id] = {
                "name": name,
                "category": category,
                "price": price,
                "qty": 1,
            }
        self._refresh_order_display()
        self._refresh_pos_grid()

    def _pos_remove_item(self, item_id):
        if item_id in self._pos_order:
            self._pos_order[item_id]["qty"] -= 1
            if self._pos_order[item_id]["qty"] <= 0:
                del self._pos_order[item_id]
        self._refresh_order_display()
        self._refresh_pos_grid()

    def _refresh_order_display(self):
        c = self.colors
        for w in self._order_list_frame.winfo_children():
            w.destroy()

        if not self._pos_order:
            self._order_empty_label = tk.Label(
                self._order_list_frame,
                text="No items added yet\nTap items on the left",
                bg=c["surface_alt"],
                fg=c["text_muted"],
                font=("Segoe UI", 9),
                justify="center",
            )
            self._order_empty_label.pack(expand=True)
            self._pos_total_var.set("$0.00")
            return

        total = 0.0
        for item_id, info in self._pos_order.items():
            line_total = info["price"] * info["qty"]
            total += line_total

            row = tk.Frame(self._order_list_frame, bg=c["surface_alt"])
            row.pack(fill="x", pady=3)

            # Item info
            info_frame = tk.Frame(row, bg=c["surface_alt"])
            info_frame.pack(side="left", fill="x", expand=True)

            tk.Label(
                info_frame,
                text=info["name"][:18],
                bg=c["surface_alt"],
                fg=c["text_primary"],
                font=("Segoe UI", 9, "bold"),
                anchor="w",
            ).pack(fill="x")
            tk.Label(
                info_frame,
                text="${:.2f} x {}".format(info["price"], info["qty"]),
                bg=c["surface_alt"],
                fg=c["text_muted"],
                font=("Segoe UI", 8),
                anchor="w",
            ).pack(fill="x")

            # Right side: line total + remove
            right_col = tk.Frame(row, bg=c["surface_alt"])
            right_col.pack(side="right")

            tk.Label(
                right_col,
                text="${:.2f}".format(line_total),
                bg=c["surface_alt"],
                fg=c["text_primary"],
                font=("Segoe UI", 9, "bold"),
            ).pack(side="left", padx=(0, 6))

            # +/- buttons
            minus_btn = tk.Button(
                right_col,
                text="-",
                bg=c["error_light"],
                fg=c["error"],
                font=("Segoe UI", 8, "bold"),
                bd=0,
                width=2,
                height=1,
                cursor="hand2",
                command=lambda iid=item_id: self._pos_remove_item(iid),
            )
            minus_btn.pack(side="left", padx=(0, 2))

            plus_btn = tk.Button(
                right_col,
                text="+",
                bg=c["success_light"],
                fg=c["success"],
                font=("Segoe UI", 8, "bold"),
                bd=0,
                width=2,
                height=1,
                cursor="hand2",
                command=lambda iid=item_id,
                nm=info["name"],
                cat=info["category"],
                pr=info["price"]: self._pos_add_item(iid, nm, cat, pr),
            )
            plus_btn.pack(side="left")

        self._pos_total_var.set("${:.2f}".format(total))

    def _pos_checkout(self):
        if not self._pos_order:
            messagebox.showwarning("Empty Order", "Add items to the order first.")
            return

        # Validate stock for all items
        for item_id, info in self._pos_order.items():
            if not self.db.check_stock_for_sale(item_id, info["qty"]):
                messagebox.showerror(
                    "Stock Error", "Not enough stock for '{}'.".format(info["name"])
                )
                return

        # Record each sale
        errors = []
        for item_id, info in self._pos_order.items():
            line_total = info["price"] * info["qty"]
            try:
                self.db.record_sale(
                    menu_item_id=item_id,
                    item_name=info["name"],
                    category=info["category"],
                    quantity=info["qty"],
                    unit_price=info["price"],
                    total_amount=line_total,
                )
            except Exception as e:
                errors.append(str(e))

        if errors:
            messagebox.showerror("Error", "Some sales failed:\n" + "\n".join(errors))
        else:
            total = sum(i["price"] * i["qty"] for i in self._pos_order.values())
            items_count = sum(i["qty"] for i in self._pos_order.values())
            messagebox.showinfo(
                "Sale Complete",
                "\u2713 Order completed!\n\nItems: {}\nTotal: ${:.2f}".format(
                    items_count, total
                ),
            )

        self._pos_clear_order()

    def _pos_clear_order(self):
        self._pos_order.clear()
        self._refresh_order_display()
        self._refresh_pos_grid()

    # ── Revenue Chart ───────────────────────────────────────────

    def update_revenue_chart(self, event=None):
        c = self.colors
        for w in self.revenue_canvas_frame.winfo_children():
            w.destroy()

        period = self.revenue_trend_var.get()
        fig = Figure(figsize=(6, 2.8), dpi=100)
        fig.patch.set_facecolor(c["surface"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(c["surface"])
        data_found = False

        try:
            if period == "Daily (Last 30 Days)":
                daily = self.db.get_daily_sales_trend(30)
                if daily:
                    dates = [datetime.strptime(r[0], "%Y-%m-%d") for r in daily]
                    revs = [r[2] for r in daily]
                    ax.plot(
                        dates,
                        revs,
                        color=c["accent"],
                        linewidth=2.5,
                        marker="o",
                        markersize=4,
                    )
                    ax.fill_between(dates, revs, alpha=0.10, color=c["accent"])
                    fig.autofmt_xdate()
                    data_found = True

            elif period == "Monthly (Last 12 Months)":
                end = datetime.now()
                start = end - timedelta(days=365)
                raw = self.db.get_sales_data(
                    date_range=[start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")]
                )
                agg = self._aggregate(raw, "monthly")
                if agg:
                    dates = [datetime.strptime(d[0], "%Y-%m") for d in agg]
                    revs = [d[1] for d in agg]
                    ax.plot(
                        dates,
                        revs,
                        color=c["accent"],
                        linewidth=2.5,
                        marker="o",
                        markersize=4,
                    )
                    ax.fill_between(dates, revs, alpha=0.10, color=c["accent"])
                    fig.autofmt_xdate()
                    data_found = True

            elif period == "Yearly (All Time)":
                raw = self.db.get_sales_data(
                    date_range=["2000-01-01", datetime.now().strftime("%Y-%m-%d")]
                )
                agg = self._aggregate(raw, "yearly")
                if agg:
                    labels = [d[0] for d in agg]
                    revs = [d[1] for d in agg]
                    bars = ax.bar(labels, revs, color=c["accent"], width=0.5)
                    for bar in bars:
                        h = bar.get_height()
                        ax.text(
                            bar.get_x() + bar.get_width() / 2,
                            h + h * 0.02,
                            "${:,.0f}".format(h),
                            ha="center",
                            va="bottom",
                            fontsize=8,
                            color=c["text_secondary"],
                        )
                    data_found = True
        except Exception:
            data_found = False

        if not data_found:
            empty_img = self._keep(_load_tk_image("empty_plate.png", size=(80, 80)))
            empty_frame = tk.Frame(self.revenue_canvas_frame, bg=c["surface"])
            empty_frame.pack(expand=True, pady=30)
            if empty_img:
                tk.Label(empty_frame, image=empty_img, bg=c["surface"]).pack()
            tk.Label(
                empty_frame,
                text="No sales data for this period",
                bg=c["surface"],
                fg=c["text_muted"],
                font=("Segoe UI", 11),
            ).pack(pady=(8, 0))
            return

        ax.set_ylabel("Revenue ($)", fontsize=9, color=c["text_secondary"])
        ax.tick_params(axis="both", labelsize=8, colors=c["text_muted"])
        ax.grid(True, alpha=0.15, color=c["text_muted"])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(c["border"])
        ax.spines["bottom"].set_color(c["border"])
        fig.tight_layout(pad=2)

        canvas = FigureCanvasTkAgg(fig, self.revenue_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _aggregate(self, raw_data, period):
        if not raw_data:
            return []
        fmt = "%Y-%m" if period == "monthly" else "%Y" if period == "yearly" else ""
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

    # ── Category Chart ──────────────────────────────────────────

    def create_category_chart(self, parent):
        c = self.colors
        cat_data = self.db.get_category_performance()
        if not cat_data:
            empty_img = self._keep(_load_tk_image("empty_plate.png", size=(80, 80)))
            empty_frame = tk.Frame(parent, bg=c["surface"])
            empty_frame.pack(expand=True, pady=30)
            if empty_img:
                tk.Label(empty_frame, image=empty_img, bg=c["surface"]).pack()
            tk.Label(
                empty_frame,
                text="No category data available",
                bg=c["surface"],
                fg=c["text_muted"],
                font=("Segoe UI", 11),
            ).pack(pady=(8, 0))
            return

        fig = Figure(figsize=(6, 2.8), dpi=100)
        fig.patch.set_facecolor(c["surface"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(c["surface"])

        categories = [r[0] for r in cat_data]
        revenues = [r[3] for r in cat_data]
        palette = ["#3b82f6", "#059669", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]
        bars = ax.bar(categories, revenues, color=palette[: len(categories)], width=0.5)

        for bar in bars:
            h = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + h * 0.02,
                "${:,.0f}".format(h),
                ha="center",
                va="bottom",
                fontsize=8,
                color=c["text_secondary"],
            )

        ax.set_ylabel("Revenue ($)", fontsize=9, color=c["text_secondary"])
        ax.tick_params(axis="both", labelsize=8, colors=c["text_muted"])
        ax.grid(True, alpha=0.15, axis="y", color=c["text_muted"])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(c["border"])
        ax.spines["bottom"].set_color(c["border"])
        fig.tight_layout(pad=2)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
