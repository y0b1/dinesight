import tkinter as tk
from tkinter import ttk, messagebox
from RestaurantDatabaseManager import RestaurantDatabaseManager


class SalesLogger(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = RestaurantDatabaseManager()
        self.configure(padding=0)

        self.selected_item_id = None
        self.selected_item_name = None
        self.selected_item_category = None
        self.selected_item_price = None

        self.build_modern_ui()
        self.refresh_menu_list()
        self.refresh_sales_history()

    def build_modern_ui(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 30))

        title_label = ttk.Label(
            header_frame,
            text="Sales Logger (POS)",
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(anchor="w")

        subtitle_label = ttk.Label(
            header_frame,
            text="Log daily sales to power your analytics",
            font=("Segoe UI", 12),
            foreground="#888888"
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True)

        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

        menu_items_frame = ttk.LabelFrame(left_frame, text="Available Menu Items", padding=15)
        menu_items_frame.pack(fill="both", expand=True, pady=(0, 15))
        self.build_menu_list(menu_items_frame)

        sales_history_wrapper = ttk.LabelFrame(left_frame, text="Sales History", padding=15)
        sales_history_wrapper.pack(fill="both", expand=True)
        self.build_sales_history(sales_history_wrapper)

        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side="right", fill="y", padx=(0, 20))

        self.build_logging_form(right_frame)

    def build_menu_list(self, parent):
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill="both", expand=True)

        self.menu_tree = ttk.Treeview(
            tree_frame, columns=("id", "Name", "Category", "Price"),
            show="headings", height=8
        )

        self.menu_tree.heading("id", text="ID")
        self.menu_tree.heading("Name", text="Name")
        self.menu_tree.heading("Category", text="Category")
        self.menu_tree.heading("Price", text="Price ($)")
        self.menu_tree.column("id", width=0, stretch=tk.NO)
        self.menu_tree.column("Name", width=200, anchor="w")
        self.menu_tree.column("Category", width=120, anchor="w")
        self.menu_tree.column("Price", width=80, anchor="center")

        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.menu_tree.yview)
        self.menu_tree.configure(yscrollcommand=v_scrollbar.set)

        self.menu_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")

        self.menu_tree.bind("<<TreeviewSelect>>", self.on_item_select)

    def build_sales_history(self, parent):
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill="both", expand=True)

        self.sales_history_tree = ttk.Treeview(
            tree_frame,
            columns=("id", "Item", "Qty", "Total", "Date"),
            show="headings",
            height=10
        )

        self.sales_history_tree.heading("id", text="ID")
        self.sales_history_tree.heading("Item", text="Item")
        self.sales_history_tree.heading("Qty", text="Qty")
        self.sales_history_tree.heading("Total", text="Total ($)")
        self.sales_history_tree.heading("Date", text="Date")

        self.sales_history_tree.column("id", width=0, stretch=tk.NO)
        self.sales_history_tree.column("Item", width=150, anchor="w")
        self.sales_history_tree.column("Qty", width=50, anchor="center")
        self.sales_history_tree.column("Total", width=80, anchor="center")
        self.sales_history_tree.column("Date", width=100, anchor="center")

        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.sales_history_tree.yview)
        self.sales_history_tree.configure(yscrollcommand=v_scrollbar.set)

        self.sales_history_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")

    def refresh_sales_history(self):
        """Refreshes the sales history treeview with recent sales."""
        for row in self.sales_history_tree.get_children():
            self.sales_history_tree.delete(row)

        sales = self.db.get_sales_data()  # Gets all sales, you might want to filter later
        for sale in sales:
            self.sales_history_tree.insert("", "end", values=(
                sale[0],
                sale[1],
                sale[3],
                f"${sale[5]:.2f}",
                sale[6]
            ))

    def build_logging_form(self, parent):
        form_container = ttk.LabelFrame(parent, text="Log a Sale", padding=25)
        form_container.pack(fill="x")
        form_container.configure(width=350)

        self.item_name_var = tk.StringVar(value="No item selected")
        self.item_price_var = tk.StringVar()
        self.quantity_var = tk.StringVar(value="1")

        ttk.Label(form_container, text="Item:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        item_label = ttk.Label(
            form_container,
            textvariable=self.item_name_var,
            font=("Segoe UI", 12, "bold"),
            foreground="#3b82f6"
        )
        item_label.pack(anchor="w", pady=(0, 15))

        ttk.Label(form_container, text="Price:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        price_label = ttk.Label(
            form_container,
            textvariable=self.item_price_var,
            font=("Segoe UI", 11)
        )
        price_label.pack(anchor="w", pady=(0, 20))

        ttk.Label(form_container, text="Quantity Sold:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        quantity_entry = ttk.Entry(
            form_container,
            textvariable=self.quantity_var,
            font=("Segoe UI", 11),
            width=30
        )
        quantity_entry.pack(fill="x", pady=(0, 20))

        button_frame = ttk.Frame(form_container)
        button_frame.pack(fill="x", pady=(10, 0))

        log_btn = ttk.Button(
            button_frame,
            text="Log Sale",
            command=self.log_sale,
            style="Accent.TButton"
        )
        log_btn.pack(fill="x", expand=True, side="left", padx=(0, 10))

        clear_btn = ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_form
        )
        clear_btn.pack(fill="x", expand=True, side="left")

    def refresh_menu_list(self):
        """Refresh the list of available menu items"""
        # Deselect first
        self.clear_form()

        for row in self.menu_tree.get_children():
            self.menu_tree.delete(row)

        menu_items = self.db.get_menu_items(available_only=True)
        for item in menu_items:
            item_id, name, category, price = item[0], item[1], item[2], item[4]
            self.menu_tree.insert("", "end", values=(item_id, name, category, f"${price:.2f}"))

    def on_item_select(self, event):
        selection = self.menu_tree.selection()
        if selection:
            item_data = self.menu_tree.item(selection[0])['values']

            self.selected_item_id = int(item_data[0])
            self.selected_item_name = item_data[1]
            self.selected_item_category = item_data[2]
            self.selected_item_price = float(item_data[3].strip('$'))

            self.item_name_var.set(self.selected_item_name)
            self.item_price_var.set(f"${self.selected_item_price:.2f}")
            self.quantity_var.set("1")

    def log_sale(self):
        if not self.selected_item_id:
            messagebox.showwarning("No Item Selected", "Please select an item from the menu list first.")
            return

        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Please enter a valid positive number for the quantity.")
            return

        has_enough_stock = self.db.check_stock_for_sale(self.selected_item_id, quantity)

        if not has_enough_stock:
            messagebox.showerror("Out of Stock", "There are not enough ingredients in inventory to make this sale.")
            return

        unit_price = self.selected_item_price
        total_amount = unit_price * quantity

        try:
            self.db.record_sale(
                menu_item_id=self.selected_item_id,
                item_name=self.selected_item_name,
                category=self.selected_item_category,
                quantity=quantity,
                unit_price=unit_price,
                total_amount=total_amount
            )

            messagebox.showinfo(
                "Sale Logged",
                f"Successfully logged sale:\n\n"
                f"Item: {self.selected_item_name}\n"
                f"Quantity: {quantity}\n"
                f"Total: ${total_amount:.2f}"
            )

            self.refresh_menu_list()
            self.refresh_sales_history()

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to log sale: {e}")

    def clear_form(self):
        self.selected_item_id = None
        self.selected_item_name = None
        self.selected_item_category = None
        self.selected_item_price = None

        self.item_name_var.set("No item selected")
        self.item_price_var.set("")
        self.quantity_var.set("1")

        if self.menu_tree.selection():
            self.menu_tree.selection_remove(self.menu_tree.selection()[0])