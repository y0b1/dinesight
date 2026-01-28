import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from RestaurantDatabaseManager import RestaurantDatabaseManager
from RecipeEditor import RecipeEditorWindow


class MenuTracker(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = RestaurantDatabaseManager()
        self.configure(padding=0)

        self.selected_menu_item_id = None

        self.build_modern_ui()

    def build_modern_ui(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 30))

        title_label = ttk.Label(
            header_frame,
            text="Menu Management",
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(anchor="w")

        subtitle_label = ttk.Label(
            header_frame,
            text="Manage your restaurant's menu items and pricing",
            font=("Segoe UI", 12),
            foreground="#888888"
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True)

        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side="left", fill="y", padx=(0, 20))

        self.build_modern_form(left_frame)

        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        self.build_menu_list(right_frame)
        self.refresh_all_data()

    def build_modern_form(self, parent):
        form_container = ttk.LabelFrame(parent, text="Add New Menu Item", padding=25)
        form_container.pack(fill="x", pady=(0, 20))
        form_container.configure(width=350)

        self.name_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Main Course")
        self.description_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.cost_var = tk.StringVar()
        self.prep_time_var = tk.StringVar()

        fields = [
            ("Item Name *", self.name_var, "e.g., Menu Items"),
            ("Category", self.category_var, None),
            ("Description", self.description_var, "Brief item description"),
            ("Selling Price ($) *", self.price_var, "Customer price"),
            ("Food Cost ($)", self.cost_var, "Cost to prepare"),
            ("Prep Time (mins)", self.prep_time_var, "Average preparation time"),
        ]

        for i, (label, var, placeholder) in enumerate(fields):
            label_widget = ttk.Label(form_container, text=label, font=("Segoe UI", 10, "bold"))
            label_widget.pack(anchor="w", pady=(15 if i > 0 else 0, 5))

            if label == "Category":
                categories = ["Appetizer", "Main Course", "Dessert", "Beverage", "Special"]
                category_combo = ttk.Combobox(
                    form_container, textvariable=var, values=categories,
                    state="readonly", font=("Segoe UI", 11), width=28
                )
                category_combo.pack(fill="x", pady=(0, 5))
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
            text="Add Menu Item",
            command=self.add_menu_item,
            style="Accent.TButton"
        )
        add_btn.pack(side="left", padx=(0, 10))

        clear_btn = ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_form
        )
        clear_btn.pack(side="left")

        # MODIFICATION: Add "Manage Recipe" button
        self.recipe_btn = ttk.Button(
            form_container,
            text="Manage Recipe for Selected Item",
            command=self.open_recipe_editor,
            state="disabled"  # Starts disabled
        )
        self.recipe_btn.pack(fill="x", pady=(20, 0))

        self.stats_frame = ttk.LabelFrame(parent, text="Menu Overview", padding=20)
        self.stats_frame.pack(fill="x", pady=10)

    def refresh_menu_stats_card(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        menu_items = self.db.get_menu_items()
        total_items = len(menu_items)
        available_items = len([item for item in menu_items if item[7]]) if menu_items else 0

        if menu_items:
            avg_price = sum(item[4] for item in menu_items) / len(menu_items)
            categories = set(item[2] for item in menu_items if item[2])
        else:
            avg_price, categories = 0, set()

        sales_summary = self.db.get_sales_summary()

        stats_text = f"Total Items: {total_items}\n"
        stats_text += f"Available: {available_items}\n"
        stats_text += f"Categories: {len(categories)}\n"
        stats_text += f"Avg Price: ${avg_price:.2f}\n"
        stats_text += f"Popular: {sales_summary['popular_item']}"

        stats_label = ttk.Label(self.stats_frame, text=stats_text, font=("Segoe UI", 10), justify="left")
        stats_label.pack(anchor="w")

    def build_menu_list(self, parent):
        list_header = ttk.Frame(parent)
        list_header.pack(fill="x", pady=(0, 15))

        ttk.Label(list_header, text="Current Menu", font=("Segoe UI", 16, "bold")).pack(side="left")

        self.menu_tree = ttk.Treeview(
            parent, columns=("id", "Name", "Category", "Price", "Available"),
            show="headings", height=15
        )
        self.menu_tree.pack(fill="both", expand=True)

        self.menu_tree.heading("id", text="ID")
        self.menu_tree.heading("Name", text="Name")
        self.menu_tree.heading("Category", text="Category")
        self.menu_tree.heading("Price", text="Price ($)")
        self.menu_tree.heading("Available", text="Available")

        self.menu_tree.column("id", width=0, stretch=tk.NO)  # Hide ID
        self.menu_tree.column("Name", width=200)
        self.menu_tree.column("Category", width=120)
        self.menu_tree.column("Price", width=100)
        self.menu_tree.column("Available", width=100)

        self.menu_tree.bind("<<TreeviewSelect>>", self.on_menu_item_select)

    def refresh_menu_list(self):
        for row in self.menu_tree.get_children():
            self.menu_tree.delete(row)

        menu_items = self.db.get_menu_items()
        for item in menu_items:
            # item = (id, name, category, desc, price, cost, prep, is_available, ...)
            self.menu_tree.insert("", "end", values=(
                item[0],  # id
                item[1],  # name
                item[2],  # category
                f"${item[4]:.2f}",  # price
                "Yes" if item[7] else "No"  # is_available
            ))

    def refresh_all_data(self):
        self.refresh_menu_list()
        self.refresh_menu_stats_card()

        # MODIFICATION: Reset selection
        self.selected_menu_item_id = None
        self.recipe_btn.config(state="disabled")

    def add_menu_item(self):
        name = self.name_var.get().strip()
        category = self.category_var.get()
        description = self.description_var.get()
        price = self.price_var.get()
        cost = self.cost_var.get()
        prep_time = self.prep_time_var.get()

        if not name or not price:
            messagebox.showerror("Error", "Name and Price are required.")
            return

        try:
            price = float(price)
            cost = float(cost) if cost else 0
            prep_time = int(prep_time) if prep_time else 0
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric values.")
            return

        self.db.add_menu_item(name, category, description, price, cost, prep_time, True)
        messagebox.showinfo("Success", f"Menu item '{name}' added!")
        self.refresh_all_data()
        self.clear_form()

    def clear_form(self):
        self.name_var.set("")
        self.category_var.set("Main Course")
        self.description_var.set("")
        self.price_var.set("")
        self.cost_var.set("")
        self.prep_time_var.set("")

        # Deselect in tree
        if self.menu_tree.selection():
            self.menu_tree.selection_remove(self.menu_tree.selection()[0])
        self.selected_menu_item_id = None
        self.recipe_btn.config(state="disabled")

    def on_menu_item_select(self, event):
        selection = self.menu_tree.selection()
        if selection:
            item_data = self.menu_tree.item(selection[0])
            self.selected_menu_item_id = item_data['values'][0]  # Get the ID
            self.recipe_btn.config(state="normal")  # Enable the button
        else:
            self.selected_menu_item_id = None
            self.recipe_btn.config(state="disabled")

    def open_recipe_editor(self):
        if not self.selected_menu_item_id:
            messagebox.showwarning("Error", "No menu item selected.")
            return

        editor = RecipeEditorWindow(self, self.db, self.selected_menu_item_id)