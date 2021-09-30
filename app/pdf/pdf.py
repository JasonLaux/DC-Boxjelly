import os
import comtypes.client
import xlwings as xw

app = xw.App(visible = False)
wb = xw.Book(r'C:\Users\John\Desktop\testing.xlsx') #excel template file path
sheet = wb.sheets['MEXReport']

sheet.range('T13').value = "CAL NUMBER" #CAL NUMBER

sheet.range('G20').value = "Client Name" #Client Name
sheet.range('G105').value = "Report Date" #Client Name
sheet.range('L139').value = "Calibrated by: Operator " #Client Name

sheet.range('G21').value = "Address 1" #Address 1
sheet.range('G22').value = "Address 2" #Address 2

sheet.range('G25').value = "Chamber Info" #Chamber Information
sheet.range('G106').value = "Chamber Info" #Chamber Information

sheet.range('G27').value = "Date of measurement" #Date of Measurement: Option -> 2-6 July 2021 or Option 2-> 2 July 2021 to 6 July 2021
sheet.range('G118').value = "Date of measurement" #Date of Measurement: Option -> 2-6 July 2021 or Option 2-> 2 July 2021 to 6 July 2021

sheet.range('G31').value = "Test By" #Name of Operator of latest run
sheet.range('G32').value = "Report By" #Name of Operator of latest run

sheet.range('G33').value = "Report Date" #Report generation date/current

sheet.range('G107').value = "Variable + on the guard electrode" #Client RAW File, IC HV Value

sheet.range('G108').value = "Positive + (Central  Electrode Negative" #if above is negative, then here is positive

#insert table 1 @ Cell A122 or Replace NK value from Q124 to Q134

#insert table 2 @ Cell A145 or Replace NK value from Q147 to Q186
#insert table 2-A @ Cell A192 or Replace NK value from Q194 to Q215

#Chart 1: N vs KvP Chart @ Cell A220
#Chart 2: N vs HVL Chart (mm Al) @ Cell A245
#Chart 2: N vs HVL Chart (mm Cu) @ Cell A272

#Footer Values
sheet.range('A56').value = "Calibration No: + CAL NUMBER" #CAL Number
sheet.range('I56').value = "Calibration No: + CAL NUMBER" #CAL Number

app = xw.apps.active
wb.save(r'C:\Users\John\Desktop\testing.xlsx') # excel template file path
app.quit()

SOURCE_DIR = r'C:\Users\John\Desktop'
TARGET_DIR = r'C:\Users\John\Desktop'

app = comtypes.client.CreateObject('Excel.Application')
app.Visible = False

infile = os.path.join(os.path.abspath(SOURCE_DIR), 'testing.xlsx')
outfile = os.path.join(os.path.abspath(TARGET_DIR), 'ClientReport.pdf')

doc = app.Workbooks.Open(infile)
doc.ExportAsFixedFormat(0, outfile, 1, 0)
doc.Close()
app.Quit()