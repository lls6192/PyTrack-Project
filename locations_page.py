from tkinter import *
from tkinter import ttk
from tkinter import messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
from datetime import datetime
from database import get_location_id, conn, cur, get_locations, get_flavor_id, log_inventory, log_sale, log_action, get_fixed_costs, get_total_fixed_costs, get_consumable_id

class LocationPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.location_name = ""

        self.controller = controller

        self.title_label = Label(self, text=f"Store Location Page: {self.location_name}", font=("Times New Roman", 24))
        self.title_label.grid(row=0, column=0, columnspan=3, pady=20)

        btn_restock = Button(self, text = "Restock Flavor Inventory", command=self.restock_flavor_inventory)
        btn_restock.grid(row=1, column=0, padx=10, pady=10)

        btn_restock_item = Button(self, text="Restock Consumables", command=self.restock_consumables_inventory)
        btn_restock_item.grid(row=1, column=1, padx=10, pady=10)


        btn_daily_sales = Button(self, text = "Enter Daily Sales", command=self.enter_daily_sales)
        btn_daily_sales.grid(row=1, column=2, padx=10, pady=10)
        btn_report = Button(self, text = "Generate Report", command=self.generate_report)
        btn_report.grid(row=2, column=0, padx=10, pady=10)

        btn_fixed_costs = Button(self, text="View Fixed Costs", command=self.view_fixed_costs)
        btn_fixed_costs.grid(row=2, column=1, padx=10, pady=10)

        btn_history_log = Button(self, text="View History Log", command=self.view_history_log)
        btn_history_log.grid(row=2, column=2, padx=10, pady=10)

        btn_back = Button(
            self,
            text="Back",
            command=lambda: controller.show_frame("StartPage")
        )
        btn_back.grid(row=3, column=1, pady=20)

    def restock_flavor_inventory(self):
        # Quantity and Flavor Restocked, and Date/Time
        restock_window = Toplevel(self)
        restock_window.title("Restock Flavor Inventory")
        restock_window.geometry("500x200")
        restock_window.grab_set()  # Make the restock window modal

        flavor_options = [
            "Vanilla",
            "Chocolate",
            "Cookies & Cream",
            "Neapolitan",
            "Cookie Dough"
        ]

        rows_frame = Frame(restock_window)
        rows_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="w")

        restock_rows = []

        def add_restock_row():
            row_index = len(restock_rows)
            flavor_var = StringVar()
            flavor_dropdown = ttk.Combobox(
                rows_frame,
                textvariable=flavor_var,
                values=flavor_options,
                state="readonly",
                width=12
            )
            flavor_dropdown.grid(row=row_index, column=1, padx=10, pady=  5, sticky="w")
            flavor_dropdown.set("Select a flavor")

            flavor_label = Label(rows_frame, text="Flavor Restocked:")
            flavor_label.grid(row=row_index, column=0, pady=10, sticky="w")

            quantity_label = Label(rows_frame, text = "Quantity Restocked:")
            quantity_label.grid(row=row_index, column=2, padx=10, pady=5, sticky="w")
            
            quantity_entry = Entry(rows_frame, width = 4)
            quantity_entry.grid(row=row_index, column=3, padx=10, pady=5, sticky="w")
            restock_rows.append((flavor_var, quantity_entry))
        
        def submit_restock():
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

            log_inventory(flavor, quantity, f"New inventory for {flavor} at {self.location_name}: {quantity} scoops")

            messagebox.showinfo(
                "Restock Saved",
                f"Inventory restocked for {self.location_name}"
            )
            restock_window.destroy()

        add_restock_row()  # Add the first row by default

        add_button = Button(restock_window, text="Add Another Flavor", command=add_restock_row)
        add_button.grid(row=2, column=0, columnspan=4, pady=10)

        # Buttons frame
        button_frame = Frame(restock_window)
        button_frame.grid(row=3, column=0, columnspan=4, pady=20)
        ok_button = Button(button_frame, text="OK", width=12, command=submit_restock)
        ok_button.grid(row=0, column=0, padx=10)

        cancel_button = Button(button_frame, text="Cancel", width=12, command=restock_window.destroy)
        cancel_button.grid(row=0, column=1, padx=10)

    def restock_consumables_inventory(self):
        restock_consumables_window = Toplevel(self)
        restock_consumables_window.title("Restock Consumables Inventory")
        restock_consumables_window.geometry("600x200")
        restock_consumables_window.grab_set()

        consumables_options = [
            "Standard Ice Cream Cone",
            "Waffle Cone",
            "Dish with Spoon",
            "Napkins"
        ]

        rows_frame = Frame(restock_consumables_window)
        rows_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="w")

        restock_consumables_rows = []

        def add_restock_consumables_row():
            row_index = len(restock_consumables_rows)
            consumable_var = StringVar()
            consumable_dropdown = ttk.Combobox(
                rows_frame,
                textvariable=consumable_var,
                values=consumables_options,
                state="readonly",
                width=15
            )
            consumable_dropdown.grid(row=row_index, column=1, padx=10, pady=5, sticky="w")
            consumable_dropdown.set("Select a consumable")

            consumable_label = Label(rows_frame, text="Consumable Restocked:")
            consumable_label.grid(row=row_index, column=0, pady=10, sticky="w")

            quantity_label = Label(rows_frame, text="Quantity Restocked:")
            quantity_label.grid(row=row_index, column=2, padx=10, pady=5, sticky="w")

            quantity_entry = Entry(rows_frame, width=4)
            quantity_entry.grid(row=row_index, column=3, padx=10, pady=5, sticky="w")

            restock_consumables_rows.append((consumable_var, quantity_entry))
        
        def submit_consumables_restock():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            location_id = get_location_id(self.location_name)

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

                # if standard ice cream cone, waffle cone, or dish with spoon convert each restock has 100 count
                if consumable in ["Standard Ice Cream Cone", "Waffle Cone", "Dish with Spoon"]:
                    quantity = quantity * 100
                else:
                    quantity = quantity * 10000 # for napkins, each restock has 10,000 count

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

            messagebox.showinfo(
                "Restock Saved",
                f"Consumables inventory restocked for {self.location_name}"
            )
            restock_consumables_window.destroy()
        
        add_restock_consumables_row()  # Add the first row by default

        add_button = Button(restock_consumables_window, text="Add Another Consumable", command=add_restock_consumables_row)
        add_button.grid(row=2, column=0, columnspan=4, pady=10)

        # Buttons frame
        button_frame = Frame(restock_consumables_window)
        button_frame.grid(row=3, column=0, columnspan=4, pady=20)
        ok_button = Button(button_frame, text="OK", width=12, command=submit_consumables_restock)
        ok_button.grid(row=0, column=0, padx=10)

        cancel_button = Button(button_frame, text="Cancel", width=12, command=restock_consumables_window.destroy)
        cancel_button.grid(row=0, column=1, padx=10)

    def enter_daily_sales(self):
        # Flavors and Quantitiies Sold
        daily_sales_window = Toplevel(self)
        daily_sales_window.title("Enter Daily Sales")
        daily_sales_window.geometry("900x200")
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
        cone_container_options = ["Standard Ice Cream Cone", "Waffle Cone", "Sugar Cone", "Dish with Spoon"]

        row_frame = Frame(daily_sales_window)
        row_frame.grid(row=1, column=0, columnspan=6, padx=10, pady=5, sticky="w")

        daily_sales_rows = []

        def add_daily_sales_row():
            row_index = len(daily_sales_rows)

            flavor_var = StringVar()
            size_var = StringVar()

            flavor_label = Label(row_frame, text="Flavor Sold:")
            flavor_label.grid(row=row_index, column=0, pady=10, sticky="w")

            flavor_dropdown = ttk.Combobox(
                row_frame,
                textvariable=flavor_var,
                values=flavor_options,
                state="readonly",
                width=12
            )
            flavor_dropdown.grid(row=row_index, column=1, padx=10, pady=5, sticky="w")
            flavor_dropdown.set("Select a flavor")

            size_label = Label(row_frame, text="Size:")
            size_label.grid(row=row_index, column=2, padx=10, pady=5, sticky="w")

            size_dropdown = ttk.Combobox(
                row_frame,
                textvariable=size_var,
                values=size_options,
                state="readonly",
                width = 10
            )
            size_dropdown.grid(row=row_index, column=3, padx=10, pady=5, sticky="w")
            size_dropdown.set("Select a size")

            quantity_label = Label(row_frame, text="Quantity Sold:")
            quantity_label.grid(row=row_index, column=4, padx=10, pady=5, sticky="w")
            
            quantity_entry = Entry(row_frame, width=4)
            quantity_entry.grid(row=row_index, column=5, padx=10, pady=5, sticky="w")

            cone_container_entry = ttk.Combobox(
                row_frame,
                values=cone_container_options,
                state="readonly",
                width=25
            )
            cone_container_entry.grid(row=row_index, column=6, padx=10, pady=5, sticky="w")
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
                cur.execute("SELECT quantity FROM inventory WHERE location_id = ? AND cone_container = ?", (location_id, cone_container_entry.get()))
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
                    INSERT INTO sales (location_id, flavor_id, quantity, revenue, datetime, size, cone_container)
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

                    # check updated flavor inventory level
                    cur.execute("""
                        SELECT quantity FROM flavor_inventory
                        WHERE location_id = ? AND flavor_id = ?
                    """, (location_id, entry["flavor_id"]))

                    updated_quantity = cur.fetchone()[0]

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

        add_daily_sales_button = Button(daily_sales_window, text="Add Another Flavor", command=add_daily_sales_row)
        add_daily_sales_button.grid(row=2, column=0, columnspan=4, pady=10)

         # Buttons frame
        button_frame = Frame(daily_sales_window)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        ok_button = Button(button_frame, text="OK", width=12, command=submit_daily_sales)
        ok_button.grid(row=0, column=0, padx=10)

        cancel_button = Button(button_frame, text="Cancel", width=12, command=daily_sales_window.destroy)
        cancel_button.grid(row=0, column=1, padx=10)

        # If inventory is low, alert the user to restock
        print(f"Enter Daily Sales for {self.location_name}")

    #View the fixed costs current locaiton ID, month and shows this information in a table
    def view_fixed_costs(self):
        if not self.location_name:
            messagebox.showerror("Error", "Please select a location first.")
            return

        location_id = get_location_id(self.location_name)
        current_month = datetime.now().strftime("%Y-%m")

        fixed_cost_rows = get_fixed_costs(location_id, current_month)
        total_fixed_costs = get_total_fixed_costs(location_id, current_month)

        fixed_costs_window = Toplevel(self)
        fixed_costs_window.title(f"Fixed Costs - {self.location_name}")
        fixed_costs_window.geometry("700x350")
        fixed_costs_window.grab_set()

        Label(
            fixed_costs_window,
            text=f"Fixed Costs for {self.location_name} ({current_month})",
            font=("Times New Roman", 16, "bold")
        ).pack(pady=10)

        columns = ("name", "amount", "frequency", "month")
        tree = ttk.Treeview(fixed_costs_window, columns=columns, show="headings", height=10)

        tree.heading("name", text="Cost Name")
        tree.heading("amount", text="Amount")
        tree.heading("frequency", text="Frequency")
        tree.heading("month", text="Month")

        tree.column("name", width=260)
        tree.column("amount", width=120, anchor="center")
        tree.column("frequency", width=120, anchor="center")
        tree.column("month", width=120, anchor="center")

        for row in fixed_cost_rows:
            name, amount, frequency, month = row
            tree.insert("", END, values=(name, f"${amount:,.2f}", frequency, month))

        tree.pack(padx=15, pady=10, fill="both", expand=True)

        Label(
            fixed_costs_window,
            text=f"Total Fixed Costs: ${total_fixed_costs:,.2f}",
            font=("Times New Roman", 14, "bold")
        ).pack(pady=10)

        Button(fixed_costs_window, text="Close", width=12, command=fixed_costs_window.destroy).pack(pady=5)

        log_action(f"VIEW FIXED COSTS - {self.location_name} for {current_month}")
    
    def view_history_log(self):
        log_file = Path("daily_log.txt")

        history_window = Toplevel(self)
        history_window.title(f"History Log - {self.location_name}")
        history_window.geometry("800x450")
        history_window.grab_set()

        Label(
            history_window,
            text="System History Log",
            font=("Times New Roman", 16, "bold")
        ).pack(pady=10)

        log_text = ScrolledText(history_window, wrap=WORD, width=95, height=22)
        log_text.pack(padx=10, pady=10, fill="both", expand=True)

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

        Button(history_window, text="Close", width=12, command=history_window.destroy).pack(pady=5)

    def generate_report(self):
        if not self.location_name:
            messagebox.showerror("Error", "Please select a location first.")
            return

        location_id = get_location_id(self.location_name)
        current_month = datetime.now().strftime("%Y-%m")

        cur.execute("""
            SELECT SUM(revenue)
            FROM sales
            WHERE location_id = ? AND substr(datetime, 1, 7) = ?
        """, (location_id, current_month))

        total_sales = cur.fetchone()[0] or 0

        total_fixed = get_total_fixed_costs(location_id, current_month)
        profit = total_sales - total_fixed

        report_window = Toplevel(self)
        report_window.title(f"Monthly Report - {self.location_name}")
        report_window.geometry("450x260")
        report_window.grab_set()

        Label(
            report_window,
            text=f"Monthly Report for {self.location_name}",
            font=("Times New Roman", 16, "bold")
        ).pack(pady=10)

        report_text = (
            f"Month: {current_month}\n\n"
            f"Total Sales Revenue: ${total_sales:,.2f}\n"
            f"Total Fixed Costs: ${total_fixed:,.2f}\n"
            f"Estimated Profit: ${profit:,.2f}"
        )

        Label(
            report_window,
            text=report_text,
            font=("Times New Roman", 13),
            justify="left"
        ).pack(pady=20)

        Button(
            report_window,
            text="Close",
            width=12,
            command=report_window.destroy
        ).pack(pady=10)

        log_action(
            f"REPORT GENERATED - {self.location_name} - Month: {current_month}, "
            f"Sales: ${total_sales:,.2f}, Fixed Costs: ${total_fixed:,.2f}, Profit: ${profit:,.2f}"
        )
        
        # Include fixed costs and sales revenue
        # Have monthly income statements for individual locations and the entire company
            #print(f"Generate Report for {self.location_name}")
            #cur.execute("SELECT SUM(total) FROM sales")
            #total_sales = cur.fetchone()[0] or 0

        # cur.execute("SELECT SUM(amount) FROM fixed_costs")
        # total_fixed = cur.fetchone()[0] or 0

        # profit = total_sales - total_fixed
        # print("Total Sales: ${total_sales}")
        # print("Fixed Costs: ${total_fixed}")
        # print("Profit: ${profit}")
    

    def set_location(self, location_name):
        self.location_name = location_name
        self.title_label.config(text=f"Store Location Page - {self.location_name}")
