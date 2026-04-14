from tkinter import *
from tkinter import ttk
from tkinter import messagebox, simpledialog
from datetime import datetime

from startup_page import get_location_id

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
        restock_window.geometry("400x200")
        restock_window.grab_set()  # Make the restock window modal

        flavor_label = Label(restock_window, text="Flavor Restocked:")
        flavor_label.grid(row=0, column=0, padx=10, pady=(15,5), sticky="w")

        flavor_options = [
            "Vanilla",
            "Chocolate",
            "Cookies & Cream",
            "Neapolitan",
            "Cookie Dough"
        ]

        flavor_var = StringVar()
        flavor_dropdown = ttk.Combobox(
            restock_window,
            textvariable=flavor_var,
            values=flavor_options,
            state="readonly"
        )
        flavor_dropdown.grid(row=0, column=1, padx=10, pady=(15,5), sticky="w")
        flavor_dropdown.set("Select a flavor")

        quantity_label = Label(restock_window, text = "Quantity Restocked:")
        quantity_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        quantity_entry = Entry(restock_window)
        quantity_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        def submit_restock():
            flavor = flavor_var.get().strip()
            quantity_text = quantity_entry.get().strip()

            if quantity_text == "":
                messagebox.showerror("Error", "Quantity cannot be empty.")
                return

            if not quantity_text.isdigit():
                messagebox.showerror("Error", "Quantity must be a whole number.")
                return

            quantity = int(quantity_text)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"Location: {self.location_name}")
            print(f"Flavor Restocked: {flavor}")
            print(f"Quantity Added: {quantity}")
            print(f"Date/Time: {timestamp}")

            messagebox.showinfo(
                "Restock Saved",
                f"{quantity} of {flavor} added for {self.location_name}"
            )
            restock_window.destroy()

        # Buttons frame
        button_frame = Frame(restock_window)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ok_button = Button(button_frame, text="OK", width=12, command=submit_restock)
        ok_button.grid(row=0, column=0, padx=10)

        cancel_button = Button(button_frame, text="Cancel", width=12, command=restock_window.destroy)
        cancel_button.grid(row=0, column=1, padx=10)

    def enter_daily_sales(self):
        # Flavors and Quantitiies Sold
        daily_sales_window = Toplevel(self)
        daily_sales_window.title("Enter Daily Sales")
        daily_sales_window.geometry("400 x 200")
        daily_sales_window.grab_set()  # Make the daily sales window modal

        flavor_label = Label(daily_sales_window, text="Flavor Sold:")
        flavor_label.grid(row=0, column=0, padx=10, pady=(15,5), sticky="w")

        flavor_options = [
            "Vanilla",
            "Chocolate",
            "Cookies & Cream",
            "Neapolitan",
            "Cookie Dough"
        ]

        flavor_var = StringVar()
        flavor_dropdown = ttk.Combobox(
            daily_sales_window,
            textvariable=flavor_var,
            values=flavor_options,
            state="readonly"
        )
        flavor_dropdown.grid(row=0, column=1, padx=10, pady=(15,5), sticky="w")
        flavor_dropdown.set("Select a flavor")

        quantity_label = Label(daily_sales_window, text="Quantity Sold:")
        quantity_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        quantity_entry = Entry(daily_sales_window)
        quantity_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        def submit_daily_sales():
            flavor = flavor_var.get().strip()
            quantity_text = quantity_entry.get().strip()

            if quantity_text == "":
                messagebox.showerror("Error", "Quantity cannot be empty.")
                return

            if not quantity_text.isdigit():
                messagebox.showerror("Error", "Quantity must be a whole number.")
                return

            quantity = int(quantity_text)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cur.execute("INSERT INTO daily_sales (location_id, flavor, quantity, timestamp) VALUES (?, ?, ?, ?)", (get_location_id(self.location_name), flavor, quantity, timestamp))
            conn.commit()

            print(f"Location: {self.location_name}")
            print(f"Flavor Sold: {flavor}")
            print(f"Quantity Sold: {quantity}")
            print(f"Date/Time: {timestamp}")

            messagebox.showinfo(
                "Daily Sales Saved",
                f"{quantity} of {flavor} sold for {self.location_name}"
            )
            daily_sales_window.destroy()

         # Buttons frame
        button_frame = Frame(daily_sales_window)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

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
