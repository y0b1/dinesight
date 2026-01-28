import tkinter as tk
from tkinter import ttk, messagebox
from RestaurantDatabaseManager import RestaurantDatabaseManager


class SalesLogger(tk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors['background'])
        self.db = RestaurantDatabaseManager()
        self.colors = colors

        self.selected_item_id = None
        self.selected_item_name = None
        self.selected_item_category = None
        self.selected_item_price = None

        self.build_ui()
        self.refresh_menu_list()
        self.refresh_sales_history()

    def build_ui(self):
        c = self.colors

        # Header
        header = tk.Frame(self, bg=c['background'])
        header.pack(fill="x", pady=(0, 24))

        tk.Label(header, text="Sales Logger (POS)", bg=c['background'],
                 fg=c['text_primary'], font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Log daily sales to power your analytics",
                 bg=c['background'], fg=c['text_secondary'],
                 font=("Segoe UI", 11)).pack(anchor="w", pady=(4, 0))

        content = tk.Frame(self, bg=c['background'])
        content.pack(fill="both", expand=True)

        # Left panel - menu + sales history
        left = tk.Frame(content, bg=c['background'])
        left.pack(side="left", fill="both", expand=True, padx=(0, 20))

        self.build_menu_section(left)
        self.build_sales_history(left)

        # Right panel - log form
        right = tk.Frame(content, bg=c['background'], width=340)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        self.build_logging_form(right)

    # Menu Items Section

    def build_menu_section(self, parent):
        c = self.colors
        card = tk.Frame(parent, bg=c['surface'], bd=1, relief="solid",
                        highlightbackground=c['border'], highlightthickness=1)
        card.pack(fill="both", expand=True, pady=(0, 12))

        tk.Label(card, text="Available Menu Items", bg=c['surface'], fg=c['text_primary'],
                 font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x", padx=20, pady=(16, 10))

        # Search
        search_frame = tk.Frame(card, bg=c['surface'])
        search_frame.pack(fill="x", padx=20, pady=(0, 8))

        self.menu_search_var = tk.StringVar()
        self.menu_search_var.trace_add("write", lambda *_: self.filter_menu())
        ttk.Entry(search_frame, textvariable=self.menu_search_var,
                  font=("Segoe UI", 10)).pack(side="left", fill="x", expand=True)
        tk.Label(search_frame, text="Search items", bg=c['surface'], fg=c['text_muted'],
                 font=("Segoe UI", 9)).pack(side="right", padx=(8, 0))

        # Treeview
        tree_frame = tk.Frame(card, bg=c['surface'])
        tree_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.menu_tree = ttk.Treeview(
            tree_frame, columns=("id", "Name", "Category", "Price"),
            show="headings", height=8
        )
        self.menu_tree.heading("id", text="ID")
        self.menu_tree.heading("Name", text="Name")
        self.menu_tree.heading("Category", text="Category")
        self.menu_tree.heading("Price", text="Price ($)")

        self.menu_tree.column("id", width=0, stretch=False)
        self.menu_tree.column("Name", width=200, anchor="w")
        self.menu_tree.column("Category", width=120, anchor="w")
        self.menu_tree.column("Price", width=80, anchor="e")

        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.menu_tree.yview)
        self.menu_tree.configure(yscrollcommand=v_scroll.set)
        self.menu_tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

        self.menu_tree.bind("<<TreeviewSelect>>", self.on_item_select)

    # Sales History

    def build_sales_history(self, parent):
        c = self.colors
        card = tk.Frame(parent, bg=c['surface'], bd=1, relief="solid",
                        highlightbackground=c['border'], highlightthickness=1)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Recent Sales", bg=c['surface'], fg=c['text_primary'],
                 font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x", padx=20, pady=(16, 10))

        tree_frame = tk.Frame(card, bg=c['surface'])
        tree_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.sales_tree = ttk.Treeview(
            tree_frame,
            columns=("id", "Item", "Qty", "Total", "Date", "Time"),
            show="headings", height=8
        )
        self.sales_tree.heading("id", text="ID")
        self.sales_tree.heading("Item", text="Item")
        self.sales_tree.heading("Qty", text="Qty")
        self.sales_tree.heading("Total", text="Total ($)")
        self.sales_tree.heading("Date", text="Date")
        self.sales_tree.heading("Time", text="Time")

        self.sales_tree.column("id", width=0, stretch=False)
        self.sales_tree.column("Item", width=160, anchor="w")
        self.sales_tree.column("Qty", width=50, anchor="center")
        self.sales_tree.column("Total", width=80, anchor="e")
        self.sales_tree.column("Date", width=95, anchor="center")
        self.sales_tree.column("Time", width=70, anchor="center")

        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=v_scroll.set)
        self.sales_tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

    # Logging Form

    def build_logging_form(self, parent):
        c = self.colors
        card = tk.Frame(parent, bg=c['surface'], bd=1, relief="solid",
                        highlightbackground=c['border'], highlightthickness=1)
        card.pack(fill="x")

        tk.Label(card, text="Log a Sale", bg=c['surface'], fg=c['text_primary'],
                 font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x", padx=20, pady=(16, 16))

        form = tk.Frame(card, bg=c['surface'])
        form.pack(fill="x", padx=20, pady=(0, 20))

        self.item_name_var = tk.StringVar(value="No item selected")
        self.item_price_var = tk.StringVar(value="--")
        self.quantity_var = tk.StringVar(value="1")

        # Selected item display
        tk.Label(form, text="Selected Item", bg=c['surface'], fg=c['text_secondary'],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))

        sel_frame = tk.Frame(form, bg=c['accent_light'])
        sel_frame.pack(fill="x", pady=(0, 14))

        self.sel_name_label = tk.Label(sel_frame, textvariable=self.item_name_var,
                                       bg=c['accent_light'], fg=c['accent'],
                                       font=("Segoe UI", 12, "bold"), anchor="w")
        self.sel_name_label.pack(fill="x", padx=12, pady=(10, 2))

        self.sel_price_label = tk.Label(sel_frame, textvariable=self.item_price_var,
                                        bg=c['accent_light'], fg=c['text_secondary'],
                                        font=("Segoe UI", 10), anchor="w")
        self.sel_price_label.pack(fill="x", padx=12, pady=(0, 10))

        # Quantity
        tk.Label(form, text="Quantity", bg=c['surface'], fg=c['text_secondary'],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))

        qty_frame = tk.Frame(form, bg=c['surface'])
        qty_frame.pack(fill="x", pady=(0, 20))

        ttk.Button(qty_frame, text="-", width=3,
                   command=self.decrement_qty).pack(side="left", padx=(0, 4))
        ttk.Entry(qty_frame, textvariable=self.quantity_var,
                  font=("Segoe UI", 12, "bold"), width=6,
                  justify="center").pack(side="left", padx=(0, 4))
        ttk.Button(qty_frame, text="+", width=3,
                   command=self.increment_qty).pack(side="left")

        # Buttons
        ttk.Button(form, text="Log Sale", command=self.log_sale,
                   style="Accent.TButton").pack(fill="x", pady=(0, 8))
        ttk.Button(form, text="Clear", command=self.clear_form).pack(fill="x")

    # Data Operations

    def refresh_menu_list(self):
        self.clear_form()
        for row in self.menu_tree.get_children():
            self.menu_tree.delete(row)

        items = self.db.get_menu_items(available_only=True)
        for item in items:
            self.menu_tree.insert("", "end", values=(
                item[0], item[1], item[2], "${:.2f}".format(item[4])
            ))

    def filter_menu(self):
        query = self.menu_search_var.get().lower()
        for row in self.menu_tree.get_children():
            self.menu_tree.delete(row)

        items = self.db.get_menu_items(available_only=True)
        for item in items:
            if query and query not in item[1].lower() and query not in (item[2] or "").lower():
                continue
            self.menu_tree.insert("", "end", values=(
                item[0], item[1], item[2], "${:.2f}".format(item[4])
            ))

    def refresh_sales_history(self):
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)

        sales = self.db.get_sales_data()
        for sale in sales:
            self.sales_tree.insert("", "end", values=(
                sale[0], sale[1], sale[3],
                "${:.2f}".format(sale[5]), sale[6], sale[7]
            ))

    def on_item_select(self, event):
        sel = self.menu_tree.selection()
        if sel:
            data = self.menu_tree.item(sel[0])['values']
            self.selected_item_id = int(data[0])
            self.selected_item_name = data[1]
            self.selected_item_category = data[2]
            self.selected_item_price = float(str(data[3]).strip('$'))

            self.item_name_var.set(self.selected_item_name)
            self.item_price_var.set("${:.2f} per unit".format(self.selected_item_price))
            self.quantity_var.set("1")

    def increment_qty(self):
        try:
            q = int(self.quantity_var.get())
            self.quantity_var.set(str(q + 1))
        except ValueError:
            self.quantity_var.set("1")

    def decrement_qty(self):
        try:
            q = int(self.quantity_var.get())
            if q > 1:
                self.quantity_var.set(str(q - 1))
        except ValueError:
            self.quantity_var.set("1")

    def log_sale(self):
        if not self.selected_item_id:
            messagebox.showwarning("No Item", "Select an item from the menu first.")
            return

        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Enter a valid positive number.")
            return

        if not self.db.check_stock_for_sale(self.selected_item_id, quantity):
            messagebox.showerror("Out of Stock",
                                 "Not enough ingredients in inventory for this sale.")
            return

        total = self.selected_item_price * quantity

        try:
            self.db.record_sale(
                menu_item_id=self.selected_item_id,
                item_name=self.selected_item_name,
                category=self.selected_item_category,
                quantity=quantity,
                unit_price=self.selected_item_price,
                total_amount=total
            )
            messagebox.showinfo("Sale Logged",
                                "Logged: {} x{}\nTotal: ${:.2f}".format(
                                    self.selected_item_name, quantity, total))
            self.refresh_menu_list()
            self.refresh_sales_history()
        except Exception as e:
            messagebox.showerror("Error", "Failed to log sale: {}".format(e))

    def clear_form(self):
        self.selected_item_id = None
        self.selected_item_name = None
        self.selected_item_category = None
        self.selected_item_price = None

        self.item_name_var.set("No item selected")
        self.item_price_var.set("--")
        self.quantity_var.set("1")

        if self.menu_tree.selection():
            self.menu_tree.selection_remove(self.menu_tree.selection()[0])
