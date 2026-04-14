from tkinter import *
from tkinter import ttk
from tkinter import messagebox, simpledialog
from datetime import datetime
from database import get_location_id, conn, cur, get_locations

class LocationPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.location_name = ""

        self.controller = controller

        self.title_label = Label(self, text=f"Store Location Page: {self.location_name}", font=("Times New Roman", 24))
        self.title_label.grid(row=0, column=0, columnspan=3, pady=20)

        btn_restock = Button(self, text = "Restock Inventory", command=self.restock_inventory)
        btn_restock.grid(row=1, column=0, padx=10, pady=10)

        btn_daily_sales = Button(self, text = "Enter Daily Sales", command=self.enter_daily_sales)
        btn_daily_sales.grid(row=1, column=1, padx=10, pady=10)

        btn_report = Button(self, text = "Generate Report", command=self.generate_report)
        btn_report.grid(row=1, column=2, padx=10, pady=10)

        btn_back = Button(
            self,
            text="Back",
            command=lambda: controller.show_frame("StartPage")
        )
        btn_back.grid(row=2, column=1, pady=20)

    def restock_inventory(self):
        # Quantity and Flavor Restocked, and Date/Time
        restock_window = Toplevel(self)
        restock_window.title("Restock Inventory")
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
                # convert from number of 5-gallon buckets to number of scoops (assuming 1 bucket = 32 scoops)
                quantity = quantity * 160 
                cur.execute("INSERT INTO inventory (location_id, flavor, quantity, timestamp) VALUES (?, ?, ?, ?)",
                            (location_id, flavor, quantity, timestamp))
            conn.commit()

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

    def enter_daily_sales(self):
        # Flavors and Quantitiies Sold
        daily_sales_window = Toplevel(self)
        daily_sales_window.title("Enter Daily Sales")
        daily_sales_window.geometry("700x200")
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
            daily_sales_rows.append((flavor_var, quantity_entry))

        def submit_daily_sales():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            location_id = get_location_id(self.location_name)

            valid_entries = []

            for flavor_var, size_var, quantity_entry in daily_sales_rows:

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

                # check current inventory
                cur.execute("SELECT quantity FROM inventory WHERE location_id = ? AND flavor_id = ?", (location_id, flavor_id))
                inventory_row = cur.fetchone()

                current_inventory = inventory_row[0] if inventory_row else 0

                if current_inventory < inventory_use:
                    messagebox.showerror("Error", f"Insufficient inventory for flavor '{flavor}'.")
                    return
                
                revenue = size_prices[size] * quantity

                valid_entries.append({
                    "flavor_id": flavor_id,
                    "flavor": flavor,
                    "size": size,
                    "quantity": quantity,
                    "inventory_needed": inventory_use,
                    "revenue": revenue
                })

                valid_entries.append((flavor, quantity))
            
            if not valid_entries:
                messagebox.showerror("Error", "Please add at least one flavor sold.")
                return

            # add to database
            try:
                for entry in valid_entries:
                    # insert into sales table
                    cur.execute("""
                    INSERT INTO sales (location_id, flavor_id, quantity, revenue, datetime, size)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        location_id,
                        entry["flavor_id"],
                        entry["quantity_sold"],
                        entry["revenue"],
                        timestamp,
                        entry["size"]
                    ))

                    # subtract from inventory
                    cur.execute("""
                        UPDATE inventory
                        SET quantity = quantity - ?
                        WHERE location_id = ? AND flavor_id = ?
                        """, (
                        entry["inventory_needed"],
                        location_id,
                        entry["flavor_id"]
                    ))
                conn.commit()

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
    
    def generate_report(self):
        # Include fixed costs and sales revenue
        # Have monthly income statements for individual locations and the entire company
        print(f"Generate Report for {self.location_name}")

    def set_location(self, location_name):
        self.location_name = location_name
        self.title_label.config(text=f"Store Location Page - {self.location_name}")
