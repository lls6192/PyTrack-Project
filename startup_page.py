from tkinter import *
from tkinter import ttk

def create_new_location():
    # Code to create a new location
    pass

def cmd_submit():
    selected_location = cb.get()
    print(f"Selected location: {selected_location}")
    # Code to handle the selected location
    pass

# Create Window
root_window = Tk()
root_window.title("PyTrack")
root_window.geometry("400x300")

# Title
title = Label(root_window, text="Welcome to PyTrack!", font=("Arial", 24)).pack(pady=20)

# Label for Selecting an Existing Location
Label(root_window, text="Select an Existing Location:").pack()

# Dropdown options  
existing_locations = ["Webster", "Pittsford", "Henrietta"]

# Combobox  
cb = ttk.Combobox(root_window, values=existing_locations)
cb.set("Select a location")
cb.pack()

# Button to display selection  
Button(root_window, text="Submit", command = cmd_submit).pack()

root_window.mainloop()

