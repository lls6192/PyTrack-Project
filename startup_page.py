from tkinter import *
from tkinter import ttk
from tkinter import messagebox, simpledialog

# Dropdown options  
existing_locations = ["Webster", "Pittsford", "Henrietta"]

def create_new_location():
    # Code to create a new location
    new_location = simpledialog.askstring("Create New Location", "Enter the name of the new location:")
    if new_location:
        existing_locations.append(new_location)
        cb['values'] = existing_locations
        messagebox.showinfo("Create New Location", f"Location created: {new_location}")
        # Code to open the new location's page
        pass

def cmd_submit():
    selected_location = cb.get()
    print(f"Selected location: {selected_location}")
    # Code to handle the selected location
    pass

# Create Window
root_window = Tk()
root_window.title("PyTrack")
root_window.geometry("500x300")

# Make columns expand (for centering)
root_window.columnconfigure(0, weight=1)
root_window.columnconfigure(1, weight=1)

# Title
title = Label(root_window, text="Welcome to PyTrack!", font=("Times New Roman", 24))
title.grid(row=0, column=0, columnspan=2, pady=20, sticky="ew")

#------------------------------------------------------------------
# Label for Selecting an Existing Location
lbl_existing_location = Label(root_window, text="Select an Existing Location:", font=("Times New Roman", 16, 'bold'))
lbl_existing_location.grid(row=1, column=0, padx=40, pady=1, sticky="w")

# Combobox  
cb = ttk.Combobox(root_window, values=sorted(existing_locations))
cb.set("Select a location")
cb.grid(row=2, column=0, padx=40, pady=1, sticky="w")

# Button to display selection  
btn_submit = Button(root_window, text="Submit", command = cmd_submit)
btn_submit.grid(row=3, column=0, padx=40, pady=1)
#------------------------------------------------------------------
# Label for Creating a New Location
lbl_new_location = Label(root_window, text="Create a New Location:", font=("Times New Roman", 16, 'bold'))
lbl_new_location.grid(row=1, column=1, padx=5, pady=1, sticky="w")

# Button to create a new location
btn_create_new_location = Button(root_window, text="Create New Location", command=create_new_location)
btn_create_new_location.grid(row=2, column=1, padx=5, sticky="w")

root_window.mainloop()

