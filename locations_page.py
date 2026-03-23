from tkinter import *
from tkinter import ttk

class LocationPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        label = Label(self, text=f"Store Location Page", font=("Times New Roman", 24))
        label.pack(pady=20)

        self.location_label = Label(self, text="", font=("Times New Roman", 16))
        self.location_label.pack(pady=10)

        btn_back = Button(
            self,
            text="Back",
            command=lambda: controller.show_frame("StartPage")
        )
        btn_back.pack()

    def set_location(self, location_name):
        self.location_label.config(text=f"Selected: {location_name}")