from tkinter import *
from tkinter import ttk
from tkinter import messagebox, simpledialog
from locations_page import LocationPage

# Dropdown options  
existing_locations = ["Webster", "Pittsford", "Henrietta"]

class PyTrackApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("PyTrack")
        self.geometry("620x500")

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
        # Check if the new location already exists
        if new_location in existing_locations:
            messagebox.showerror("Error", f"Location '{new_location}' already exists.")
        # Check if the new location is valid (not empty or just whitespace)
        elif new_location not in existing_locations and new_location is not None and new_location.strip() != "":
            existing_locations.append(new_location)
            self.cb['values'] = existing_locations
            messagebox.showinfo("Create New Location", f"Location created: {new_location}")
            # Code to open the new location's page
            pass

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
        self.cb = ttk.Combobox(self, values=sorted(existing_locations), state="readonly")
        self.cb.set("Select a location")
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

if __name__ == "__main__":
    app = PyTrackApp()
    app.mainloop()
