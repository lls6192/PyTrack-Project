from tkinter import *
from tkinter import ttk
from tkinter import messagebox, simpledialog
from locations_page import LocationPage
from database import get_location_id, conn, cur, get_locations
from datetime import datetime

class PyTrackApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("PyTrack")
        self.geometry("620x400")

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        # add Both pages to the container
        for F in (StartPage, LocationPage):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("StartPage")
    
    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()


class StartPage(ttk.Frame):
    def create_new_location(self):
        # Code to create a new location
        new_location = simpledialog.askstring("Create New Location", "Enter the name of the new location:")
        
        if new_location is None:
            return

        new_location = new_location.strip() 

        # Check if the new location already exists
        if new_location == "":
            messagebox.showerror("Error", "Location name cannot be empty.")
            return
        elif get_location_id(new_location) is not None:
            messagebox.showerror("Error", f"Location '{new_location}' already exists.")
            return
        # Check if the new location is valid (not empty or just whitespace)
        else:
            cur.execute("INSERT INTO locations (name) VALUES (?)", (new_location,))
            conn.commit()
            self.cb['values'] = get_locations()
            self.cb.set(new_location)
            messagebox.showinfo("Create New Location", f"Location created: {new_location}")
            # Code to open the new location's page
            location_page = self.controller.frames["LocationPage"]
            location_page.set_location(new_location)
            self.controller.show_frame("LocationPage")

    def cmd_submit(self):
        selected_location = self.cb.get()
        print(f"Selected location: {selected_location}")

        # Code to handle the selected location
        #get the location page
        location_page = self.controller.frames["LocationPage"]

        #send data to it
        location_page.set_location(selected_location)

        # show the location page
        self.controller.show_frame("LocationPage")

    def generate_report(self):
        # Code to generate a report for the whole company
        #messagebox.showinfo("Generate Report", "Generating company report...")
        # Use database and pandas dataframe to generate the report
        current_month = datetime.now().strftime("%Y-%m")

        # Total company revenue
        cur.execute("""
            SELECT SUM(amount)
            FROM costs
            WHERE transaction_type = 'Revenue'
            AND substr(datetime, 1, 7) = ?
        """, (current_month,))
        total_revenue = cur.fetchone()[0] or 0

        # Total company expenses
        cur.execute("""
            SELECT SUM(amount)
            FROM costs
            WHERE transaction_type = 'Expense'
            AND substr(datetime, 1, 7) = ?
        """, (current_month,))
        total_expenses = cur.fetchone()[0] or 0

        net_income = total_revenue - total_expenses

        # Expense breakdown
        cur.execute("""
            SELECT category, SUM(amount)
            FROM costs
            WHERE transaction_type = 'Expense'
            AND substr(datetime, 1, 7) = ?
            GROUP BY category
        """, (current_month,))
        expense_rows = cur.fetchall()

        # Revenue by location
        cur.execute("""
            SELECT locations.name, SUM(costs.amount)
            FROM costs
            JOIN locations ON costs.location_id = locations.id
            WHERE costs.transaction_type = 'Revenue'
            AND substr(costs.datetime, 1, 7) = ?
            GROUP BY locations.name
        """, (current_month,))
        location_revenue_rows = cur.fetchall()

        report_window = Toplevel(self)
        report_window.title("Company Monthly Income Statement")
        report_window.geometry("600x500")
        report_window.grab_set()

        Label(
            report_window,
            text="Company Monthly Income Statement",
            font=("Times New Roman", 16, "bold")
        ).pack(pady=10)

        report_text = (
            f"Month: {current_month}\n\n"
            f"Total Sales Revenue: ${total_revenue:,.2f}\n\n"
            f"Expenses:\n"
        )

        for category, amount in expense_rows:
            report_text += f"  {category}: ${amount:,.2f}\n"

        report_text += (
            f"\nTotal Expenses: ${total_expenses:,.2f}\n"
            f"Net Income: ${net_income:,.2f}\n\n"
            f"Revenue by Location:\n"
        )

        for location_name, revenue in location_revenue_rows:
            report_text += f"  {location_name}: ${revenue:,.2f}\n"

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

    def __init__(self, parent, controller):
        super().__init__(parent)
    
        self.controller = controller

        # Make columns expand (for centering)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Title
        title = Label(self, text="Welcome to PyTrack!", font=("Times New Roman", 24))
        title.grid(row=0, column=0, columnspan=2, pady=20, sticky="ew")

        #------------------------------------------------------------------
        # Label for Selecting an Existing Location
        lbl_existing_location = Label(self, text="Select an Existing Location:", font=("Times New Roman", 16, 'bold'))
        lbl_existing_location.grid(row=1, column=0, padx=40, pady=1, sticky="w")

         # Combobox  
        self.cb = ttk.Combobox(self, state="readonly")
        self.cb.set("Select a location")
        self.cb['values'] = get_locations()
        self.cb.grid(row=2, column=0, padx=40, pady=1, sticky="w")

        # Button to display selection  
        btn_submit = Button(self, text="Submit", command = self.cmd_submit)
        btn_submit.grid(row=3, column=0, padx=40, pady=1)
        #------------------------------------------------------------------
        # Label for Creating a New Location
        lbl_new_location = Label(
            self,
            text="Create a New Location:", 
            font=("Times New Roman", 16, 'bold')
        )
        lbl_new_location.grid(row=1, column=1, padx=5, pady=1, sticky="w")

        # Button to create a new location
        btn_create_new_location = Button(self, text="Create New Location", command=self.create_new_location)
        btn_create_new_location.grid(row=2, column=1, padx=5, sticky="w")

        #------------------------------------------------------------------
        # Generate Report button for whole company
        btn_generate_report = Button(self, text="Generate Company Monthly Income Statement", command=self.generate_report)
        btn_generate_report.grid(row=4, column=0, columnspan=2, pady=20)


if __name__ == "__main__":
    app = PyTrackApp()
    app.mainloop()
