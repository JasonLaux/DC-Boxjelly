import logging
import os
import comtypes.client
import xlwings as xw
import sys
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_pdf(**kwgs):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    templateFilePath = os.path.join(base_path, 'app', 'pdf', 'testing.xlsx')

    tablePath = os.path.join(base_path, 'app', 'pdf', 'test', 'pdf_table.xlsx')
    hvl_al_fig = os.path.join(base_path, 'app', 'pdf', 'test', 'HVL_Al.png')
    hvl_cu_fig = os.path.join(base_path, 'app', 'pdf', 'test', 'HVL_Cu.png')
    kvp_fig = os.path.join(base_path, 'app', 'pdf', 'test', 'kVp.png')

    try:
        subtable_df = pd.read_excel(tablePath, usecols=["NK [2]"], sheet_name='subset')
        total1_df = pd.read_excel(tablePath, usecols=["NK [2]"], sheet_name='total-1')
        total2_df = pd.read_excel(tablePath, usecols=["NK [2]"], sheet_name='total-2')
    except:
        logger.debug("Cannot read table file properly!")


    logger.debug(kwgs)
    app = xw.App(visible = False)
    wb = xw.Book(templateFilePath) #excel template file path
    sheet = wb.sheets['MEXReport']

    sheet.range('T13').value = kwgs["cal_num"] #CAL NUMBER

    sheet.range('G20').value = kwgs["client_name"] #Client Name
    sheet.range('G105').value = kwgs["client_name"] #Client Name
    sheet.range('L139').value = "Calibrated by: " + kwgs["client_name"] #Client Name #####

    sheet.range('G21').value = kwgs["address1"] #Address 1
    sheet.range('G22').value = kwgs["address2"] #Address 2

    sheet.range('G25').value = kwgs["model"] #Chamber Information
    sheet.range('G106').value = kwgs["serial"] #Chamber Information

    sheet.range('G27').value = kwgs["period"] #Date of Measurement: Option -> 2-6 July 2021 or Option 2-> 2 July 2021 to 6 July 2021
    sheet.range('G118').value = kwgs["period"] #Date of Measurement: Option -> 2-6 July 2021 or Option 2-> 2 July 2021 to 6 July 2021

    sheet.range('G31').value = kwgs["operator"] #Name of Operator of latest run
    sheet.range('G32').value = kwgs["operator"] #Name of Operator of latest run

    sheet.range('G33').value = kwgs["report_date"] #Report generation date/current

    sheet.range('G107').value = "Variable + on the guard electrode" #Client RAW File, IC HV Value

    sheet.range('G108').value = "Positive + (Central  Electrode Negative" #if above is negative, then here is positive

    #insert table 1 @ Cell A122 or Replace NK value from Q124 to Q134

    # sheet.range('Q124:Q134').value = subtable_df["NK [2]"].to_list()
    sheet.range('Q124').options(transpose=True).value = subtable_df["NK [2]"].to_list()

    #insert table 2 @ Cell A145 or Replace NK value from Q147 to Q186
    # sheet.range('Q147:Q186').value = total1_df["NK [2]"].to_list()
    sheet.range('Q147').options(transpose=True).value = total1_df["NK [2]"].to_list()

    #insert table 2-A @ Cell A192 or Replace NK value from Q194 to Q215
    # sheet.range('Q194:Q215').value = total2_df["NK [2]"].to_list()
    sheet.range('Q194').options(transpose=True).value = total2_df["NK [2]"].to_list()


    #Chart 1: N vs KvP Chart @ Cell A220
    sheet.pictures.add(kvp_fig, name='Chart 1', update=True)
    #Chart 2: N vs HVL Chart (mm Al) @ Cell A245
    sheet.pictures.add(hvl_al_fig, name='Chart 2', update=True)
    #Chart 3: N vs HVL Chart (mm Cu) @ Cell A272
    sheet.pictures.add(hvl_cu_fig, name='Chart 3', update=True)


    #Footer Values
    sheet.range('A56').value = "Calibration No: + " + kwgs["cal_num"] #CAL Number
    sheet.range('I56').value = "Calibration No: + " + kwgs["cal_num"] #CAL Number

    app = xw.apps.active
    wb.save(templateFilePath) # excel template file path
    app.quit()

    app = comtypes.client.CreateObject('Excel.Application')
    app.Visible = False

    # infile = os.path.join(templateFilePath)
    # outfile = os.path.join(base_path, 'app', 'pdf', 'test', 'ClientReport.pdf')

    # doc = app.Workbooks.Open(infile)
    # doc.ExportAsFixedFormat(0, outfile, 1, 0)
    # doc.Close()
    # app.Quit()