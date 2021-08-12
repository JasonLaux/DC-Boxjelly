import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master=master)

        tk.Label(self, text="A graph") \
            .pack(padx=10, pady=10)

        canvas = FigureCanvasTkAgg(self._create_figure(), self)
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def _create_figure(self):
        f = Figure(figsize=(5,5), dpi=100)
        a = f.add_subplot(111)
        a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])

        return f
    