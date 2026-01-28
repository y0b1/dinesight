import sqlite3
from datetime import datetime


class RestaurantDatabaseManager:
    def __init__(self, db_name="dinesight.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                description TEXT,
                price REAL NOT NULL,
                cost REAL,
                preparation_time INTEGER,
                is_available BOOLEAN DEFAULT 1,
                created_date TEXT,
                last_updated TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT,
                category TEXT,
                quantity INTEGER,
                unit_price REAL,
                total_amount REAL,
                order_date TEXT,
                order_time TEXT,
                day_of_week TEXT,
                month TEXT,
                year INTEGER
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ingredient_name TEXT NOT NULL,
                current_stock REAL,
                unit TEXT,
                minimum_threshold REAL,
                cost_per_unit REAL,
                supplier TEXT,
                last_restocked TEXT,
                expiry_date TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                menu_item_id INTEGER NOT NULL,
                ingredient_id INTEGER NOT NULL,
                quantity_used REAL NOT NULL,
                FOREIGN KEY (menu_item_id) REFERENCES menu_items (id) ON DELETE CASCADE,
                FOREIGN KEY (ingredient_id) REFERENCES inventory (id) ON DELETE CASCADE
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT,
                rating INTEGER,
                comment TEXT,
                feedback_date TEXT
            )
        """)

        self.conn.commit()
        self.check_and_update_all_menu_availability()

    # ── Inventory ───────────────────────────────────────────────

    def get_inventory_item_by_id(self, item_id):
        try:
            self.cursor.execute("SELECT * FROM inventory WHERE id=?", (item_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error fetching inventory item by ID: {e}")
            return None

    def add_inventory_item(
        self, name, stock, unit, threshold, cost_per_unit, supplier, expiry_date
    ):
        try:
            last_restocked = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute(
                """
                INSERT INTO inventory
                (ingredient_name, current_stock, unit, minimum_threshold,
                 cost_per_unit, supplier, last_restocked, expiry_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    name,
                    stock,
                    unit,
                    threshold,
                    cost_per_unit,
                    supplier,
                    last_restocked,
                    expiry_date,
                ),
            )
            self.conn.commit()
            self.check_and_update_all_menu_availability()
            return True
        except Exception as e:
            print(f"Error adding inventory item: {e}")
            return False

    def update_inventory_item(
        self, item_id, name, stock, unit, threshold, cost, supplier, expiry
    ):
        try:
            existing = self.get_inventory_item_by_id(item_id)
            if existing and float(stock) > existing[2]:
                last_restocked = datetime.now().strftime("%Y-%m-%d")
            else:
                last_restocked = (
                    existing[7] if existing else datetime.now().strftime("%Y-%m-%d")
                )

            self.cursor.execute(
                """
                UPDATE inventory
                SET ingredient_name=?, current_stock=?, unit=?, minimum_threshold=?,
                    cost_per_unit=?, supplier=?, last_restocked=?, expiry_date=?
                WHERE id=?
            """,
                (
                    name,
                    stock,
                    unit,
                    threshold,
                    cost,
                    supplier,
                    last_restocked,
                    expiry,
                    item_id,
                ),
            )
            self.conn.commit()
            self.check_and_update_all_menu_availability()
            return True
        except Exception as e:
            print(f"Error updating inventory item: {e}")
            return False

    def delete_inventory_item(self, item_id):
        try:
            self.cursor.execute("DELETE FROM inventory WHERE id=?", (item_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting inventory item: {e}")
            return False

    def get_inventory(self, low_stock_only=False):
        try:
            query = "SELECT * FROM inventory"
            if low_stock_only:
                query += " WHERE current_stock <= minimum_threshold"
            query += " ORDER BY ingredient_name"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching inventory: {e}")
            return []

    def update_inventory_stock(self, item_id, new_stock):
        try:
            self.cursor.execute(
                "UPDATE inventory SET current_stock=? WHERE id=?", (new_stock, item_id)
            )
            return True
        except Exception as e:
            print(f"Error updating inventory stock: {e}")
            return False

    # ── Menu Items ──────────────────────────────────────────────

    def add_menu_item(
        self, name, category, description, price, cost, prep_time, is_available=True
    ):
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                """
                INSERT INTO menu_items
                (name, category, description, price, cost, preparation_time,
                 is_available, created_date, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    name,
                    category,
                    description,
                    price,
                    cost,
                    prep_time,
                    int(is_available),
                    now,
                    now,
                ),
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding menu item: {e}")
            return False

    def get_menu_items(self, available_only=False):
        try:
            query = "SELECT * FROM menu_items"
            if available_only:
                query += " WHERE is_available = 1"
            query += " ORDER BY category, name"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching menu items: {e}")
            return []

    def get_menu_item_by_id(self, item_id):
        try:
            self.cursor.execute("SELECT * FROM menu_items WHERE id=?", (item_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error fetching menu item by ID: {e}")
            return None

    def update_menu_item(
        self, item_id, name, category, description, price, cost, prep_time, is_available
    ):
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                """
                UPDATE menu_items
                SET name=?, category=?, description=?, price=?, cost=?,
                    preparation_time=?, is_available=?, last_updated=?
                WHERE id=?
            """,
                (
                    name,
                    category,
                    description,
                    price,
                    cost,
                    prep_time,
                    is_available,
                    now,
                    item_id,
                ),
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating menu item: {e}")
            return False

    def delete_menu_item(self, item_id):
        try:
            self.cursor.execute("DELETE FROM menu_items WHERE id=?", (item_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting menu item: {e}")
            return False

    def update_menu_item_availability(self, item_id, is_available):
        try:
            self.cursor.execute(
                "UPDATE menu_items SET is_available=? WHERE id=?",
                (int(is_available), item_id),
            )
        except Exception as e:
            print(f"Error updating item availability: {e}")

    # ── Sales ───────────────────────────────────────────────────

    def record_sale(
        self, menu_item_id, item_name, category, quantity, unit_price, total_amount
    ):
        try:
            now = datetime.now()
            self.cursor.execute(
                """
                INSERT INTO sales
                (item_name, category, quantity, unit_price, total_amount,
                 order_date, order_time, day_of_week, month, year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    item_name,
                    category,
                    quantity,
                    unit_price,
                    total_amount,
                    now.strftime("%Y-%m-%d"),
                    now.strftime("%H:%M:%S"),
                    now.strftime("%A"),
                    now.strftime("%B"),
                    now.year,
                ),
            )

            recipe = self.get_recipe_for_item(menu_item_id)
            if recipe:
                for recipe_id, ingredient_id, ing_name, quantity_used, unit in recipe:
                    ingredient = self.get_inventory_item_by_id(ingredient_id)
                    if ingredient:
                        new_stock = ingredient[2] - (quantity_used * quantity)
                        self.update_inventory_stock(ingredient_id, new_stock)

            self.conn.commit()
            self.check_and_update_all_menu_availability()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error recording sale: {e}")
            return False

    def get_sales_data(self, date_range=None, category=None):
        try:
            query = "SELECT * FROM sales"
            params = []
            conditions = []
            if date_range:
                conditions.append("order_date BETWEEN ? AND ?")
                params.extend([date_range[0], date_range[1]])
            if category:
                conditions.append("category = ?")
                params.append(category)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY order_date DESC, order_time DESC"
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching sales data: {e}")
            return []

    def get_sales_summary(self):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute(
                "SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM sales WHERE order_date = ?",
                (today,),
            )
            today_count, today_revenue = self.cursor.fetchone()

            this_month = datetime.now().strftime("%Y-%m")
            self.cursor.execute(
                "SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM sales WHERE strftime('%Y-%m', order_date) = ?",
                (this_month,),
            )
            month_count, month_revenue = self.cursor.fetchone()

            self.cursor.execute(
                "SELECT item_name, SUM(quantity) as total_sold FROM sales GROUP BY item_name ORDER BY total_sold DESC LIMIT 1"
            )
            popular = self.cursor.fetchone()

            return {
                "today": {"count": today_count or 0, "revenue": today_revenue or 0},
                "month": {"count": month_count or 0, "revenue": month_revenue or 0},
                "popular_item": popular[0] if popular else "N/A",
            }
        except Exception as e:
            print(f"Error getting sales summary: {e}")
            return {
                "today": {"count": 0, "revenue": 0},
                "month": {"count": 0, "revenue": 0},
                "popular_item": "N/A",
            }

    # ── Analytics ───────────────────────────────────────────────

    def get_category_performance(self):
        try:
            self.cursor.execute("""
                SELECT category, COUNT(*) as orders, SUM(quantity) as items_sold,
                       SUM(total_amount) as revenue
                FROM sales GROUP BY category ORDER BY revenue DESC
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting category performance: {e}")
            return []

    def get_hourly_sales_pattern(self):
        try:
            self.cursor.execute("""
                SELECT strftime('%H', order_time) as hour, COUNT(*) as orders,
                       SUM(total_amount) as revenue
                FROM sales GROUP BY hour ORDER BY hour
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting hourly sales pattern: {e}")
            return []

    def get_daily_sales_trend(self, days=30):
        try:
            # FIX: Use parameterized query instead of string formatting
            self.cursor.execute(
                """
                SELECT order_date, COUNT(*) as orders, SUM(total_amount) as revenue
                FROM sales
                WHERE order_date >= date('now', '-' || ? || ' days')
                GROUP BY order_date ORDER BY order_date
            """,
                (str(days),),
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting daily sales trend: {e}")
            return []

    # ── Recipes ─────────────────────────────────────────────────

    def add_recipe_item(self, menu_item_id, ingredient_id, quantity_used):
        try:
            self.cursor.execute(
                "INSERT INTO recipes (menu_item_id, ingredient_id, quantity_used) VALUES (?, ?, ?)",
                (menu_item_id, ingredient_id, quantity_used),
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding recipe item: {e}")
            return False

    def get_recipe_for_item(self, menu_item_id):
        """Returns: list of (recipe_id, ingredient_id, ingredient_name, quantity_used, unit)"""
        try:
            self.cursor.execute(
                """
                SELECT r.id, i.id as ingredient_id, i.ingredient_name,
                       r.quantity_used, i.unit
                FROM recipes r
                JOIN inventory i ON r.ingredient_id = i.id
                WHERE r.menu_item_id = ?
            """,
                (menu_item_id,),
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting recipe for item: {e}")
            return []

    def delete_recipe_item(self, recipe_id):
        try:
            self.cursor.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting recipe item: {e}")
            return False

    # ── Stock / Availability ────────────────────────────────────

    def check_stock_for_sale(self, menu_item_id, quantity_sold):
        try:
            recipe = self.get_recipe_for_item(menu_item_id)
            if not recipe:
                return True

            for recipe_id, ingredient_id, ing_name, quantity_used, unit in recipe:
                total_needed = quantity_used * quantity_sold
                ingredient = self.get_inventory_item_by_id(ingredient_id)
                if not ingredient or ingredient[2] < total_needed:
                    return False
            return True
        except Exception as e:
            print(f"Error checking stock: {e}")
            return False

    def check_and_update_all_menu_availability(self):
        try:
            menu_items = self.get_menu_items()
            for item in menu_items:
                item_id = item[0]
                currently_available = bool(item[7])
                can_make = self.check_stock_for_sale(item_id, 1)

                if currently_available != can_make:
                    self.update_menu_item_availability(item_id, can_make)
            self.conn.commit()
        except Exception as e:
            print(f"Error updating menu availability: {e}")

    def close(self):
        self.conn.close()


DatabaseManager = RestaurantDatabaseManager
