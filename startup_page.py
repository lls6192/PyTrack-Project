from tkinter import *
from tkinter import ttk
from tkinter import messagebox, simpledialog
from locations_page import LocationPage
from database import get_location_id, conn, cur, get_locations
from datetime import datetime
from theme import (
    apply_theme, fonts, COLORS,
    style_primary_button, style_secondary_button, style_ghost_button,
    style_label, style_frame, style_toplevel, hairline,
)


class PyTrackApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("PyTrack")
        self.geometry("820x520")
        self.minsize(720, 460)

        # apply visual theme to the whole app once
        apply_theme(self)

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

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
        # get the location page
        location_page = self.controller.frames["LocationPage"]

        # send data to it
        location_page.set_location(selected_location)

        # show the location page
        self.controller.show_frame("LocationPage")

    def generate_report(self):
        # Code to generate a report for the whole company
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

        # ---------- Report window UI ----------
        report_window = Toplevel(self)
        style_toplevel(report_window, "Company Monthly Income Statement")
        report_window.geometry("620x600")
        report_window.grab_set()

        # outer padding
        outer = Frame(report_window, bg=COLORS["bg_main"])
        outer.pack(fill="both", expand=True, padx=30, pady=24)

        title_lbl = Label(outer, text="Company Monthly Income Statement")
        style_label(title_lbl, "heading")
        title_lbl.pack(anchor="w")

        sub_lbl = Label(outer, text=f"Reporting period · {current_month}")
        style_label(sub_lbl, "subtitle")
        sub_lbl.pack(anchor="w", pady=(2, 14))

        hairline(outer).pack(fill="x", pady=(0, 18))

        # card containing the financials
        card = Frame(outer, bg=COLORS["bg_card"],
                     highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        body = Frame(card, bg=COLORS["bg_card"])
        body.pack(fill="both", expand=True, padx=24, pady=20)

        # Revenue line
        rev_row = Frame(body, bg=COLORS["bg_card"])
        rev_row.pack(fill="x", pady=(0, 6))
        l = Label(rev_row, text="Total Sales Revenue")
        style_label(l, "body", bg=COLORS["bg_card"])
        l.pack(side="left")
        l = Label(rev_row, text=f"${total_revenue:,.2f}")
        style_label(l, "body_bold", bg=COLORS["bg_card"])
        l.pack(side="right")

        hairline(body).pack(fill="x", pady=10)

        # Expense breakdown header
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

        # Total expenses
        row = Frame(body, bg=COLORS["bg_card"])
        row.pack(fill="x", pady=2)
        l = Label(row, text="Total Expenses")
        style_label(l, "body_bold", bg=COLORS["bg_card"])
        l.pack(side="left")
        l = Label(row, text=f"${total_expenses:,.2f}")
        style_label(l, "body_bold", bg=COLORS["bg_card"])
        l.pack(side="right")

        # Net income — accent color
        row = Frame(body, bg=COLORS["bg_card"])
        row.pack(fill="x", pady=(8, 4))
        l = Label(row, text="Net Income")
        l.configure(font=fonts["report_bold"], fg=COLORS["accent"], bg=COLORS["bg_card"])
        l.pack(side="left")
        l = Label(row, text=f"${net_income:,.2f}")
        l.configure(font=fonts["report_bold"], fg=COLORS["accent"], bg=COLORS["bg_card"])
        l.pack(side="right")

        hairline(body).pack(fill="x", pady=12)

        # Revenue by location
        l = Label(body, text="Revenue by Location")
        style_label(l, "section", bg=COLORS["bg_card"])
        l.configure(fg=COLORS["text_secondary"])
        l.pack(anchor="w", pady=(2, 6))

        if location_revenue_rows:
            for location_name, revenue in location_revenue_rows:
                row = Frame(body, bg=COLORS["bg_card"])
                row.pack(fill="x", pady=2)
                l = Label(row, text=f"  {location_name}")
                style_label(l, "body", bg=COLORS["bg_card"])
                l.pack(side="left")
                l = Label(row, text=f"${revenue:,.2f}")
                style_label(l, "body", bg=COLORS["bg_card"])
                l.pack(side="right")
        else:
            l = Label(body, text="  (no revenue recorded yet this month)")
            style_label(l, "small_muted", bg=COLORS["bg_card"])
            l.pack(anchor="w", pady=2)

        # Close
        close_btn = Button(outer, text="Close", command=report_window.destroy)
        style_ghost_button(close_btn, width=10)
        close_btn.pack(pady=(18, 0))

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        self.configure(style="TFrame")

        # ---------- outer padding wrapper ----------
        wrapper = Frame(self, bg=COLORS["bg_main"])
        wrapper.pack(fill="both", expand=True, padx=48, pady=36)

        # ---------- Header ----------
        header = Frame(wrapper, bg=COLORS["bg_main"])
        header.pack(fill="x")

        title = Label(header, text="Welcome to PyTrack")
        style_label(title, "title")
        title.pack(anchor="w")

        subtitle = Label(
            header,
            text="A small ledger for your ice-cream operation. Pick a location to begin."
        )
        style_label(subtitle, "subtitle")
        subtitle.pack(anchor="w", pady=(2, 0))

        hairline(wrapper).pack(fill="x", pady=(18, 22))

        # ---------- Two-column action area ----------
        cards = Frame(wrapper, bg=COLORS["bg_main"])
        cards.pack(fill="both", expand=True)
        cards.columnconfigure(0, weight=1, uniform="card")
        cards.columnconfigure(1, weight=1, uniform="card")

        # --- Card 1: Existing Location ---
        card1 = Frame(
            cards, bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"], highlightthickness=1,
        )
        card1.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        card1_inner = Frame(card1, bg=COLORS["bg_card"])
        card1_inner.pack(fill="both", expand=True, padx=22, pady=20)

        eyebrow = Label(card1_inner, text="STEP 01")
        eyebrow.configure(font=fonts["section"], fg=COLORS["accent"], bg=COLORS["bg_card"])
        eyebrow.pack(anchor="w")

        lbl_existing_location = Label(card1_inner, text="Select an existing location")
        style_label(lbl_existing_location, "heading", bg=COLORS["bg_card"])
        lbl_existing_location.pack(anchor="w", pady=(4, 14))

        # Combobox
        self.cb = ttk.Combobox(card1_inner, state="readonly", width=28)
        self.cb.set("Select a location")
        self.cb['values'] = get_locations()
        self.cb.pack(anchor="w", fill="x")

        # Submit button
        btn_submit = Button(card1_inner, text="Open Location  →", command=self.cmd_submit)
        style_primary_button(btn_submit)
        btn_submit.pack(anchor="w", pady=(16, 0))

        # --- Card 2: New Location ---
        card2 = Frame(
            cards, bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"], highlightthickness=1,
        )
        card2.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        card2_inner = Frame(card2, bg=COLORS["bg_card"])
        card2_inner.pack(fill="both", expand=True, padx=22, pady=20)

        eyebrow2 = Label(card2_inner, text="OR")
        eyebrow2.configure(font=fonts["section"], fg=COLORS["accent"], bg=COLORS["bg_card"])
        eyebrow2.pack(anchor="w")

        lbl_new_location = Label(card2_inner, text="Create a new location")
        style_label(lbl_new_location, "heading", bg=COLORS["bg_card"])
        lbl_new_location.pack(anchor="w", pady=(4, 6))

        helper2 = Label(
            card2_inner,
            text="Add a brand new store to start tracking sales, inventory, and costs.",
            wraplength=300, justify="left",
        )
        style_label(helper2, "small", bg=COLORS["bg_card"])
        helper2.pack(anchor="w", pady=(0, 14))

        btn_create_new_location = Button(
            card2_inner,
            text="+  Create New Location",
            command=self.create_new_location,
        )
        style_secondary_button(btn_create_new_location)
        btn_create_new_location.pack(anchor="w")

        # ---------- Footer: Generate Report ----------
        footer = Frame(wrapper, bg=COLORS["bg_main"])
        footer.pack(fill="x", pady=(28, 0))

        btn_generate_report = Button(
            footer,
            text="Generate Company Monthly Income Statement",
            command=self.generate_report,
        )
        style_primary_button(btn_generate_report)
        btn_generate_report.pack()


if __name__ == "__main__":
    app = PyTrackApp()
    app.mainloop()
