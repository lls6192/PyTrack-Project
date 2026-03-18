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

# Make columns expand (for centering)
root_window.columnconfigure(0, weight=1)
root_window.columnconfigure(1, weight=1)

# Title
title = Label(root_window, text="Welcome to PyTrack!", font=("Arial", 24))
title.grid(row=0, column=0, columnspan=2, pady=20, sticky="ew")

#------------------------------------------------------------------
# Label for Selecting an Existing Location
lbl_existing_location = Label(root_window, text="Select an Existing Location:")
lbl_existing_location.grid(row=1, column=0, padx=40, pady=1, sticky="w")

# Dropdown options  
existing_locations = ["Webster", "Pittsford", "Henrietta"]

# Combobox  
cb = ttk.Combobox(root_window, values=existing_locations)
cb.set("Select a location")
cb.grid(row=2, column=0, padx=40, pady=1, sticky="w")

# Button to display selection  
btn_submit = Button(root_window, text="Submit", command = cmd_submit)
btn_submit.grid(row=3, column=0, padx=40, pady=1, sticky="w")
#------------------------------------------------------------------

# Button to create a new location
btn_create_new_location = Button(root_window, text="Create New Location", command=create_new_location)
btn_create_new_location.grid(row=2, column=1, padx=5)

root_window.mainloop()

