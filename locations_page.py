from tkinter import *
from tkinter import ttk

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
        print(f"Restock Inventory for {self.location_name}")

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
