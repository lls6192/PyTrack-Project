from tkinter import *
from tkinter import ttk
from tkinter import messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
from datetime import datetime
from database import get_location_id, conn, cur, get_locations, get_flavor_id, log_inventory, log_sale, log_action, get_fixed_costs, get_total_fixed_costs, get_consumable_id
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from theme import (
    fonts, COLORS,
    style_primary_button, style_secondary_button, style_ghost_button,
    style_label, style_entry, style_toplevel, hairline,
)

# cost per 5-gal bucket
flavor_costs = {
    "Vanilla": 1.80,
    "Chocolate": 1.80,
    "Cookies & Cream": 1.90,
    "Neapolitan": 1.85,
    "Cookie Dough": 1.95
}

# cost per BOX (100 count)
consumable_costs = {
    "Standard Ice Cream Cone": 5.00,
    "Waffle Cone": 6.00,
    "Dish with Spoon": 4.50
}

napkin_cost_per_box = 20


# ---- small visual helper used inside this module ------------------------
def _section_header(parent, eyebrow_text, heading_text, bg=None):
    """A small two-line header (eyebrow + heading) used in popup windows."""
    bg = bg or COLORS["bg_main"]
    eb = Label(parent, text=eyebrow_text)
    eb.configure(font=fonts["section"], fg=COLORS["accent"], bg=bg)
    eb.pack(anchor="w")
    hd = Label(parent, text=heading_text)
    style_label(hd, "heading", bg=bg)
    hd.pack(anchor="w", pady=(2, 0))
    return eb, hd


def _form_row(parent, row_index):
    """Returns a frame that lays out a single form row consistently."""
    f = Frame(parent, bg=COLORS["bg_card"])
    f.grid(row=row_index, column=0, sticky="ew", padx=2, pady=4)
    return f


def _styled_combobox(parent, **kw):
    """ttk.Combobox already gets theme styling via apply_theme()."""
    return ttk.Combobox(parent, **kw)


class LocationPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.location_name = ""

        self.controller = controller

        # outer wrapper for padding
        wrapper = Frame(self, bg=COLORS["bg_main"])
        wrapper.pack(fill="both", expand=True, padx=40, pady=30)

        # ---------- Header ----------
        header = Frame(wrapper, bg=COLORS["bg_main"])
        header.pack(fill="x")

        eyebrow = Label(header, text="STORE LOCATION")
        eyebrow.configure(font=fonts["section"], fg=COLORS["accent"], bg=COLORS["bg_main"])
        eyebrow.pack(anchor="w")

        self.title_label = Label(header, text=f"{self.location_name or '—'}")
        style_label(self.title_label, "title")
        self.title_label.pack(anchor="w", pady=(2, 0))

        subtitle = Label(header, text="Manage inventory, log sales, and review reports for this location.")
        style_label(subtitle, "subtitle")
        subtitle.pack(anchor="w", pady=(2, 0))

        hairline(wrapper).pack(fill="x", pady=(18, 18))

        # ---------- Action grid (three sections, three buttons each) ----------
        # Each "card" is a section with an eyebrow label + a row of styled buttons.
        # All buttons retain the same handlers and behavior as the original.
        actions = Frame(wrapper, bg=COLORS["bg_main"])
        actions.pack(fill="both", expand=True)
        for c in range(3):
            actions.columnconfigure(c, weight=1, uniform="action")

        def _make_section(col, eyebrow_text, heading_text, buttons):
            card = Frame(
                actions, bg=COLORS["bg_card"],
                highlightbackground=COLORS["border"], highlightthickness=1,
            )
            card.grid(row=0, column=col, sticky="nsew",
                      padx=(0 if col == 0 else 8, 0 if col == 2 else 8))
            inner = Frame(card, bg=COLORS["bg_card"])
            inner.pack(fill="both", expand=True, padx=18, pady=16)

            eb = Label(inner, text=eyebrow_text)
            eb.configure(font=fonts["section"], fg=COLORS["accent"], bg=COLORS["bg_card"])
            eb.pack(anchor="w")

            hd = Label(inner, text=heading_text)
            style_label(hd, "heading", bg=COLORS["bg_card"])
            hd.pack(anchor="w", pady=(2, 14))

            for label, cmd, kind in buttons:
                b = Button(inner, text=label, command=cmd)
                if kind == "primary":
                    style_primary_button(b)
                else:
                    style_secondary_button(b)
                b.pack(anchor="w", fill="x", pady=4)

            return card

        # Section 1 — Inventory
        _make_section(
            0, "INVENTORY", "Stock & supplies",
            [
                ("Restock Flavor Inventory", self.restock_flavor_inventory, "primary"),
                ("Restock Consumables",     self.restock_consumables_inventory, "secondary"),
                ("View Inventory Levels",   self.view_inventory, "secondary"),
            ],
        )

        # Section 2 — Sales
        _make_section(
            1, "SALES", "Daily activity",
            [
                ("Enter Daily Sales",   self.enter_daily_sales, "primary"),
                ("View Daily Sales",    self.view_daily_sales, "secondary"),
                ("Flavor Sales Trends", self.show_flavor_trends, "secondary"),
            ],
        )

        # Section 3 — Reports & logs
        _make_section(
            2, "REPORTS", "Financials & history",
            [
                ("Monthly Income Statement", self.generate_report, "primary"),
                ("View Fixed Costs",         self.view_fixed_costs, "secondary"),
                ("View History Log",         self.view_history_log, "secondary"),
            ],
        )

        # ---------- Footer: back button ----------
        footer = Frame(wrapper, bg=COLORS["bg_main"])
        footer.pack(fill="x", pady=(22, 0))

        btn_back = Button(
            footer,
            text="←  Back to locations",
            command=lambda: controller.show_frame("StartPage"),
        )
        style_ghost_button(btn_back)
        btn_back.pack(anchor="w")

    # ---------------------------------------------------------------- restock
    def restock_flavor_inventory(self):
        # Quantity and Flavor Restocked, and Date/Time
        restock_window = Toplevel(self)
        style_toplevel(restock_window, "Restock Flavor Inventory")
        restock_window.geometry("620x340")
        restock_window.grab_set()  # Make the restock window modal

        flavor_options = [
            "Vanilla",
            "Chocolate",
            "Cookies & Cream",
            "Neapolitan",
            "Cookie Dough"
        ]

        # outer padding
        outer = Frame(restock_window, bg=COLORS["bg_main"])
        outer.pack(fill="both", expand=True, padx=24, pady=20)

        _section_header(outer, "INVENTORY", "Restock Flavor Inventory")

        hairline(outer).pack(fill="x", pady=(14, 14))

        # white card containing the rows
        card = Frame(outer, bg=COLORS["bg_card"],
                     highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        rows_frame = Frame(card, bg=COLORS["bg_card"])
        rows_frame.pack(fill="both", expand=True, padx=18, pady=14)

        restock_rows = []

        def add_restock_row():
            row_index = len(restock_rows)
            flavor_var = StringVar()

            flavor_label = Label(rows_frame, text="Flavor")
            style_label(flavor_label, "small", bg=COLORS["bg_card"])
            flavor_label.grid(row=row_index, column=0, padx=(0, 6), pady=6, sticky="w")

            flavor_dropdown = ttk.Combobox(
                rows_frame,
                textvariable=flavor_var,
                values=flavor_options,
                state="readonly",
                width=18,
            )
            flavor_dropdown.grid(row=row_index, column=1, padx=6, pady=6, sticky="w")
            flavor_dropdown.set("Select a flavor")

            quantity_label = Label(rows_frame, text="Buckets")
            style_label(quantity_label, "small", bg=COLORS["bg_card"])
            quantity_label.grid(row=row_index, column=2, padx=(18, 6), pady=6, sticky="w")

            quantity_entry = Entry(rows_frame, width=6)
            style_entry(quantity_entry)
            quantity_entry.grid(row=row_index, column=3, padx=6, pady=6, sticky="w")
            restock_rows.append((flavor_var, quantity_entry))

        def submit_restock():
            total_cost = 0

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            location_id = get_location_id(self.location_name)

            valid_entries = []

            for flavor_var, quantity_entry in restock_rows:
                flavor = flavor_var.get().strip()
                quantity_text = quantity_entry.get().strip()

                if flavor == "Select a flavor":
                    messagebox.showerror("Error", "Please select a flavor for all entries.")
                    return

                if quantity_text == "":
                    messagebox.showerror("Error", "Quantity cannot be empty.")
                    return

                if not quantity_text.isdigit():
                    messagebox.showerror("Error", "Quantity must be a whole number.")
                    return

                quantity = int(quantity_text)
                valid_entries.append((flavor, quantity))

            if not valid_entries:
                messagebox.showerror("Error", "Please add at least one flavor to restock.")
                return

            for entry in valid_entries:
                flavor, quantity = entry

                cost_per_bucket = flavor_costs.get(flavor, 0)
                total_cost += quantity * cost_per_bucket

                flavor_id = get_flavor_id(flavor)
                # convert from number of 5-gallon buckets to number of scoops (assuming 1 bucket = 32 scoops)
                quantity = quantity * 160

                # check to see if the flavor already exists
                cur.execute("""
                    SELECT id, quantity FROM flavor_inventory
                    WHERE location_id = ? AND flavor_id = ?
                """, (location_id, flavor_id))
                existing_row = cur.fetchone()

                if existing_row:
                    inventory_id, existing_quantity = existing_row
                    new_quantity = existing_quantity + quantity
                    cur.execute("""
                        UPDATE flavor_inventory
                        SET quantity = ?, timestamp = ?
                        WHERE id = ?
                    """, (new_quantity, timestamp, inventory_id))
                else:
                    cur.execute("INSERT INTO flavor_inventory (location_id, flavor, flavor_id, quantity, timestamp) VALUES (?, ?, ?, ?, ?)",
                                (location_id, flavor, flavor_id, quantity, timestamp))
            conn.commit()

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cur.execute("""
                INSERT INTO costs (location_id, category, description, transaction_type, amount, datetime)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                location_id,
                "Inventory",
                "Flavor Restock",
                "Expense",
                total_cost,
                timestamp
            ))
            conn.commit()

            log_inventory(flavor, quantity, f"New inventory for {flavor} at {self.location_name}: {quantity} scoops")

            messagebox.showinfo(
                "Restock Saved",
                f"Inventory restocked for {self.location_name}"
            )
            restock_window.destroy()

        add_restock_row()  # Add the first row by default

        # add another flavor button
        add_button = Button(card, text="+  Add another flavor", command=add_restock_row)
        style_ghost_button(add_button)
        add_button.pack(anchor="w", padx=18, pady=(0, 12))

        # OK / Cancel buttons
        button_frame = Frame(outer, bg=COLORS["bg_main"])
        button_frame.pack(fill="x", pady=(14, 0))

        cancel_button = Button(button_frame, text="Cancel", width=10, command=restock_window.destroy)
        style_ghost_button(cancel_button)
        cancel_button.pack(side="right")

        ok_button = Button(button_frame, text="Save Restock", width=14, command=submit_restock)
        style_primary_button(ok_button)
        ok_button.pack(side="right", padx=(0, 8))

    # ----------------------------------------------------- restock consumables
    def restock_consumables_inventory(self):
        restock_consumables_window = Toplevel(self)
        style_toplevel(restock_consumables_window, "Restock Consumables Inventory")
        restock_consumables_window.geometry("680x340")
        restock_consumables_window.grab_set()

        consumables_options = [
            "Standard Ice Cream Cone",
            "Waffle Cone",
            "Dish with Spoon",
            "Napkins"
        ]

        outer = Frame(restock_consumables_window, bg=COLORS["bg_main"])
        outer.pack(fill="both", expand=True, padx=24, pady=20)

        _section_header(outer, "INVENTORY", "Restock Consumables")

        hairline(outer).pack(fill="x", pady=(14, 14))

        card = Frame(outer, bg=COLORS["bg_card"],
                     highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        rows_frame = Frame(card, bg=COLORS["bg_card"])
        rows_frame.pack(fill="both", expand=True, padx=18, pady=14)

        restock_consumables_rows = []

        def add_restock_consumables_row():
            row_index = len(restock_consumables_rows)
            consumable_var = StringVar()

            consumable_label = Label(rows_frame, text="Consumable")
            style_label(consumable_label, "small", bg=COLORS["bg_card"])
            consumable_label.grid(row=row_index, column=0, padx=(0, 6), pady=6, sticky="w")

            consumable_dropdown = ttk.Combobox(
                rows_frame,
                textvariable=consumable_var,
                values=consumables_options,
                state="readonly",
                width=22,
            )
            consumable_dropdown.grid(row=row_index, column=1, padx=6, pady=6, sticky="w")
            consumable_dropdown.set("Select a consumable")

            quantity_label = Label(rows_frame, text="Boxes")
            style_label(quantity_label, "small", bg=COLORS["bg_card"])
            quantity_label.grid(row=row_index, column=2, padx=(18, 6), pady=6, sticky="w")

            quantity_entry = Entry(rows_frame, width=6)
            style_entry(quantity_entry)
            quantity_entry.grid(row=row_index, column=3, padx=6, pady=6, sticky="w")

            restock_consumables_rows.append((consumable_var, quantity_entry))

        def submit_consumables_restock():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            location_id = get_location_id(self.location_name)

            total_cost = 0

            valid_entries = []

            for consumable_var, quantity_entry in restock_consumables_rows:
                consumable = consumable_var.get().strip()
                quantity_text = quantity_entry.get().strip()

                if consumable == "Select a consumable":
                    messagebox.showerror("Error", "Please select a consumable for all entries.")
                    return

                if quantity_text == "":
                    messagebox.showerror("Error", "Quantity cannot be empty.")
                    return

                if not quantity_text.isdigit():
                    messagebox.showerror("Error", "Quantity must be a whole number.")
                    return

                quantity = int(quantity_text)
                valid_entries.append((consumable, quantity))

            if not valid_entries:
                messagebox.showerror("Error", "Please add at least one consumable to restock.")
                return

            for entry in valid_entries:
                consumable, quantity = entry
                consumable_id = get_consumable_id(consumable)

                if consumable == "Napkins":
                    total_cost += quantity * 20
                else:
                    cost_per_box = consumable_costs.get(consumable, 0)
                    total_cost += quantity * cost_per_box

                # if standard ice cream cone, waffle cone, or dish with spoon convert each restock has 100 count
                if consumable in ["Standard Ice Cream Cone", "Waffle Cone", "Dish with Spoon"]:
                    quantity = quantity * 100
                else:
                    quantity = quantity * 10000  # for napkins, each restock has 10,000 count

                # check to see if the consumable already exists
                cur.execute("""
                    SELECT id, quantity FROM consumables_inventory
                    WHERE location_id = ? AND consumable_id = ?
                """, (location_id, consumable_id))
                existing_row = cur.fetchone()

                if existing_row:
                    inventory_id, existing_quantity = existing_row
                    new_quantity = existing_quantity + quantity
                    cur.execute("""
                        UPDATE consumables_inventory
                        SET quantity = ?, timestamp = ?
                        WHERE id = ?
                    """, (new_quantity, timestamp, inventory_id))
                else:
                    cur.execute("INSERT INTO consumables_inventory (location_id, consumable, consumable_id, quantity, timestamp) VALUES (?, ?, ?, ?, ?)",
                                (location_id, consumable, consumable_id, quantity, timestamp))
            conn.commit()

            log_inventory(consumable, quantity, f"New inventory for {consumable} at {self.location_name}: {quantity} items")

            cur.execute("""
                INSERT INTO costs (location_id, category, description, transaction_type, amount, datetime)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                location_id,
                "Inventory",
                "Consumables Restock",
                "Expense",
                total_cost,
                timestamp
            ))
            conn.commit()

            messagebox.showinfo(
                "Restock Saved",
                f"Consumables inventory restocked for {self.location_name}"
            )
            restock_consumables_window.destroy()

        add_restock_consumables_row()  # Add the first row by default

        add_button = Button(card, text="+  Add another consumable", command=add_restock_consumables_row)
        style_ghost_button(add_button)
        add_button.pack(anchor="w", padx=18, pady=(0, 12))

        # OK / Cancel buttons
        button_frame = Frame(outer, bg=COLORS["bg_main"])
        button_frame.pack(fill="x", pady=(14, 0))

        cancel_button = Button(button_frame, text="Cancel", width=10, command=restock_consumables_window.destroy)
        style_ghost_button(cancel_button)
        cancel_button.pack(side="right")

        ok_button = Button(button_frame, text="Save Restock", width=14, command=submit_consumables_restock)
        style_primary_button(ok_button)
        ok_button.pack(side="right", padx=(0, 8))

    # --------------------------------------------------------- enter daily sales
    def enter_daily_sales(self):
        # Flavors and Quantitiies Sold
        daily_sales_window = Toplevel(self)
        style_toplevel(daily_sales_window, "Enter Daily Sales")
        daily_sales_window.geometry("980x320")
        daily_sales_window.grab_set()  # Make the daily sales window modal

        flavor_options = [
            "Vanilla",
            "Chocolate",
            "Cookies & Cream",
            "Neapolitan",
            "Cookie Dough"
        ]

        size_options = ["Kiddie", "Small", "Medium", "Large"]

        size_prices = {
            "Kiddie": 3.00,
            "Small": 3.50,
            "Medium": 4.00,
            "Large": 4.50
        }

        # for inventory quanity tracked in scoops
        size_inventory_use = {
            "Kiddie": 1,
            "Small": 2,
            "Medium": 3,
            "Large": 4
        }

        # Cones/Container
        cone_container_options = ["Standard Ice Cream Cone", "Waffle Cone", "Dish with Spoon"]

        outer = Frame(daily_sales_window, bg=COLORS["bg_main"])
        outer.pack(fill="both", expand=True, padx=24, pady=20)

        _section_header(outer, "SALES", "Enter Daily Sales")

        hairline(outer).pack(fill="x", pady=(14, 14))

        card = Frame(outer, bg=COLORS["bg_card"],
                     highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        row_frame = Frame(card, bg=COLORS["bg_card"])
        row_frame.pack(fill="both", expand=True, padx=18, pady=14)

        daily_sales_rows = []

        def add_daily_sales_row():
            row_index = len(daily_sales_rows)

            flavor_var = StringVar()
            size_var = StringVar()

            flavor_label = Label(row_frame, text="Flavor")
            style_label(flavor_label, "small", bg=COLORS["bg_card"])
            flavor_label.grid(row=row_index, column=0, padx=(0, 6), pady=6, sticky="w")

            flavor_dropdown = ttk.Combobox(
                row_frame,
                textvariable=flavor_var,
                values=flavor_options,
                state="readonly",
                width=14
            )
            flavor_dropdown.grid(row=row_index, column=1, padx=6, pady=6, sticky="w")
            flavor_dropdown.set("Select a flavor")

            size_label = Label(row_frame, text="Size")
            style_label(size_label, "small", bg=COLORS["bg_card"])
            size_label.grid(row=row_index, column=2, padx=(14, 6), pady=6, sticky="w")

            size_dropdown = ttk.Combobox(
                row_frame,
                textvariable=size_var,
                values=size_options,
                state="readonly",
                width=10
            )
            size_dropdown.grid(row=row_index, column=3, padx=6, pady=6, sticky="w")
            size_dropdown.set("Select a size")

            quantity_label = Label(row_frame, text="Qty")
            style_label(quantity_label, "small", bg=COLORS["bg_card"])
            quantity_label.grid(row=row_index, column=4, padx=(14, 6), pady=6, sticky="w")

            quantity_entry = Entry(row_frame, width=5)
            style_entry(quantity_entry)
            quantity_entry.grid(row=row_index, column=5, padx=6, pady=6, sticky="w")

            cone_label = Label(row_frame, text="Cone / dish")
            style_label(cone_label, "small", bg=COLORS["bg_card"])
            cone_label.grid(row=row_index, column=6, padx=(14, 6), pady=6, sticky="w")

            cone_container_entry = ttk.Combobox(
                row_frame,
                values=cone_container_options,
                state="readonly",
                width=22
            )
            cone_container_entry.grid(row=row_index, column=7, padx=6, pady=6, sticky="w")
            cone_container_entry.set("Select cone/container")

            daily_sales_rows.append((flavor_var, size_var, quantity_entry, cone_container_entry))

        def submit_daily_sales():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            location_id = get_location_id(self.location_name)

            valid_entries = []

            for flavor_var, size_var, quantity_entry, cone_container_entry in daily_sales_rows:

                flavor = flavor_var.get().strip()
                quantity_text = quantity_entry.get().strip()
                size = size_var.get().strip()

                if flavor == "Select a flavor":
                    messagebox.showerror("Error", "Please select a flavor.")
                    return

                if size == "Select a size":
                    messagebox.showerror("Error", "Please select a size.")
                    return

                if quantity_text == "":
                    messagebox.showerror("Error", "Quantity cannot be empty.")
                    return

                if not quantity_text.isdigit():
                    messagebox.showerror("Error", "Quantity must be a whole number.")
                    return

                if cone_container_entry.get() == "Select cone/container":
                    messagebox.showerror("Error", "Please select a cone/container option.")
                    return

                quantity = int(quantity_text)

                # find flavor_id
                cur.execute("SELECT id FROM flavors WHERE name = ?", (flavor,))
                flavor_row = cur.fetchone()

                if flavor_row is None:
                    messagebox.showerror("Error", f"Flavor '{flavor}' is not in the database.")
                    return
                flavor_id = flavor_row[0]

                # how much inventory to remove
                inventory_use = size_inventory_use[size] * quantity
                inventory_container_use = quantity

                # check current inventory
                cur.execute("SELECT quantity FROM flavor_inventory WHERE location_id = ? AND flavor_id = ?", (location_id, flavor_id))
                inventory_row = cur.fetchone()

                current_inventory = inventory_row[0] if inventory_row else 0

                if current_inventory < inventory_use:
                    messagebox.showerror("Error", f"Insufficient inventory for flavor '{flavor}'.")
                    return

                # check inventory for cones/containers
                cur.execute("SELECT quantity FROM consumables_inventory WHERE location_id = ? AND consumable = ?", (location_id, cone_container_entry.get()))
                container_inventory_row = cur.fetchone()

                current_container_inventory = container_inventory_row[0] if container_inventory_row else 0

                if current_container_inventory < inventory_container_use:
                    messagebox.showerror("Error", f"Insufficient inventory for cone/container '{cone_container_entry.get()}'.")
                    return

                revenue = size_prices[size] * quantity

                valid_entries.append({
                    "flavor_id": flavor_id,
                    "flavor": flavor,
                    "size": size,
                    "quantity": quantity,
                    "inventory_needed": inventory_use,
                    "revenue": revenue,
                    "cone_container": cone_container_entry.get(),
                    "container_inventory_needed": inventory_container_use
                })

            if not valid_entries:
                messagebox.showerror("Error", "Please add at least one flavor sold.")
                return

            # add to database
            try:
                for entry in valid_entries:
                    # insert into sales table
                    cur.execute("""
                    INSERT INTO sales (location_id, flavor_id, quantity, revenue, datetime, size, container)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        location_id,
                        entry["flavor_id"],
                        entry["quantity"],
                        entry["revenue"],
                        timestamp,
                        entry["size"],
                        entry["cone_container"]
                    ))

                    # insert sales into costs table as revenue
                    cur.execute("""
                        INSERT INTO costs (location_id, category, description, transaction_type, amount, datetime)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        location_id,
                        "Sales",
                        f"{entry['quantity']} {entry['size']} {entry['flavor']} sold",
                        "Revenue",
                        entry["revenue"],
                        timestamp
                    ))

                    # subtract from flavor inventory
                    cur.execute("""
                        UPDATE flavor_inventory
                        SET quantity = quantity - ?
                        WHERE location_id = ? AND flavor_id = ?
                        """, (
                        entry["inventory_needed"],
                        location_id,
                        entry["flavor_id"]
                    ))

                    # subtract from cone/container inventory
                    cur.execute("""
                        UPDATE consumables_inventory
                        SET quantity = quantity - ?
                        WHERE location_id = ? AND consumable = ?
                    """, (
                        entry["container_inventory_needed"],
                        location_id,
                        entry["cone_container"]
                    ))

                    # subtract napkins (2 per order)
                    cur.execute("""
                        UPDATE consumables_inventory
                        SET quantity = quantity - ?
                        WHERE location_id = ? AND consumable = ?
                    """, (
                        entry["quantity"] * 2,
                        location_id,
                        "Napkins"
                    ))

                    # check napkins inventory
                    cur.execute("""
                        SELECT quantity
                        FROM consumables_inventory
                        WHERE location_id = ? AND consumable = ?
                    """, (
                        location_id,
                        "Napkins"
                    ))

                    napkin_row = cur.fetchone()
                    napkin_qty = napkin_row[0] if napkin_row else 0

                    if napkin_qty < 50:
                        messagebox.showwarning(
                            "Low Inventory Warning",
                            f"Inventory for napkins is low ({napkin_qty} remaining). Please restock soon."
                        )

                    # check updated flavor inventory level
                    cur.execute("""
                        SELECT quantity FROM flavor_inventory
                        WHERE location_id = ? AND flavor_id = ?
                    """, (location_id, entry["flavor_id"]))

                    updated_quantity = cur.fetchone()[0]

                    # check flavor inventory
                    if updated_quantity < 20:
                        messagebox.showwarning(
                            "Low Inventory Warning",
                            f"Inventory for flavor '{entry['flavor']}' is low ({updated_quantity} scoops remaining). Please restock soon."
                        )

                    # check updated cone/container inventory level
                    cur.execute("""
                        SELECT quantity FROM consumables_inventory
                        WHERE location_id = ? AND consumable = ?
                    """, (location_id, entry["cone_container"]))
                    updated_container_quantity = cur.fetchone()[0]
                    if updated_container_quantity < 20:
                        messagebox.showwarning(
                            "Low Inventory Warning",
                            f"Inventory for cone/container '{entry['cone_container']}' is low ({updated_container_quantity} remaining). Please restock soon."
                        )

                conn.commit()

                log_sale(entry["revenue"], entry["quantity"], f"{entry['size']} {entry['flavor']}")

                messagebox.showinfo(
                    "Daily Sales Saved",
                    f"Daily sales entered for {self.location_name}"
                )
                daily_sales_window.destroy()

            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"An error occurred while saving daily sales: {str(e)}")

        add_daily_sales_row()  # Add the first row by default

        add_daily_sales_button = Button(card, text="+  Add another sale", command=add_daily_sales_row)
        style_ghost_button(add_daily_sales_button)
        add_daily_sales_button.pack(anchor="w", padx=18, pady=(0, 12))

        # Buttons frame
        button_frame = Frame(outer, bg=COLORS["bg_main"])
        button_frame.pack(fill="x", pady=(14, 0))

        cancel_button = Button(button_frame, text="Cancel", width=10, command=daily_sales_window.destroy)
        style_ghost_button(cancel_button)
        cancel_button.pack(side="right")

        ok_button = Button(button_frame, text="Save Sales", width=14, command=submit_daily_sales)
        style_primary_button(ok_button)
        ok_button.pack(side="right", padx=(0, 8))

        # If inventory is low, alert the user to restock
        print(f"Enter Daily Sales for {self.location_name}")

    # ---------------------------------------------------------- view fixed costs
    # View the fixed costs current location ID, month and shows this information in a table
    def view_fixed_costs(self):
        if not self.location_name:
            messagebox.showerror("Error", "Please select a location first.")
            return

        location_id = get_location_id(self.location_name)
        current_month = datetime.now().strftime("%Y-%m")

        fixed_cost_rows = get_fixed_costs(location_id, current_month)
        total_fixed_costs = get_total_fixed_costs(location_id, current_month)

        fixed_costs_window = Toplevel(self)
        style_toplevel(fixed_costs_window, f"Fixed Costs · {self.location_name}")
        fixed_costs_window.geometry("760x420")
        fixed_costs_window.grab_set()

        outer = Frame(fixed_costs_window, bg=COLORS["bg_main"])
        outer.pack(fill="both", expand=True, padx=24, pady=20)

        _section_header(outer, "REPORT", f"Fixed Costs · {self.location_name}")

        sub = Label(outer, text=f"Reporting period · {current_month}")
        style_label(sub, "subtitle")
        sub.pack(anchor="w", pady=(2, 0))

        hairline(outer).pack(fill="x", pady=(14, 14))

        columns = ("name", "amount", "frequency", "month")
        tree = ttk.Treeview(outer, columns=columns, show="headings", height=10)

        tree.heading("name", text="Cost Name")
        tree.heading("amount", text="Amount")
        tree.heading("frequency", text="Frequency")
        tree.heading("month", text="Month")

        tree.column("name", width=280)
        tree.column("amount", width=120, anchor="center")
        tree.column("frequency", width=120, anchor="center")
        tree.column("month", width=120, anchor="center")

        for row in fixed_cost_rows:
            name, amount, frequency, month = row
            tree.insert("", END, values=(name, f"${amount:,.2f}", frequency, month))

        tree.pack(fill="both", expand=True)

        # Total row
        total_row = Frame(outer, bg=COLORS["bg_main"])
        total_row.pack(fill="x", pady=(14, 0))
        l = Label(total_row, text="Total Fixed Costs")
        style_label(l, "body_bold")
        l.pack(side="left")
        l = Label(total_row, text=f"${total_fixed_costs:,.2f}")
        l.configure(font=fonts["report_bold"], fg=COLORS["accent"], bg=COLORS["bg_main"])
        l.pack(side="right")

        close_btn = Button(outer, text="Close", width=10, command=fixed_costs_window.destroy)
        style_ghost_button(close_btn)
        close_btn.pack(pady=(14, 0))

        log_action(f"VIEW FIXED COSTS - {self.location_name} for {current_month}")

    # ----------------------------------------------------------- view history log
    def view_history_log(self):
        log_file = Path("daily_log.txt")

        history_window = Toplevel(self)
        style_toplevel(history_window, f"History Log · {self.location_name}")
        history_window.geometry("840x500")
        history_window.grab_set()

        outer = Frame(history_window, bg=COLORS["bg_main"])
        outer.pack(fill="both", expand=True, padx=24, pady=20)

        _section_header(outer, "LOG", "System History Log")

        hairline(outer).pack(fill="x", pady=(14, 14))

        # Card around the scrolled text
        card = Frame(outer, bg=COLORS["bg_card"],
                     highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        log_text = ScrolledText(
            card, wrap=WORD,
            bg=COLORS["bg_card"], fg=COLORS["text_primary"],
            font=fonts["small"],
            relief="flat", borderwidth=0,
            padx=14, pady=12,
            insertbackground=COLORS["text_primary"],
        )
        log_text.pack(fill="both", expand=True)

        if log_file.exists():
            with open(log_file, "r") as file:
                contents = file.read().strip()
                if contents:
                    log_text.insert(END, contents)
                else:
                    log_text.insert(END, "The history log is currently empty.")
        else:
            log_text.insert(END, "No log file found yet.")

        log_text.config(state="disabled")

        close_btn = Button(outer, text="Close", width=10, command=history_window.destroy)
        style_ghost_button(close_btn)
        close_btn.pack(pady=(14, 0))

    # ---------------------------------------------------------- generate report
    def generate_report(self):
        if not self.location_name:
            messagebox.showerror("Error", "Please select a location first.")
            return

        location_id = get_location_id(self.location_name)
        current_month = datetime.now().strftime("%Y-%m")

        # sales revenue from costs table
        cur.execute("""
            SELECT SUM(amount)
            FROM costs
            WHERE location_id = ?
            AND transaction_type = 'Revenue'
            AND substr(datetime, 1, 7) = ?
        """, (location_id, current_month))
        total_revenue = cur.fetchone()[0] or 0

        # all expenses from costs table
        cur.execute("""
            SELECT SUM(amount)
            FROM costs
            WHERE location_id = ?
            AND substr(datetime, 1, 7) = ?
            AND transaction_type = 'Expense'
        """, (location_id, current_month))
        total_expenses = cur.fetchone()[0] or 0

        net_income = total_revenue - total_expenses

        # expense breakdown by category
        cur.execute("""
            SELECT category, SUM(amount)
            FROM costs
            WHERE location_id = ?
            AND transaction_type = 'Expense'
            AND substr(datetime, 1, 7) = ?
            GROUP BY category
        """, (location_id, current_month))
        expense_rows = cur.fetchall()

        # ------ Report window UI ------
        report_window = Toplevel(self)
        style_toplevel(report_window, f"Monthly Report · {self.location_name}")
        report_window.geometry("600x540")
        report_window.grab_set()

        outer = Frame(report_window, bg=COLORS["bg_main"])
        outer.pack(fill="both", expand=True, padx=30, pady=24)

        _section_header(outer, "REPORT", f"{self.location_name}")

        sub = Label(outer, text=f"Monthly Income Statement · {current_month}")
        style_label(sub, "subtitle")
        sub.pack(anchor="w", pady=(2, 0))

        hairline(outer).pack(fill="x", pady=(14, 18))

        card = Frame(outer, bg=COLORS["bg_card"],
                     highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        body = Frame(card, bg=COLORS["bg_card"])
        body.pack(fill="both", expand=True, padx=24, pady=20)

        # Revenue
        row = Frame(body, bg=COLORS["bg_card"])
        row.pack(fill="x", pady=(0, 6))
        l = Label(row, text="Total Sales Revenue")
        style_label(l, "body", bg=COLORS["bg_card"])
        l.pack(side="left")
        l = Label(row, text=f"${total_revenue:,.2f}")
        style_label(l, "body_bold", bg=COLORS["bg_card"])
        l.pack(side="right")

        hairline(body).pack(fill="x", pady=10)

        # Expense header
        l = Label(body, text="Expenses")
        style_label(l, "section", bg=COLORS["bg_card"])
        l.configure(fg=COLORS["text_secondary"])
        l.pack(anchor="w", pady=(2, 6))

        for category, amount in expense_rows:
            row = Frame(body, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=2)
            l = Label(row, text=f"  {category}")
            style_label(l, "body", bg=COLORS["bg_card"])
            l.pack(side="left")
            l = Label(row, text=f"${amount:,.2f}")
            style_label(l, "body", bg=COLORS["bg_card"])
            l.pack(side="right")

        hairline(body).pack(fill="x", pady=10)

        row = Frame(body, bg=COLORS["bg_card"])
        row.pack(fill="x", pady=2)
        l = Label(row, text="Total Expenses")
        style_label(l, "body_bold", bg=COLORS["bg_card"])
        l.pack(side="left")
        l = Label(row, text=f"${total_expenses:,.2f}")
        style_label(l, "body_bold", bg=COLORS["bg_card"])
        l.pack(side="right")

        # Net income
        row = Frame(body, bg=COLORS["bg_card"])
        row.pack(fill="x", pady=(10, 4))
        l = Label(row, text="Net Income")
        l.configure(font=fonts["report_bold"], fg=COLORS["accent"], bg=COLORS["bg_card"])
        l.pack(side="left")
        l = Label(row, text=f"${net_income:,.2f}")
        l.configure(font=fonts["report_bold"], fg=COLORS["accent"], bg=COLORS["bg_card"])
        l.pack(side="right")

        close_btn = Button(outer, text="Close", width=10, command=report_window.destroy)
        style_ghost_button(close_btn)
        close_btn.pack(pady=(18, 0))

        log_action(
            f"INCOME STATEMENT GENERATED - {self.location_name} - Month: {current_month}, "
            f"Sales: ${total_revenue:,.2f}, Expenses: ${total_expenses:,.2f}, Net Income: ${net_income:,.2f}"
        )

    # ----------------------------------------------------------- view daily sales
    def view_daily_sales(self):
        if not self.location_name:
            messagebox.showerror("Error", "Please select a location first.")
            return

        location_id = get_location_id(self.location_name)
        current_month = datetime.now().strftime("%Y-%m")

        cur.execute("""
            SELECT sales.datetime, flavors.name, sales.size, sales.quantity, 
                sales.container, sales.revenue
            FROM sales
            JOIN flavors ON sales.flavor_id = flavors.id
            WHERE sales.location_id = ?
            AND substr(sales.datetime, 1, 7) = ?
            ORDER BY sales.datetime DESC
        """, (location_id, current_month))

        sales_rows = cur.fetchall()

        sales_window = Toplevel(self)
        style_toplevel(sales_window, f"Daily Sales · {self.location_name}")
        sales_window.geometry("900x460")
        sales_window.grab_set()

        outer = Frame(sales_window, bg=COLORS["bg_main"])
        outer.pack(fill="both", expand=True, padx=24, pady=20)

        _section_header(outer, "SALES", f"Daily Sales · {self.location_name}")

        sub = Label(outer, text=f"Reporting period · {current_month}")
        style_label(sub, "subtitle")
        sub.pack(anchor="w", pady=(2, 0))

        hairline(outer).pack(fill="x", pady=(14, 14))

        columns = ("datetime", "flavor", "size", "quantity", "cone_container", "revenue")
        tree = ttk.Treeview(outer, columns=columns, show="headings", height=12)

        tree.heading("datetime", text="Date/Time")
        tree.heading("flavor", text="Flavor")
        tree.heading("size", text="Size")
        tree.heading("quantity", text="Qty")
        tree.heading("cone_container", text="Cone/Dish")
        tree.heading("revenue", text="Revenue")

        tree.column("datetime", width=170)
        tree.column("flavor", width=160)
        tree.column("size", width=90, anchor="center")
        tree.column("quantity", width=70, anchor="center")
        tree.column("cone_container", width=200)
        tree.column("revenue", width=110, anchor="e")

        total_revenue = 0

        for row in sales_rows:
            sale_datetime, flavor, size, quantity, cone_container, revenue = row
            total_revenue += revenue
            tree.insert("", END, values=(
                sale_datetime,
                flavor,
                size,
                quantity,
                cone_container,
                f"${revenue:,.2f}"
            ))

        tree.pack(fill="both", expand=True)

        # Total
        total_row = Frame(outer, bg=COLORS["bg_main"])
        total_row.pack(fill="x", pady=(14, 0))
        l = Label(total_row, text="Total Sales Revenue")
        style_label(l, "body_bold")
        l.pack(side="left")
        l = Label(total_row, text=f"${total_revenue:,.2f}")
        l.configure(font=fonts["report_bold"], fg=COLORS["accent"], bg=COLORS["bg_main"])
        l.pack(side="right")

        close_btn = Button(outer, text="Close", width=10, command=sales_window.destroy)
        style_ghost_button(close_btn)
        close_btn.pack(pady=(14, 0))

        log_action(f"VIEW DAILY SALES - {self.location_name} for {current_month}")

    # ---------------------------------------------------------- flavor trends
    def show_flavor_trends(self):
        if not self.location_name:
            messagebox.showerror("Error", "Please select a location first.")
            return

        location_id = get_location_id(self.location_name)
        current_month = datetime.now().strftime("%Y-%m")

        cur.execute("""
            SELECT flavors.name, SUM(sales.quantity)
            FROM sales
            JOIN flavors ON sales.flavor_id = flavors.id
            WHERE sales.location_id = ? 
            AND substr(sales.datetime, 1, 7) = ?
            GROUP BY flavors.name
            ORDER BY SUM(sales.quantity) DESC
        """, (location_id, current_month))

        flavor_trends_rows = cur.fetchall()

        if not flavor_trends_rows:
            messagebox.showinfo("No Sales Data", "No sales data available to show flavor trends.")
            return

        trends_window = Toplevel(self)
        style_toplevel(trends_window, f"Flavor Sales Trends · {self.location_name}")
        trends_window.geometry("780x540")
        trends_window.grab_set()

        outer = Frame(trends_window, bg=COLORS["bg_main"])
        outer.pack(fill="both", expand=True, padx=24, pady=20)

        _section_header(outer, "TRENDS", f"Flavor Sales · {self.location_name}")

        sub = Label(outer, text=f"Reporting period · {current_month}")
        style_label(sub, "subtitle")
        sub.pack(anchor="w", pady=(2, 0))

        hairline(outer).pack(fill="x", pady=(14, 14))

        # chart card
        card = Frame(outer, bg=COLORS["bg_card"],
                     highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        flavors_list = [row[0] for row in flavor_trends_rows]
        quantities = [row[1] for row in flavor_trends_rows]

        # styled matplotlib figure to match the theme
        figure = Figure(figsize=(6, 3.5), dpi=100, facecolor=COLORS["bg_card"])
        plot = figure.add_subplot(111)
        plot.set_facecolor(COLORS["bg_card"])

        bars = plot.bar(flavors_list, quantities, color=COLORS["accent"],
                        edgecolor=COLORS["accent_hover"], linewidth=0.5)

        plot.set_xlabel("Flavor", fontsize=10, color=COLORS["text_secondary"])
        plot.set_ylabel("Total Quantity Sold", fontsize=10, color=COLORS["text_secondary"])
        plot.set_title(
            f"Flavor Sales Trends · {self.location_name}",
            fontsize=12, color=COLORS["text_primary"], pad=12,
        )
        plot.tick_params(axis='x', rotation=20, colors=COLORS["text_primary"])
        plot.tick_params(axis='y', colors=COLORS["text_primary"])

        # subtle styling: only bottom + left spines, light grid
        for side in ("top", "right"):
            plot.spines[side].set_visible(False)
        for side in ("bottom", "left"):
            plot.spines[side].set_color(COLORS["border"])
        plot.grid(axis="y", linestyle="--", linewidth=0.6,
                  color=COLORS["divider"], alpha=0.8)
        plot.set_axisbelow(True)

        figure.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=14, pady=14, fill="both", expand=True)

        close_btn = Button(outer, text="Close", width=10, command=trends_window.destroy)
        style_ghost_button(close_btn)
        close_btn.pack(pady=(14, 0))

        log_action(f"VIEW FLAVOR SALES TRENDS - {self.location_name} for {current_month}")

    # ----------------------------------------------------------- view inventory
    def view_inventory(self):
        if not self.location_name:
            messagebox.showerror("Error", "Please select a location first.")
            return

        location_id = get_location_id(self.location_name)
        inventory_window = Toplevel(self)
        style_toplevel(inventory_window, f"Inventory · {self.location_name}")
        inventory_window.geometry("740x460")
        inventory_window.grab_set()

        outer = Frame(inventory_window, bg=COLORS["bg_main"])
        outer.pack(fill="both", expand=True, padx=24, pady=20)

        _section_header(outer, "INVENTORY", f"Stock on hand · {self.location_name}")

        hairline(outer).pack(fill="x", pady=(14, 14))

        columns = ("item", "quantity")
        tree = ttk.Treeview(outer, columns=columns, show="headings", height=14)

        tree.heading("item", text="Item")
        tree.heading("quantity", text="Quantity")

        tree.column("item", width=380)
        tree.column("quantity", width=160, anchor="center")

        # Flavor Inventory
        cur.execute("""
            SELECT flavors.name, flavor_inventory.quantity
            FROM flavor_inventory
            JOIN flavors ON flavor_inventory.flavor_id = flavors.id
            WHERE flavor_inventory.location_id = ?
        """, (location_id,))

        for name, qty in cur.fetchall():
            tree.insert("", END, values=(f"{name} (scoops)", qty))

        # Consumables Inventory
        cur.execute("""
            SELECT consumable, quantity
            FROM consumables_inventory
            WHERE location_id = ?
        """, (location_id,))

        for name, qty in cur.fetchall():
            tree.insert("", END, values=(name, qty))

        tree.pack(fill="both", expand=True)

        close_btn = Button(outer, text="Close", width=10, command=inventory_window.destroy)
        style_ghost_button(close_btn)
        close_btn.pack(pady=(14, 0))

        log_action(f"VIEW INVENTORY - {self.location_name}")

    def set_location(self, location_name):
        self.location_name = location_name
        self.title_label.config(text=f"{self.location_name}")
