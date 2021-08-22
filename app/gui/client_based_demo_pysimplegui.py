'''
    File name: client_based_GUI
    Author: Chien-Chih Wang
    Date created: 14/08/2020
    Python version: 3.9

    The file is built for the demonstration of PysimpleGUI, which fully supports Tkinter,
    and make the GUI design easiler. The layout is according to the client's first GUI
    suggestion.
'''
import PySimpleGUI as sg

# fake data
chamber1 = ["NE2571", "NE2572", "NE2573"]
chamber1_serial = ["123", "456", "789"]
chamber2 = ["PTW30013", "PTW30014", "PTW30015"]
chamber2_serial = ["00110", "00111", "00112"]

# column start from 0
col_0 = [
  [sg.Text("Job number")],
  [sg.Text("Chamber1 make/model")],
  [sg.Text("Chamber1 serial")],
  [sg.Text("Chamber2 make/model")],
  [sg.Text("Chamber2 serial")]
]

col_1 = [
  [sg.InputText(size=(10,1))],
  [sg.InputCombo(chamber1, default_value=chamber1[0],size=(10,1))],
  [sg.InputCombo(chamber1_serial, default_value=chamber1_serial[0],size=(10,1))],
  [sg.InputCombo(chamber2, default_value=chamber2[0],size=(10,1))],
  [sg.InputCombo(chamber2_serial, default_value=chamber2_serial[0],size=(10,1))]
]

col_21 = [
  [sg.Text("Client name")],
  [sg.InputText(size=(10,1))],
  [sg.Text("Client Address")],
  [sg.InputText(size=(30,1))]
]

col_22 = [
  [sg.Button(button_text="Add new run"), sg.Button(button_text="Compare data")],
  [sg.Button(button_text="Create PDF"), sg.Button(button_text="Create DCC")],
  # [sg.Canvas(size=(300,300),background_color="#D3B8B2")]
]

col_2 = [
  [sg.Frame(layout=[[sg.Column(col_21, vertical_alignment='c')]],
    vertical_alignment='c',title='')],
  [sg.Frame(layout=[[sg.Column(col_22, vertical_alignment = 'c')]],
  vertical_alignment = 'c',title='')]
]

# the layout would be the interface for the user
# each list in the layout would be a row
# the "row list" could have multiple items as columns
# the row, column grid system is easy to use
# reference:
# https://stackoverflow.com/questions/65083402/pysimplegui-align-rows-on-different-columns
layout = [
  # row 0
  [sg.Column(col_0),sg.Column(col_1,justification="top"),sg.Column(col_2)],
  # row 1
  [sg.Canvas(size=(600,300),background_color="#D3B8B2")]
]

def make_window():
    window = sg.Window('Window Title', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break

    window.close()

if __name__ == '__main__':
  make_window()