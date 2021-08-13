import tkinter as tk
from tksheet import Sheet
from .GraphWindow import GraphWindow

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Job List')

        btn_group = tk.Frame(self)
        btn_group.pack(side=tk.TOP, pady=10)

        btn_add = tk.Button(btn_group, text ="Add")
        btn_add.pack(side=tk.LEFT, padx=2, pady=2)
        btn_edit = tk.Button(btn_group, text ="Edit")
        btn_edit.pack(side=tk.LEFT, padx=2, pady=2)

        table_frame = tk.Frame(self)
        table_frame.pack(side=tk.BOTTOM, pady=10, fill=tk.BOTH)
        table = Sheet(table_frame, data=[
            ['id', 'name', 'address'],
            [1, 'Test client', '100 Street'],
            [2, 'Test client2', '200 Street'],
        ])
        table.enable_bindings()
        table.grid(row = 0, column = 0, sticky = "nswe")