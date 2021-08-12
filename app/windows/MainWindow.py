import tkinter as tk
from .GraphWindow import GraphWindow

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
         
        tk.Label(self, text ="This is the main window") \
            .pack(side = tk.TOP, pady = 10)

        btn = tk.Button(self,
             text ="Click to open graph window")
        btn.bind("<Button>",
                lambda _: GraphWindow(self))
        btn.pack(pady = 10)