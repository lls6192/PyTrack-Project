from tkinter import *
from tkinter import ttk

class LocationPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.title_label = Label(self, text=f"Store Location Page ", font=("Times New Roman", 24))
        self.title_label.pack(pady=20)

        btn_back = Button(
            self,
            text="Back",
            command=lambda: controller.show_frame("StartPage")
        )
        btn_back.pack()

    def set_location(self, location_name):
        # Update title
        self.title_label.config(text=f"Store Location Page - {location_name}" )
