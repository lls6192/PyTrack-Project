import sqlite3
import pathlib
from tkinter import messagebox
import logging
from datetime import datetime

db_file = pathlib.Path(r"pytrack_database.db")

if db_file.exists():
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
else:
    messagebox.showerror("Database Error", f"Database file '{db_file}' not found.")
    quit()

def get_location_id(location_name):
    cur.execute("SELECT id FROM locations WHERE name = ?", (location_name,))
    result = cur.fetchone()
    return result[0] if result else None    

def get_locations():
    cur.execute("SELECT DISTINCT name FROM locations ORDER BY name")
    return [row[0] for row in cur.fetchall()]

logging.basicConfig(
    filename="daily_log.txt", \
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def log_sale(Total_price, Quantity, Item):
    logging.info(f"SALE - ITEM:{Item}, Qty: {Quantity}, Total: ${Total_price}")

def log_inventory(item, change, new_stock):
    logging.info(f"INVENTORY - ITEM: {item}, Change: {change}, New Stock: {new_stock}")

def log_action(action_text):
    logging.info(action_text)

def seed_flavors():
    flavors = [
        ("Vanilla",),
        ("Chocolate",),
        ("Cookies & Cream",),
        ("Neapolitan",),
        ("Cookie Dough",)
    ]
    cur.executemany("INSERT OR IGNORE INTO flavors (name) VALUES (?)", flavors)
    conn.commit()

def get_flavor_id(flavor_name):
    cur.execute("SELECT id FROM flavors WHERE name = ?", (flavor_name,))
    result = cur.fetchone()
    return result[0] if result else None

def add_monthly_fixed_costs():
    current_month = datetime.now().strftime("%Y-%m")

    locations = get_locations()
    for location in locations:
        location_id = get_location_id(location)

        # check if fixed costs for this month already exist
        cur.execute("""
            SELECT COUNT(*)
            FROM fixed_costs
            WHERE location_id = ? AND month = ?
        """, (location_id, current_month))
        count = cur.fetchone()[0]

        if count == 0:
            fixed_cost_items = [
                ("Rent per location", 1000, "monthly", current_month, location_id),
                ("Utilities per location", 250, "monthly", current_month, location_id),
                ("Labor per location", 15000, "monthly", current_month, location_id),
                ("Equipment leases per location", 2000, "monthly", current_month, location_id)
            ]

            cur.executemany("""
                INSERT INTO fixed_costs (name, amount, frequency, month, location_id)
                VALUES (?, ?, ?, ?, ?)
            """, fixed_cost_items)

        conn.commit()

def get_total_fixed_costs(location_id, month):
    cur.execute("""
        SELECT SUM(amount) 
        FROM fixed_costs 
        WHERE location_id = ? AND month = ?
    """, (location_id, month))
    result = cur.fetchone()[0]
    return result if result else 0

#Add get fixed costs display
def get_fixed_costs(location_id, month=None):
    if month is None:
        month = datetime.now().strftime("%Y-%m")
    cur.execute (""" 
        SELECT name, amount, frequency, month
        FROM fixed_costs
        WHERE location_id = ? AND month = ?
        ORDER BY name
    """, (location_id, month))
    return cur.fetchall()

seed_flavors()
add_monthly_fixed_costs()