import tkinter as tk
from tkintertable import TableCanvas, TableModel
from .GraphWindow import GraphWindow

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
         
        tk.Label(self, text ="This is the main window") \
            .pack(side = tk.TOP, pady = 10)

        btn = tk.Button(self,
             text ="Add new job")
        btn.pack(pady = 10)

        table_frame = tk.Frame(self)
        table_frame.pack(side=tk.BOTTOM, pady=10, fill=tk.BOTH)
        table = TableCanvas(table_frame, data={
            1: {'id': 1, 'name': 'Test client', 'address': '100 Street'},
            2: {'id': 2, 'name': 'Test client2', 'address': '200 Street'},
        })
        table.show()