# DineSight

A desktop restaurant management system built with Python and Tkinter. Designed for small to medium-sized restaurants to track sales, manage menus, monitor inventory, and analyze business trends -- all from a single application.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)

## Features

### Dashboard
- Real-time KPI cards: today's revenue, order count, monthly revenue, top seller
- Revenue trend chart with daily, monthly, and yearly timeframe switching
- Sales by category bar chart
- Smart insights engine that surfaces actionable tips (peak hours, best/worst days, low stock warnings)

### Menu Management
- Add, edit, and delete menu items with category, price, cost, and prep time
- Search and filter the menu list in real time
- Track availability status (auto-managed based on inventory)
- Link recipes to menu items through the recipe editor

### Inventory Management
- Track ingredients with stock levels, units, thresholds, cost, supplier, and expiry dates
- Low stock alerts with visual indicators
- Search and filter inventory
- Automatic menu availability updates when stock changes

### Sales Logger (POS)
- Select menu items and log sales with quantity controls
- Stock validation before recording a sale
- Automatic inventory deduction based on linked recipes
- Searchable sales history with item, quantity, total, date, and time

### Trends & Insights
- Peak hours analysis chart
- Top 5 selling items with visual ranking
- Weekly sales pattern by day of week
- Growth trend calculation (last 30 days vs previous 30 days)
- Key insight cards: peak hour, best day, average order value, growth percentage

### Recipe Editor
- Modal editor to define ingredient requirements per menu item
- Select ingredients from inventory, set quantities
- Add and remove recipe components
- Drives stock validation and automatic deduction on sale

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.9+ |
| GUI | Tkinter + sv-ttk (Sun Valley theme) |
| Charts | Matplotlib (embedded via FigureCanvasTkAgg) |
| Database | SQLite (local file, zero config) |

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/dinesight.git
   cd dinesight
   ```

2. Install dependencies:
   ```
   pip install matplotlib sv-ttk
   ```
   `tkinter` and `sqlite3` are included with Python.

3. Run the application:
   ```
   python main.py
   ```

The database file (`dinesight.db`) is created automatically on first launch.

## Project Structure

```
dinesight/
  main.py                      # Application entry point, sidebar navigation, theming
  Dashboard.py                 # KPI cards, revenue/category charts, smart insights
  MenuTracker.py               # Menu CRUD, search, recipe management
  InventoryManagement.py       # Inventory CRUD, low stock alerts, search
  SalesLogger.py               # POS interface, sale logging, stock validation
  TrendsAnalysis.py            # Peak hours, top items, weekly patterns, growth
  RecipeEditor.py              # Modal ingredient-to-menu linking
  RestaurantDatabaseManager.py # SQLite schema, queries, business logic
  dinesight.db                 # SQLite database (auto-created)
  SYSTEM_USER_MANUAL.txt       # Detailed user manual
```

## Database Schema

- **menu_items** -- name, category, description, price, cost, prep time, availability
- **sales** -- item, category, quantity, price, total, date/time, day of week
- **inventory** -- ingredient, stock, unit, threshold, cost, supplier, expiry
- **recipes** -- links menu items to inventory ingredients with quantities
- **customer_feedback** -- item ratings and comments

## Getting Started

1. **Add inventory** -- go to Inventory and add your ingredients with stock levels and minimum thresholds
2. **Create menu items** -- go to Menu Tracker and add your dishes with prices
3. **Link recipes** -- select a menu item and click "Manage Recipe" to define which ingredients it uses
4. **Log sales** -- go to Sales Logger, select items, and record transactions
5. **Review analytics** -- check the Dashboard and Trends pages for business insights

## License

This project is provided as-is for educational and personal use.
