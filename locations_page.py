from tkinter import *
from tkinter import ttk
from tkinter import messagebox, simpledialog
from datetime import datetime

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
        restock_window.geometry("300x200")
        restock_window.grab_set()  # Make the restock window modal

        flavor_label = Label(restock_window, text="Flavor Restocked:")
        flavor_label.pack(pady = (15,5))

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
        flavor_dropdown.pack(pady=5)
        flavor_dropdown.set("Select a flavor")

        quantity_label = Label(restock_window, text = "Quantity Restocked:")
        quantity_label.pack(pady=(15,5))

        quantity_entry = Entry(restock_window)
        quantity_entry.pack(pady=5)
        
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
        button_frame.pack(pady=20)

        ok_button = Button(button_frame, text="OK", width=12, command=submit_restock)
        ok_button.grid(row=0, column=0, padx=10)

        cancel_button = Button(button_frame, text="Cancel", width=12, command=restock_window.destroy)
        cancel_button.grid(row=0, column=1, padx=10)

    def enter_daily_sales(self):
        # Flavors and Quantitiies Sold
        # If inventory is low, alert the user to restock
        print(f"Enter Daily Sales for {self.location_name}")
    
    def generate_report(self):
        # Include fixed costs and sales revenue
        # Have monthly income statements for individual locations and the entire company
        print(f"Generate Report for {self.location_name}")

    def set_location(self, location_name):
        self.location_name = location_name
        self.title_label.config(text=f"Store Location Page - {self.location_name}")
