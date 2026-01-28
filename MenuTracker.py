import tkinter as tk
from tkinter import messagebox, ttk

from RecipeEditor import RecipeEditorWindow
from RestaurantDatabaseManager import RestaurantDatabaseManager


class MenuTracker(tk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors["background"])
        self.db = RestaurantDatabaseManager()
        self.colors = colors
        self.selected_menu_item_id = None
        self.editing = False
        self.build_ui()
        self.refresh_all_data()

    def build_ui(self):
        c = self.colors

        # Header
        header = tk.Frame(self, bg=c["background"])
        header.pack(fill="x", pady=(0, 24))

        tk.Label(
            header,
            text="Menu Management",
            bg=c["background"],
            fg=c["text_primary"],
            font=("Segoe UI", 22, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Manage your restaurant's menu items and pricing",
            bg=c["background"],
            fg=c["text_secondary"],
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=(4, 0))

        content = tk.Frame(self, bg=c["background"])
        content.pack(fill="both", expand=True)

        # Left panel - form + stats
        left = tk.Frame(content, bg=c["background"], width=360)
        left.pack(side="left", fill="y", padx=(0, 20))
        left.pack_propagate(False)

        self.build_form(left)
        self.build_stats(left)

        # Right panel - menu list
        right = tk.Frame(content, bg=c["background"])
        right.pack(side="right", fill="both", expand=True)
        self.build_menu_list(right)

    # ── Form ────────────────────────────────────────────────────

    def build_form(self, parent):
        c = self.colors
        card = tk.Frame(
            parent,
            bg=c["surface"],
            bd=1,
            relief="solid",
            highlightbackground=c["border"],
            highlightthickness=1,
        )
        card.pack(fill="x", pady=(0, 16))

        self.form_title_label = tk.Label(
            card,
            text="Add New Menu Item",
            bg=c["surface"],
            fg=c["text_primary"],
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        self.form_title_label.pack(fill="x", padx=20, pady=(16, 12))

        form = tk.Frame(card, bg=c["surface"])
        form.pack(fill="x", padx=20, pady=(0, 20))

        self.name_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Main Course")
        self.description_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.cost_var = tk.StringVar()
        self.prep_time_var = tk.StringVar()

        fields = [
            ("Item Name", self.name_var, "entry"),
            ("Category", self.category_var, "combo"),
            ("Description", self.description_var, "entry"),
            ("Selling Price ($)", self.price_var, "entry"),
            ("Food Cost ($)", self.cost_var, "entry"),
            ("Prep Time (mins)", self.prep_time_var, "entry"),
        ]

        for label_text, var, field_type in fields:
            tk.Label(
                form,
                text=label_text,
                bg=c["surface"],
                fg=c["text_secondary"],
                font=("Segoe UI", 9, "bold"),
            ).pack(anchor="w", pady=(10, 4))

            if field_type == "combo":
                categories = [
                    "Appetizer",
                    "Main Course",
                    "Dessert",
                    "Beverage",
                    "Special",
                ]
                combo = ttk.Combobox(
                    form,
                    textvariable=var,
                    values=categories,
                    state="readonly",
                    font=("Segoe UI", 10),
                    width=28,
                )
                combo.pack(fill="x")
            else:
                ttk.Entry(form, textvariable=var, font=("Segoe UI", 10), width=30).pack(
                    fill="x"
                )

        # Buttons
        btn_frame = tk.Frame(form, bg=c["surface"])
        btn_frame.pack(fill="x", pady=(18, 0))

        self.add_btn = ttk.Button(
            btn_frame,
            text="Add Item",
            command=self.add_menu_item,
            style="Accent.TButton",
        )
        self.add_btn.pack(side="left", padx=(0, 8))

        self.update_btn = ttk.Button(
            btn_frame, text="Save Changes", command=self.save_edit
        )
        # Hidden until editing

        self.cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.cancel_edit)
        # Hidden until editing

        ttk.Button(btn_frame, text="Clear", command=self.clear_form).pack(side="left")

        # Recipe button
        self.recipe_btn = ttk.Button(
            form,
            text="Manage Recipe for Selected Item",
            command=self.open_recipe_editor,
            state="disabled",
        )
        self.recipe_btn.pack(fill="x", pady=(14, 0))

    # ── Stats ───────────────────────────────────────────────────

    def build_stats(self, parent):
        c = self.colors
        self.stats_card = tk.Frame(
            parent,
            bg=c["surface"],
            bd=1,
            relief="solid",
            highlightbackground=c["border"],
            highlightthickness=1,
        )
        self.stats_card.pack(fill="x")

        tk.Label(
            self.stats_card,
            text="Menu Overview",
            bg=c["surface"],
            fg=c["text_primary"],
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        ).pack(fill="x", padx=20, pady=(16, 12))

        self.stats_content = tk.Frame(self.stats_card, bg=c["surface"])
        self.stats_content.pack(fill="x", padx=20, pady=(0, 16))

    def refresh_stats(self):
        c = self.colors
        for w in self.stats_content.winfo_children():
            w.destroy()

        items = self.db.get_menu_items()
        total = len(items)
        available = len([i for i in items if i[7]]) if items else 0
        avg_price = sum(i[4] for i in items) / total if total else 0
        cats = len(set(i[2] for i in items if i[2])) if items else 0
        popular = self.db.get_sales_summary()["popular_item"]

        stats = [
            ("Total Items", str(total)),
            ("Available", str(available)),
            ("Categories", str(cats)),
            ("Avg Price", f"${avg_price:.2f}"),
            ("Most Popular", popular),
        ]

        for label, value in stats:
            row = tk.Frame(self.stats_content, bg=c["surface"])
            row.pack(fill="x", pady=3)
            tk.Label(
                row,
                text=label,
                bg=c["surface"],
                fg=c["text_secondary"],
                font=("Segoe UI", 10),
                anchor="w",
            ).pack(side="left")
            tk.Label(
                row,
                text=value,
                bg=c["surface"],
                fg=c["text_primary"],
                font=("Segoe UI", 10, "bold"),
                anchor="e",
            ).pack(side="right")

    # ── Menu List ───────────────────────────────────────────────

    def build_menu_list(self, parent):
        c = self.colors
        card = tk.Frame(
            parent,
            bg=c["surface"],
            bd=1,
            relief="solid",
            highlightbackground=c["border"],
            highlightthickness=1,
        )
        card.pack(fill="both", expand=True)

        # Header row with title + action buttons
        hdr = tk.Frame(card, bg=c["surface"])
        hdr.pack(fill="x", padx=20, pady=(16, 12))

        tk.Label(
            hdr,
            text="Current Menu",
            bg=c["surface"],
            fg=c["text_primary"],
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")

        btn_row = tk.Frame(hdr, bg=c["surface"])
        btn_row.pack(side="right")

        ttk.Button(btn_row, text="Edit", command=self.start_edit).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(btn_row, text="Delete", command=self.delete_menu_item).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(btn_row, text="Refresh", command=self.refresh_all_data).pack(
            side="left"
        )

        # Search
        search_frame = tk.Frame(card, bg=c["surface"])
        search_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.filter_menu_list())
        search_entry = ttk.Entry(
            search_frame, textvariable=self.search_var, font=("Segoe UI", 10), width=30
        )
        search_entry.pack(side="left", fill="x", expand=True)
        search_entry.insert(0, "")
        tk.Label(
            search_frame,
            text="Search",
            bg=c["surface"],
            fg=c["text_muted"],
            font=("Segoe UI", 9),
        ).pack(side="right", padx=(8, 0))

        # Treeview
        tree_frame = tk.Frame(card, bg=c["surface"])
        tree_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.menu_tree = ttk.Treeview(
            tree_frame,
            columns=("id", "Name", "Category", "Price", "Available"),
            show="headings",
            height=15,
        )
        self.menu_tree.heading("id", text="ID")
        self.menu_tree.heading("Name", text="Name")
        self.menu_tree.heading("Category", text="Category")
        self.menu_tree.heading("Price", text="Price ($)")
        self.menu_tree.heading("Available", text="Available")

        self.menu_tree.column("id", width=0, stretch=tk.NO)
        self.menu_tree.column("Name", width=200)
        self.menu_tree.column("Category", width=120)
        self.menu_tree.column("Price", width=100, anchor="e")
        self.menu_tree.column("Available", width=90, anchor="center")

        scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.menu_tree.yview
        )
        self.menu_tree.configure(yscrollcommand=scrollbar.set)
        self.menu_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.menu_tree.bind("<<TreeviewSelect>>", self.on_menu_item_select)
        self.menu_tree.tag_configure("unavailable", foreground="#94a3b8")

    # ── Data Operations ─────────────────────────────────────────

    def refresh_menu_list(self):
        for row in self.menu_tree.get_children():
            self.menu_tree.delete(row)

        items = self.db.get_menu_items()
        for item in items:
            avail = "Yes" if item[7] else "No"
            tag = () if item[7] else ("unavailable",)
            self.menu_tree.insert(
                "",
                "end",
                values=(item[0], item[1], item[2], f"${item[4]:.2f}", avail),
                tags=tag,
            )

    def filter_menu_list(self):
        query = self.search_var.get().lower()
        for row in self.menu_tree.get_children():
            self.menu_tree.delete(row)

        items = self.db.get_menu_items()
        for item in items:
            if (
                query
                and query not in item[1].lower()
                and query not in (item[2] or "").lower()
            ):
                continue
            avail = "Yes" if item[7] else "No"
            tag = () if item[7] else ("unavailable",)
            self.menu_tree.insert(
                "",
                "end",
                values=(item[0], item[1], item[2], f"${item[4]:.2f}", avail),
                tags=tag,
            )

    def refresh_all_data(self):
        self.refresh_menu_list()
        self.refresh_stats()
        self.selected_menu_item_id = None
        self.recipe_btn.config(state="disabled")

    def on_menu_item_select(self, event):
        sel = self.menu_tree.selection()
        if sel:
            data = self.menu_tree.item(sel[0])
            self.selected_menu_item_id = data["values"][0]
            self.recipe_btn.config(state="normal")
        else:
            self.selected_menu_item_id = None
            self.recipe_btn.config(state="disabled")

    def add_menu_item(self):
        name = self.name_var.get().strip()
        price = self.price_var.get()
        if not name or not price:
            messagebox.showerror("Error", "Name and Price are required.")
            return
        try:
            price = float(price)
            cost = float(self.cost_var.get()) if self.cost_var.get() else 0
            prep = int(self.prep_time_var.get()) if self.prep_time_var.get() else 0
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric values.")
            return

        self.db.add_menu_item(
            name,
            self.category_var.get(),
            self.description_var.get(),
            price,
            cost,
            prep,
            True,
        )
        messagebox.showinfo("Success", f"'{name}' added to the menu!")
        self.clear_form()
        self.refresh_all_data()

    def start_edit(self):
        if not self.selected_menu_item_id:
            messagebox.showwarning("Warning", "Select an item from the list to edit.")
            return

        item = self.db.get_menu_item_by_id(self.selected_menu_item_id)
        if not item:
            return

        self.editing = True
        self.form_title_label.config(text=f"Editing: {item[1]}")

        self.name_var.set(item[1])
        self.category_var.set(item[2] or "Main Course")
        self.description_var.set(item[3] or "")
        self.price_var.set(str(item[4]))
        self.cost_var.set(str(item[5]) if item[5] else "")
        self.prep_time_var.set(str(item[6]) if item[6] else "")

        # Show update/cancel, hide add
        self.add_btn.pack_forget()
        self.update_btn.pack(side="left", padx=(0, 8))
        self.cancel_btn.pack(side="left", padx=(0, 8))

    def save_edit(self):
        if not self.selected_menu_item_id:
            return
        name = self.name_var.get().strip()
        price = self.price_var.get()
        if not name or not price:
            messagebox.showerror("Error", "Name and Price are required.")
            return
        try:
            price = float(price)
            cost = float(self.cost_var.get()) if self.cost_var.get() else 0
            prep = int(self.prep_time_var.get()) if self.prep_time_var.get() else 0
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric values.")
            return

        old = self.db.get_menu_item_by_id(self.selected_menu_item_id)
        is_available = old[7] if old else 1

        self.db.update_menu_item(
            self.selected_menu_item_id,
            name,
            self.category_var.get(),
            self.description_var.get(),
            price,
            cost,
            prep,
            is_available,
        )
        messagebox.showinfo("Success", f"'{name}' updated!")
        self.cancel_edit()
        self.refresh_all_data()

    def cancel_edit(self):
        self.editing = False
        self.form_title_label.config(text="Add New Menu Item")
        self.update_btn.pack_forget()
        self.cancel_btn.pack_forget()
        self.add_btn.pack(side="left", padx=(0, 8))
        self.clear_form()

    def delete_menu_item(self):
        if not self.selected_menu_item_id:
            messagebox.showwarning("Warning", "Select an item to delete.")
            return
        if messagebox.askyesno("Confirm", "Permanently delete this menu item?"):
            self.db.delete_menu_item(self.selected_menu_item_id)
            messagebox.showinfo("Success", "Menu item deleted.")
            self.clear_form()
            self.refresh_all_data()

    def clear_form(self):
        self.name_var.set("")
        self.category_var.set("Main Course")
        self.description_var.set("")
        self.price_var.set("")
        self.cost_var.set("")
        self.prep_time_var.set("")
        if self.menu_tree.selection():
            self.menu_tree.selection_remove(self.menu_tree.selection()[0])
        self.selected_menu_item_id = None
        self.recipe_btn.config(state="disabled")

    def open_recipe_editor(self):
        if not self.selected_menu_item_id:
            messagebox.showwarning("Error", "No menu item selected.")
            return
        RecipeEditorWindow(self, self.db, self.selected_menu_item_id)
