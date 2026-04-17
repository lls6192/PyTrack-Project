import sqlite3
import pathlib
from tkinter import messagebox

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


def fixed_costs():
    cur.execute(""" 
CREATE TABLE IF NOT EXISTS fixed_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT NOT NULL, 
    amount REAL NOT NULL, 
    frequency TEXT NOT NULL 
)
""")

def add_fixed_costs(item, cost, monthly):
    cur.execute("""
    INSERT INTO fixed_costs (item, cost)               
    VALUES (Rent per location, 1000, monthly, Utilities per location, 250, monthly, Labor per location, 15000, monthly, Equipment leases per location, 2000, monthly )               
    """, (item, cost, monthly))