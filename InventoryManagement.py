import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from RestaurantDatabaseManager import RestaurantDatabaseManager


class InventoryManagement(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = RestaurantDatabaseManager()
        self.configure(padding=0)
        self.selected_item_id = None
        self.build_modern_ui()
        self.refresh_all_data()

    def build_modern_ui(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 30))

        title_label = ttk.Label(
            header_frame,
            text="Inventory Management",
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(anchor="w")

        subtitle_label = ttk.Label(
            header_frame,
            text="Track ingredients, stock levels, and manage suppliers",
            font=("Segoe UI", 12),
            foreground="#888888"
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True)

        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side="left", fill="y", padx=(0, 20))

        self.build_inventory_form(left_frame)

        self.alerts_frame = ttk.LabelFrame(left_frame, text="Low Stock Alerts", padding=15)
        self.alerts_frame.pack(fill="x", pady=10)

        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        self.build_inventory_list(right_frame)

    def build_inventory_form(self, parent):
        form_container = ttk.LabelFrame(parent, text="Add/Update Inventory Item", padding=20)
        form_container.pack(fill="x", pady=(0, 20))
        form_container.configure(width=350)

        self.ingredient_name_var = tk.StringVar()
        self.current_stock_var = tk.StringVar()
        self.unit_var = tk.StringVar(value="kg")
        self.threshold_var = tk.StringVar()
        self.cost_per_unit_var = tk.StringVar()
        self.supplier_var = tk.StringVar()
        self.expiry_date_var = tk.StringVar()

        fields = [
            ("Ingredient Name *", self.ingredient_name_var, "e.g., Item Ingredient"),
            ("Current Stock *", self.current_stock_var, "Current quantity"),
            ("Unit", self.unit_var, None),
            ("Min Threshold *", self.threshold_var, "Reorder level"),
            ("Cost per Unit ($)", self.cost_per_unit_var, "Unit cost"),
            ("Supplier", self.supplier_var, "Supplier name"),
            ("Expiry Date", self.expiry_date_var, "YYYY-MM-DD format"),
        ]

        for i, (label, var, placeholder) in enumerate(fields):
            label_widget = ttk.Label(form_container, text=label, font=("Segoe UI", 10, "bold"))
            label_widget.pack(anchor="w", pady=(15 if i > 0 else 0, 5))

            if label == "Unit":
                units = ["kg", "lbs", "liters", "pieces", "boxes", "bags"]
                unit_combo = ttk.Combobox(form_container, textvariable=var,
                                          values=units, state="readonly",
                                          font=("Segoe UI", 11), width=28)
                unit_combo.pack(fill="x", pady=(0, 5))
            else:
                entry = ttk.Entry(form_container, textvariable=var, font=("Segoe UI", 11), width=30)
                entry.pack(fill="x", pady=(0, 5))

            if placeholder:
                help_label = ttk.Label(
                    form_container,
                    text=placeholder,
                    font=("Segoe UI", 9),
                    foreground="#666666"
                )
                help_label.pack(anchor="w", pady=(0, 10))

        button_frame = ttk.Frame(form_container)
        button_frame.pack(fill="x", pady=(20, 0))

        add_btn = ttk.Button(
            button_frame,
            text="Add Item",
            command=self.add_inventory_item,
            style="Accent.TButton"
        )
        add_btn.pack(side="left", padx=(0, 10))

        update_btn = ttk.Button(
            button_frame,
            text="Update",
            command=self.update_inventory_item
        )
        update_btn.pack(side="left", padx=(0, 10))

        clear_btn = ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_form
        )
        clear_btn.pack(side="left")

    def refresh_low_stock_alerts(self):
        for widget in self.alerts_frame.winfo_children():
            widget.destroy()

        low_stock_items = self.db.get_inventory(low_stock_only=True)

        if not low_stock_items:
            no_alerts_label = ttk.Label(
                self.alerts_frame,
                text="All items are adequately stocked",
                font=("Segoe UI", 10),
                foreground="#059669"
            )
            no_alerts_label.pack()
        else:
            alerts_text = tk.Text(
                self.alerts_frame,
                height=6,
                width=40,
                font=("Segoe UI", 9),
                bg="#fef2f2",
                fg="#dc2626",
                wrap=tk.WORD,
                bd=0, highlightthickness=0
            )
            alerts_text.pack(fill="both", expand=True)

            alerts_text.config(state=tk.NORMAL)
            alerts_text.delete('1.0', tk.END)
            for item in low_stock_items:
                name, current, unit, threshold = item[1], item[2], item[3], item[4]
                alerts_text.insert(tk.END, f"{name}: {current} {unit} (min: {threshold})\n")
            alerts_text.config(state=tk.DISABLED)

    def build_inventory_list(self, parent):
        list_header = ttk.Frame(parent)
        list_header.pack(fill="x", pady=(0, 15))

        ttk.Label(
            list_header,
            text="Current Inventory",
            font=("Segoe UI", 16, "bold")
        ).pack(side="left")

        control_frame = ttk.Frame(list_header)
        control_frame.pack(side="right")

        refresh_btn = ttk.Button(
            control_frame,
            text="Refresh",
            command=self.refresh_all_data
        )
        refresh_btn.pack(side="left", padx=(0, 10))

        delete_btn = ttk.Button(
            control_frame,
            text="Delete",
            command=self.delete_inventory_item
        )
        delete_btn.pack(side="left")

        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill="both", expand=True)

        self.inventory_tree = ttk.Treeview(
            tree_frame,
            columns=("id", "name", "stock", "unit", "threshold", "cost", "supplier", "expiry"),
            show="headings",
            height=15
        )

        self.inventory_tree.heading("id", text="ID")
        self.inventory_tree.heading("name", text="Ingredient", anchor="w")
        self.inventory_tree.heading("stock", text="Stock", anchor="w")
        self.inventory_tree.heading("unit", text="Unit", anchor="w")
        self.inventory_tree.heading("threshold", text="Min", anchor="w")
        self.inventory_tree.heading("cost", text="Cost/Unit", anchor="w")
        self.inventory_tree.heading("supplier", text="Supplier", anchor="w")
        self.inventory_tree.heading("expiry", text="Expiry", anchor="w")
        self.inventory_tree.column("id", width=0, stretch=tk.NO)
        self.inventory_tree.column("name", width=150, anchor="w")
        self.inventory_tree.column("stock", width=80, anchor="w")
        self.inventory_tree.column("unit", width=60, anchor="w")
        self.inventory_tree.column("threshold", width=60, anchor="w")
        self.inventory_tree.column("cost", width=80, anchor="w")
        self.inventory_tree.column("supplier", width=120, anchor="w")
        self.inventory_tree.column("expiry", width=100, anchor="w")

        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.inventory_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.inventory_tree.xview)
        self.inventory_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.inventory_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")

        self.inventory_tree.bind("<<TreeviewSelect>>", self.on_item_select)

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

            # MODIFICATION: The db.add_inventory_item function now handles the availability check
            if self.db.add_inventory_item(name, stock, unit, threshold, cost, supplier, expiry):
                messagebox.showinfo("Success", "Inventory item added successfully!")
                self.clear_form()
                self.refresh_all_data()
            else:
                messagebox.showerror("Error", "Failed to add inventory item")

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for stock, threshold, and cost.")

    def update_inventory_item(self):
        if not self.selected_item_id:
            messagebox.showwarning("Warning", "Please select an item from the list to update.")
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

            # MODIFICATION: The db.update_inventory_item function now handles the availability check
            if self.db.update_inventory_item(self.selected_item_id, name, stock, unit, threshold, cost, supplier,
                                             expiry):
                messagebox.showinfo("Success", "Inventory item updated successfully!")
                self.clear_form()
                self.refresh_all_data()
            else:
                messagebox.showerror("Error", "Failed to update inventory item.")

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for stock, threshold, and cost.")

    def delete_inventory_item(self):
        if not self.selected_item_id:
            messagebox.showwarning("Warning", "Please select an item from the list to delete.")
            return

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to permanently delete this item?"):
            if self.db.delete_inventory_item(self.selected_item_id):
                messagebox.showinfo("Success", "Inventory item deleted.")
                # MODIFICATION: Check availability after deleting an item
                self.db.check_and_update_all_menu_availability()
                self.clear_form()
                self.refresh_all_data()
            else:
                messagebox.showerror("Error", "Failed to delete item.")

    def on_item_select(self, event):
        selection = self.inventory_tree.selection()
        if selection:
            item_data = self.inventory_tree.item(selection[0])
            self.selected_item_id = item_data['values'][0]

            item_details = self.db.get_inventory_item_by_id(self.selected_item_id)
            if item_details:
                self.ingredient_name_var.set(item_details[1])
                self.current_stock_var.set(item_details[2])
                self.unit_var.set(item_details[3])
                self.threshold_var.set(item_details[4])
                self.cost_per_unit_var.set(item_details[5] or "")
                self.supplier_var.set(item_details[6] or "")
                self.expiry_date_var.set(item_details[8] or "")

    def refresh_inventory_list(self):
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)

        inventory_items = self.db.get_inventory()
        for item in inventory_items:
            item_id, name, stock, unit, threshold = item[0], item[1], item[2], item[3], item[4]
            cost = f"{item[5]:.2f}" if item[5] is not None else ""
            supplier = item[6] or ""
            expiry = item[8] or ""
            tag = "low_stock" if stock <= threshold else "normal"

            self.inventory_tree.insert(
                "", "end",
                values=(item_id, name, stock, unit, threshold, cost, supplier, expiry),
                tags=(tag,)
            )

        self.inventory_tree.tag_configure("low_stock", background="#fef2f2", foreground="#991b1b")
        self.inventory_tree.tag_configure("normal", background="#ffffff")

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
        self.refresh_low_stock_alerts()