import tkinter as tk
from tkinter import ttk, messagebox
from RestaurantDatabaseManager import RestaurantDatabaseManager


class InventoryManagement(tk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors['background'])
        self.db = RestaurantDatabaseManager()
        self.colors = colors
        self.selected_item_id = None
        self.build_ui()
        self.refresh_all_data()

    def build_ui(self):
        c = self.colors

        # Header
        header = tk.Frame(self, bg=c['background'])
        header.pack(fill="x", pady=(0, 24))

        tk.Label(header, text="Inventory Management", bg=c['background'],
                 fg=c['text_primary'], font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Track ingredients, stock levels, and manage suppliers",
                 bg=c['background'], fg=c['text_secondary'],
                 font=("Segoe UI", 11)).pack(anchor="w", pady=(4, 0))

        content = tk.Frame(self, bg=c['background'])
        content.pack(fill="both", expand=True)

        # Left panel
        left = tk.Frame(content, bg=c['background'], width=370)
        left.pack(side="left", fill="y", padx=(0, 20))
        left.pack_propagate(False)

        self.build_form(left)
        self.build_alerts(left)

        # Right panel
        right = tk.Frame(content, bg=c['background'])
        right.pack(side="right", fill="both", expand=True)
        self.build_inventory_list(right)

    # Form

    def build_form(self, parent):
        c = self.colors
        card = tk.Frame(parent, bg=c['surface'], bd=1, relief="solid",
                        highlightbackground=c['border'], highlightthickness=1)
        card.pack(fill="x", pady=(0, 16))

        tk.Label(card, text="Add / Update Item", bg=c['surface'], fg=c['text_primary'],
                 font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x", padx=20, pady=(16, 12))

        form = tk.Frame(card, bg=c['surface'])
        form.pack(fill="x", padx=20, pady=(0, 20))

        self.ingredient_name_var = tk.StringVar()
        self.current_stock_var = tk.StringVar()
        self.unit_var = tk.StringVar(value="kg")
        self.threshold_var = tk.StringVar()
        self.cost_per_unit_var = tk.StringVar()
        self.supplier_var = tk.StringVar()
        self.expiry_date_var = tk.StringVar()

        fields = [
            ("Ingredient Name", self.ingredient_name_var, "entry"),
            ("Current Stock", self.current_stock_var, "entry"),
            ("Unit", self.unit_var, "combo"),
            ("Min Threshold", self.threshold_var, "entry"),
            ("Cost per Unit ($)", self.cost_per_unit_var, "entry"),
            ("Supplier", self.supplier_var, "entry"),
            ("Expiry Date", self.expiry_date_var, "entry"),
        ]

        for label_text, var, field_type in fields:
            tk.Label(form, text=label_text, bg=c['surface'], fg=c['text_secondary'],
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(8, 3))

            if field_type == "combo":
                units = ["kg", "lbs", "liters", "pieces", "boxes", "bags"]
                ttk.Combobox(form, textvariable=var, values=units, state="readonly",
                             font=("Segoe UI", 10), width=28).pack(fill="x")
            else:
                ttk.Entry(form, textvariable=var, font=("Segoe UI", 10), width=30).pack(fill="x")

        # Buttons
        btn_frame = tk.Frame(form, bg=c['surface'])
        btn_frame.pack(fill="x", pady=(16, 0))

        ttk.Button(btn_frame, text="Add Item", command=self.add_inventory_item,
                   style="Accent.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Update", command=self.update_inventory_item).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Clear", command=self.clear_form).pack(side="left")

    # Alerts

    def build_alerts(self, parent):
        c = self.colors
        self.alerts_card = tk.Frame(parent, bg=c['surface'], bd=1, relief="solid",
                                    highlightbackground=c['border'], highlightthickness=1)
        self.alerts_card.pack(fill="x")

        tk.Label(self.alerts_card, text="Low Stock Alerts", bg=c['surface'], fg=c['text_primary'],
                 font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x", padx=20, pady=(16, 10))

        self.alerts_content = tk.Frame(self.alerts_card, bg=c['surface'])
        self.alerts_content.pack(fill="x", padx=20, pady=(0, 16))

    def refresh_alerts(self):
        c = self.colors
        for w in self.alerts_content.winfo_children():
            w.destroy()

        low_stock = self.db.get_inventory(low_stock_only=True)

        if not low_stock:
            tk.Label(self.alerts_content, text="\u2713  All items adequately stocked",
                     bg=c['surface'], fg=c['success'],
                     font=("Segoe UI", 10)).pack(anchor="w")
            return

        for item in low_stock[:6]:
            name, current, unit, threshold = item[1], item[2], item[3], item[4]
            row = tk.Frame(self.alerts_content, bg=c['error_light'])
            row.pack(fill="x", pady=2)

            tk.Label(row, text="\u26a0", bg=c['error_light'], fg=c['error'],
                     font=("Segoe UI", 10)).pack(side="left", padx=(8, 6), pady=6)
            tk.Label(row, text="{}: {} {} (min: {})".format(name, current, unit, threshold),
                     bg=c['error_light'], fg=c['error'],
                     font=("Segoe UI", 9)).pack(side="left", pady=6)

        if len(low_stock) > 6:
            tk.Label(self.alerts_content,
                     text="  ...and {} more".format(len(low_stock) - 6),
                     bg=c['surface'], fg=c['text_muted'],
                     font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 0))

    # Inventory List

    def build_inventory_list(self, parent):
        c = self.colors
        card = tk.Frame(parent, bg=c['surface'], bd=1, relief="solid",
                        highlightbackground=c['border'], highlightthickness=1)
        card.pack(fill="both", expand=True)

        hdr = tk.Frame(card, bg=c['surface'])
        hdr.pack(fill="x", padx=20, pady=(16, 12))

        tk.Label(hdr, text="Current Inventory", bg=c['surface'], fg=c['text_primary'],
                 font=("Segoe UI", 12, "bold")).pack(side="left")

        btn_row = tk.Frame(hdr, bg=c['surface'])
        btn_row.pack(side="right")

        ttk.Button(btn_row, text="Delete", command=self.delete_inventory_item).pack(side="left", padx=(0, 6))
        ttk.Button(btn_row, text="Refresh", command=self.refresh_all_data).pack(side="left")

        # Search
        search_frame = tk.Frame(card, bg=c['surface'])
        search_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.inv_search_var = tk.StringVar()
        self.inv_search_var.trace_add("write", lambda *_: self.filter_inventory())
        ttk.Entry(search_frame, textvariable=self.inv_search_var,
                  font=("Segoe UI", 10)).pack(side="left", fill="x", expand=True)
        tk.Label(search_frame, text="Search", bg=c['surface'], fg=c['text_muted'],
                 font=("Segoe UI", 9)).pack(side="right", padx=(8, 0))

        # Treeview
        tree_frame = tk.Frame(card, bg=c['surface'])
        tree_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        cols = ("id", "name", "stock", "unit", "threshold", "cost", "supplier", "expiry")
        self.inventory_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15)

        headings = {"id": "ID", "name": "Ingredient", "stock": "Stock", "unit": "Unit",
                     "threshold": "Min", "cost": "Cost/Unit", "supplier": "Supplier", "expiry": "Expiry"}
        widths = {"id": 0, "name": 150, "stock": 70, "unit": 55, "threshold": 55,
                  "cost": 75, "supplier": 120, "expiry": 95}

        for col in cols:
            self.inventory_tree.heading(col, text=headings[col], anchor="w")
            self.inventory_tree.column(col, width=widths[col], anchor="w",
                                       stretch=(col != "id"))
            if col == "id":
                self.inventory_tree.column(col, stretch=False)

        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=v_scroll.set)
        self.inventory_tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

        self.inventory_tree.bind("<<TreeviewSelect>>", self.on_item_select)
        self.inventory_tree.tag_configure("low_stock", background=c['error_light'], foreground="#991b1b")

    # Data Operations

    def refresh_inventory_list(self):
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)

        items = self.db.get_inventory()
        for item in items:
            cost = "${:.2f}".format(item[5]) if item[5] is not None else ""
            tag = ("low_stock",) if item[2] <= item[4] else ()
            self.inventory_tree.insert("", "end", values=(
                item[0], item[1], item[2], item[3], item[4], cost,
                item[6] or "", item[8] or ""
            ), tags=tag)

    def filter_inventory(self):
        query = self.inv_search_var.get().lower()
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)

        items = self.db.get_inventory()
        for item in items:
            if query and query not in item[1].lower() and query not in (item[6] or "").lower():
                continue
            cost = "${:.2f}".format(item[5]) if item[5] is not None else ""
            tag = ("low_stock",) if item[2] <= item[4] else ()
            self.inventory_tree.insert("", "end", values=(
                item[0], item[1], item[2], item[3], item[4], cost,
                item[6] or "", item[8] or ""
            ), tags=tag)

    def add_inventory_item(self):
        try:
            name = self.ingredient_name_var.get().strip()
            stock = float(self.current_stock_var.get())
            unit = self.unit_var.get()
            threshold = float(self.threshold_var.get())
            cost = float(self.cost_per_unit_var.get() or 0)
            supplier = self.supplier_var.get().strip()
            expiry = self.expiry_date_var.get().strip()

            if not name or not self.current_stock_var.get() or not self.threshold_var.get():
                messagebox.showerror("Error", "Name, Current Stock, and Min Threshold are required.")
                return

            if self.db.add_inventory_item(name, stock, unit, threshold, cost, supplier, expiry):
                messagebox.showinfo("Success", "Inventory item added!")
                self.clear_form()
                self.refresh_all_data()
            else:
                messagebox.showerror("Error", "Failed to add inventory item.")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")

    def update_inventory_item(self):
        if not self.selected_item_id:
            messagebox.showwarning("Warning", "Select an item from the list to update.")
            return
        try:
            name = self.ingredient_name_var.get().strip()
            stock = float(self.current_stock_var.get())
            unit = self.unit_var.get()
            threshold = float(self.threshold_var.get())
            cost = float(self.cost_per_unit_var.get() or 0)
            supplier = self.supplier_var.get().strip()
            expiry = self.expiry_date_var.get().strip()

            if not name or not self.current_stock_var.get() or not self.threshold_var.get():
                messagebox.showerror("Error", "Name, Current Stock, and Min Threshold are required.")
                return

            if self.db.update_inventory_item(self.selected_item_id, name, stock, unit,
                                             threshold, cost, supplier, expiry):
                messagebox.showinfo("Success", "Item updated!")
                self.clear_form()
                self.refresh_all_data()
            else:
                messagebox.showerror("Error", "Failed to update item.")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")

    def delete_inventory_item(self):
        if not self.selected_item_id:
            messagebox.showwarning("Warning", "Select an item to delete.")
            return
        if messagebox.askyesno("Confirm", "Permanently delete this inventory item?"):
            if self.db.delete_inventory_item(self.selected_item_id):
                messagebox.showinfo("Success", "Item deleted.")
                self.db.check_and_update_all_menu_availability()
                self.clear_form()
                self.refresh_all_data()
            else:
                messagebox.showerror("Error", "Failed to delete item.")

    def on_item_select(self, event):
        sel = self.inventory_tree.selection()
        if sel:
            data = self.inventory_tree.item(sel[0])
            self.selected_item_id = data['values'][0]
            details = self.db.get_inventory_item_by_id(self.selected_item_id)
            if details:
                self.ingredient_name_var.set(details[1])
                self.current_stock_var.set(details[2])
                self.unit_var.set(details[3])
                self.threshold_var.set(details[4])
                self.cost_per_unit_var.set(details[5] or "")
                self.supplier_var.set(details[6] or "")
                self.expiry_date_var.set(details[8] or "")

    def clear_form(self):
        self.ingredient_name_var.set("")
        self.current_stock_var.set("")
        self.unit_var.set("kg")
        self.threshold_var.set("")
        self.cost_per_unit_var.set("")
        self.supplier_var.set("")
        self.expiry_date_var.set("")
        self.selected_item_id = None
        if self.inventory_tree.selection():
            self.inventory_tree.selection_remove(self.inventory_tree.selection()[0])

    def refresh_all_data(self):
        self.refresh_inventory_list()
        self.refresh_alerts()
