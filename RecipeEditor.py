import tkinter as tk
from tkinter import messagebox, ttk


class RecipeEditorWindow(tk.Toplevel):
    def __init__(self, parent, db, menu_item_id):
        super().__init__(parent)
        self.db = db
        self.menu_item_id = menu_item_id

        menu_item = self.db.get_menu_item_by_id(self.menu_item_id)
        if not menu_item:
            messagebox.showerror("Error", "Could not load menu item.", parent=self)
            self.destroy()
            return

        self.menu_item_name = menu_item[1]

        self.title(f"Recipe Editor \u2014 {self.menu_item_name}")
        self.geometry("650x520")
        self.minsize(550, 400)
        self.configure(bg="#f5f7fa")
        self.transient(parent)
        self.grab_set()

        self._center()
        self.build_ui()
        self.load_inventory_dropdown()
        self.refresh_recipe_list()

    def _center(self):
        self.update_idletasks()
        w, h = 650, 520
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def build_ui(self):
        bg = "#f5f7fa"
        surface = "#ffffff"
        border = "#e2e8f0"
        text_pri = "#0f172a"
        text_sec = "#475569"
        accent = "#2563eb"

        # Header
        hdr = tk.Frame(self, bg=bg)
        hdr.pack(fill="x", padx=24, pady=(20, 16))

        tk.Label(
            hdr,
            text=f"Recipe for {self.menu_item_name}",
            bg=bg,
            fg=text_pri,
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")
        tk.Label(
            hdr,
            text="Define the ingredients needed for this menu item",
            bg=bg,
            fg=text_sec,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(2, 0))

        # Main content
        main = tk.Frame(self, bg=bg)
        main.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # Left: Add ingredient form
        left_card = tk.Frame(
            main,
            bg=surface,
            bd=1,
            relief="solid",
            highlightbackground=border,
            highlightthickness=1,
        )
        left_card.pack(side="left", fill="y", padx=(0, 12))

        tk.Label(
            left_card,
            text="Add Ingredient",
            bg=surface,
            fg=text_pri,
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(14, 10))

        form = tk.Frame(left_card, bg=surface)
        form.pack(fill="x", padx=16, pady=(0, 16))

        tk.Label(
            form,
            text="Ingredient",
            bg=surface,
            fg=text_sec,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(0, 4))
        self.ingredient_var = tk.StringVar()
        self.ingredient_combo = ttk.Combobox(
            form,
            textvariable=self.ingredient_var,
            state="readonly",
            font=("Segoe UI", 10),
            width=24,
        )
        self.ingredient_combo.pack(fill="x", pady=(0, 12))

        tk.Label(
            form,
            text="Quantity Used",
            bg=surface,
            fg=text_sec,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(0, 4))
        self.quantity_var = tk.StringVar()
        ttk.Entry(
            form, textvariable=self.quantity_var, font=("Segoe UI", 10), width=26
        ).pack(fill="x", pady=(0, 16))

        ttk.Button(
            form,
            text="Add Ingredient",
            command=self.add_ingredient,
            style="Accent.TButton",
        ).pack(fill="x")

        # Right: Current recipe
        right_card = tk.Frame(
            main,
            bg=surface,
            bd=1,
            relief="solid",
            highlightbackground=border,
            highlightthickness=1,
        )
        right_card.pack(side="right", fill="both", expand=True, padx=(12, 0))

        tk.Label(
            right_card,
            text="Current Recipe",
            bg=surface,
            fg=text_pri,
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(14, 10))

        tree_frame = tk.Frame(right_card, bg=surface)
        tree_frame.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        self.recipe_tree = ttk.Treeview(
            tree_frame,
            columns=("id", "ingredient", "quantity", "unit"),
            show="headings",
            height=10,
        )
        self.recipe_tree.heading("id", text="ID")
        self.recipe_tree.heading("ingredient", text="Ingredient")
        self.recipe_tree.heading("quantity", text="Qty")
        self.recipe_tree.heading("unit", text="Unit")

        self.recipe_tree.column("id", width=0, stretch=tk.NO)
        self.recipe_tree.column("ingredient", width=160)
        self.recipe_tree.column("quantity", width=70, anchor="center")
        self.recipe_tree.column("unit", width=60, anchor="center")

        scroll = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.recipe_tree.yview
        )
        self.recipe_tree.configure(yscrollcommand=scroll.set)
        self.recipe_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        ttk.Button(
            right_card, text="Remove Selected", command=self.remove_ingredient
        ).pack(fill="x", padx=16, pady=(0, 16))

    def load_inventory_dropdown(self):
        items = self.db.get_inventory()
        self.inventory_map = {item[1]: item[0] for item in items}
        self.ingredient_combo["values"] = sorted(self.inventory_map.keys())

    def refresh_recipe_list(self):
        for row in self.recipe_tree.get_children():
            self.recipe_tree.delete(row)

        recipe_items = self.db.get_recipe_for_item(self.menu_item_id)
        for item in recipe_items:
            # item = (recipe_id, ingredient_id, ingredient_name, quantity_used, unit)
            self.recipe_tree.insert(
                "", "end", values=(item[0], item[2], item[3], item[4])
            )

    def add_ingredient(self):
        name = self.ingredient_var.get()
        qty_str = self.quantity_var.get()

        if not name or not qty_str:
            messagebox.showwarning(
                "Missing Info",
                "Select an ingredient and enter a quantity.",
                parent=self,
            )
            return

        try:
            qty = float(qty_str)
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid", "Enter a valid positive number.", parent=self
            )
            return

        ing_id = self.inventory_map.get(name)
        if not ing_id:
            messagebox.showerror("Error", "Ingredient not found.", parent=self)
            return

        if self.db.add_recipe_item(self.menu_item_id, ing_id, qty):
            self.refresh_recipe_list()
            self.quantity_var.set("")
            self.ingredient_var.set("")
        else:
            messagebox.showerror("Error", "Failed to add ingredient.", parent=self)

    def remove_ingredient(self):
        sel = self.recipe_tree.selection()
        if not sel:
            messagebox.showwarning(
                "No Selection", "Select an ingredient to remove.", parent=self
            )
            return

        recipe_id = self.recipe_tree.item(sel[0])["values"][0]

        if messagebox.askyesno(
            "Confirm", "Remove this ingredient from the recipe?", parent=self
        ):
            if self.db.delete_recipe_item(recipe_id):
                self.refresh_recipe_list()
            else:
                messagebox.showerror(
                    "Error", "Failed to remove ingredient.", parent=self
                )
