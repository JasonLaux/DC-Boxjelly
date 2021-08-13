import matplotlib
matplotlib.use("TkAgg")

from windows.MainWindow import MainWindow

def main():
    main = MainWindow()
    main.mainloop()

if __name__ == '__main__':
    main()