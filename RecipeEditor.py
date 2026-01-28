import tkinter as tk
from tkinter import ttk, messagebox


class RecipeEditorWindow(tk.Toplevel):
    def __init__(self, parent, db, menu_item_id):
        super().__init__(parent)
        self.db = db
        self.menu_item_id = menu_item_id

        # Get menu item details
        menu_item = self.db.get_menu_item_by_id(self.menu_item_id)
        if not menu_item:
            messagebox.showerror("Error", "Could not load menu item.", parent=self)
            self.destroy()
            return

        self.menu_item_name = menu_item[1]

        self.title(f"Recipe for {self.menu_item_name}")
        self.geometry("600x500")
        self.transient(parent)  # Keep on top
        self.grab_set()  # Modal behavior

        self.setup_ui()
        self.load_inventory_dropdown()
        self.refresh_recipe_list()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        form_frame = ttk.LabelFrame(main_frame, text="Add Ingredient", padding=15)
        form_frame.pack(side="left", fill="y", padx=(0, 20))

        ttk.Label(form_frame, text="Ingredient:").pack(anchor="w", pady=(0, 5))
        self.ingredient_var = tk.StringVar()
        self.ingredient_combo = ttk.Combobox(
            form_frame,
            textvariable=self.ingredient_var,
            state="readonly",
            width=30
        )
        self.ingredient_combo.pack(fill="x", pady=(0, 15))

        ttk.Label(form_frame, text="Quantity Used:").pack(anchor="w", pady=(0, 5))
        self.quantity_var = tk.StringVar()
        self.quantity_entry = ttk.Entry(form_frame, textvariable=self.quantity_var, width=32)
        self.quantity_entry.pack(fill="x", pady=(0, 15))

        add_btn = ttk.Button(
            form_frame,
            text="Add Ingredient",
            command=self.add_ingredient,
            style="Accent.TButton"
        )
        add_btn.pack(fill="x")

        # --- Right Side: Current Recipe List ---
        list_frame = ttk.LabelFrame(main_frame, text="Current Recipe", padding=15)
        list_frame.pack(side="right", fill="both", expand=True)

        self.recipe_tree = ttk.Treeview(
            list_frame,
            columns=("id", "ingredient", "quantity", "unit"),
            show="headings"
        )
        self.recipe_tree.heading("id", text="ID")
        self.recipe_tree.heading("ingredient", text="Ingredient")
        self.recipe_tree.heading("quantity", text="Quantity")
        self.recipe_tree.heading("unit", text="Unit")

        self.recipe_tree.column("id", width=0, stretch=tk.NO)  # Hide ID
        self.recipe_tree.column("ingredient", width=150)
        self.recipe_tree.column("quantity", width=80)
        self.recipe_tree.column("unit", width=60)

        self.recipe_tree.pack(fill="both", expand=True, pady=(0, 10))

        remove_btn = ttk.Button(
            list_frame,
            text="Remove Selected Ingredient",
            command=self.remove_ingredient
        )
        remove_btn.pack(fill="x")

    def load_inventory_dropdown(self):
        """Populate the combobox with inventory items"""
        inventory_items = self.db.get_inventory()
        # Store (name, id) tuples
        self.inventory_map = {item[1]: item[0] for item in inventory_items}
        self.ingredient_combo['values'] = sorted(self.inventory_map.keys())

    def refresh_recipe_list(self):
        """Reload the recipe items treeview"""
        for row in self.recipe_tree.get_children():
            self.recipe_tree.delete(row)

        recipe_items = self.db.get_recipe_for_item(self.menu_item_id)
        for item in recipe_items:
            # item = (recipe_id, ingredient_name, quantity_used, unit)
            self.recipe_tree.insert("", "end", values=item)

    def add_ingredient(self):
        """Add the selected ingredient from the form to the recipe"""
        ingredient_name = self.ingredient_var.get()
        quantity_str = self.quantity_var.get()

        if not ingredient_name or not quantity_str:
            messagebox.showwarning("Missing Info", "Please select an ingredient and enter a quantity.", parent=self)
            return

        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Please enter a valid, positive number for the quantity.",
                                 parent=self)
            return

        ingredient_id = self.inventory_map.get(ingredient_name)
        if not ingredient_id:
            messagebox.showerror("Error", "Could not find selected ingredient.", parent=self)
            return

        if self.db.add_recipe_item(self.menu_item_id, ingredient_id, quantity):
            self.refresh_recipe_list()
            self.quantity_var.set("")
            self.ingredient_var.set("")
        else:
            messagebox.showerror("Database Error", "Failed to add ingredient to recipe.", parent=self)

    def remove_ingredient(self):
        """Remove the selected ingredient from the recipe"""
        selection = self.recipe_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an ingredient from the list to remove.", parent=self)
            return

        item_data = self.recipe_tree.item(selection[0])
        recipe_id = item_data['values'][0]  # Get the recipe ID

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to remove this ingredient from the recipe?",
                               parent=self):
            if self.db.delete_recipe_item(recipe_id):
                self.refresh_recipe_list()
            else:
                messagebox.showerror("Database Error", "Failed to remove ingredient.", parent=self)