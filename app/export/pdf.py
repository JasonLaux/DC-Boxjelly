import logging
import os
import xlwings as xw
import sys
import pandas as pd
import numpy as np
import pythoncom
import win32com.client
from pywintypes import com_error
import shutil

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
figure_width = 450
figure_height = 450

def get_pdf(temp_folder, **kwgs):
    pythoncom.CoInitialize()

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    templateFilePath = os.path.join(base_path, 'app', 'export', 'pdf_template.xlsx')
    
    tablePath = os.path.join(temp_folder, 'pdf_table.xlsx')
    hvl_al_fig = os.path.join(temp_folder, 'HVL_Al.png')
    hvl_cu_fig = os.path.join(temp_folder, 'HVL_Cu.png')
    kvp_fig = os.path.join(temp_folder, 'kVp.png')

    doc_path = os.path.join(temp_folder, 'document.xlsx')
    shutil.copy(templateFilePath, doc_path)

    try:
        subtable_df = pd.read_excel(tablePath, sheet_name='subset', engine='openpyxl')
        total1_df = pd.read_excel(tablePath, sheet_name='total-1', engine='openpyxl')
        total2_df = pd.read_excel(tablePath, sheet_name='total-2', engine='openpyxl')
    except:
        logger.debug("Cannot read table file properly!")

    logger.debug(kwgs)
    app = xw.App(visible = False)
    wb = xw.Book(doc_path) #excel template file path
    sheet = wb.sheets['MEXReport']

    sheet.range('T12').value = kwgs["cal_num"] #CAL NUMBER

    sheet.range('G19').value = kwgs["client_name"] #Client Name
    sheet.range('G111').value = kwgs["client_name"] #Client Name
    sheet.range('L145').value = "Calibrated by: " + kwgs["client_name"] #Client Name #####

    sheet.range('G20').value = kwgs["address1"] # Address 1
    sheet.range('G21').value = kwgs["address2"] # Address 2

    sheet.range('G24').value = kwgs["model"] + ' ' + kwgs["serial"] # Chamber Information
    sheet.range('G112').value = kwgs["model"] + ' ' + kwgs["serial"] # Chamber Information

    sheet.range('G26').value = kwgs["period"] #Date of Measurement: Option -> 2-6 July 2021 or Option 2-> 2 July 2021 to 6 July 2021
    sheet.range('G124').value = kwgs["period"] #Date of Measurement: Option -> 2-6 July 2021 or Option 2-> 2 July 2021 to 6 July 2021

    sheet.range('G30').value = kwgs["operator"] #Name of Operator of latest run
    sheet.range('G31').value = kwgs["operator"] #Name of Operator of latest run

    sheet.range('G32').value = kwgs["report_date"] + ' ' #Report generation date/current

    sheet.range('G113').value = kwgs["ic_hv"] #Client RAW File, IC HV Value

    sheet.range('G114').value = kwgs["polarity"] #if above is negative, then here is positive

    #insert table 1 @ Cell A122 or Replace NK value from Q124 to Q134

    # sheet.range('Q124:Q134').value = subtable_df["NK [2]"].to_list()
    sheet.range('A130').options(transpose=True).value = subtable_df["Beam code"].to_list()
    sheet.range('C130').options(transpose=True).value = subtable_df["Tube voltage"].to_list()
    sheet.range('E130').options(transpose=True).value = subtable_df["Added filter(mm Al)"].to_list()
    sheet.range('G130').options(transpose=True).value = subtable_df["Added filter(mm Cu)"].to_list()
    sheet.range('I130').options(transpose=True).value = subtable_df["HVL(mm Al)"].to_list()
    sheet.range('K130').options(transpose=True).value = subtable_df["HVL(mm Cu)"].to_list()
    sheet.range('M130').options(transpose=True).value = subtable_df["Nominal effective energy [1]"].to_list()
    sheet.range('O130').options(transpose=True).value = subtable_df["Nominal air kerma rate"].to_list()
    sheet.range('Q130').options(transpose=True).value = subtable_df["NK [2]"].to_list()
    sheet.range('S130').options(transpose=True).value = subtable_df["U %"].to_list()


    #insert table 2 @ Cell A145 or Replace NK value from Q147 to Q186
    # sheet.range('Q147:Q186').value = total1_df["NK [2]"].to_list()
    sheet.range('A149').options(transpose=True).value = total1_df["Beam code"].to_list()
    sheet.range('C149').options(transpose=True).value = total1_df["Tube voltage"].to_list()
    sheet.range('E149').options(transpose=True).value = total1_df["Added filter(mm Al)"].to_list()
    sheet.range('G149').options(transpose=True).value = total1_df["Added filter(mm Cu)"].to_list()
    sheet.range('I149').options(transpose=True).value = total1_df["HVL(mm Al)"].to_list()
    sheet.range('K149').options(transpose=True).value = total1_df["HVL(mm Cu)"].to_list()
    sheet.range('M149').options(transpose=True).value = total1_df["Nominal effective energy [1]"].to_list()
    sheet.range('O149').options(transpose=True).value = total1_df["Nominal air kerma rate"].to_list()
    sheet.range('Q149').options(transpose=True).value = total1_df["NK [2]"].to_list()
    sheet.range('S149').options(transpose=True).value = total1_df["U %"].to_list()

    #insert table 2-A @ Cell A192 or Replace NK value from Q194 to Q215
    # sheet.range('Q194:Q215').value = total2_df["NK [2]"].to_list()
    sheet.range('A197').options(transpose=True).value = total2_df["Beam code"].to_list()
    sheet.range('C197').options(transpose=True).value = total2_df["Tube voltage"].to_list()
    sheet.range('E197').options(transpose=True).value = total2_df["Added filter(mm Al)"].to_list()
    sheet.range('G197').options(transpose=True).value = total2_df["Added filter(mm Cu)"].to_list()
    sheet.range('I197').options(transpose=True).value = total2_df["HVL(mm Al)"].to_list()
    sheet.range('K197').options(transpose=True).value = total2_df["HVL(mm Cu)"].to_list()
    sheet.range('M197').options(transpose=True).value = total2_df["Nominal effective energy [1]"].to_list()
    sheet.range('O197').options(transpose=True).value = total2_df["Nominal air kerma rate"].to_list()
    sheet.range('Q197').options(transpose=True).value = total2_df["NK [2]"].to_list()
    sheet.range('S197').options(transpose=True).value = total2_df["U %"].to_list()


    #Chart 1: N vs KvP Chart @ Cell A220
    sheet.pictures.add(kvp_fig, top=sheet.range('A225').top, left=sheet.range('A220').left, name='kVp', update=True, width=figure_width, height=figure_height)
    #Chart 1 Title
    sheet.range('C243').value = "Figure 1: Calibration coefficients for " + kwgs["model"] +" serial number " + kwgs["serial"] + " grouped by kVp"

    #Chart 2: N vs HVL Chart (mm Al) @ Cell A245
    sheet.pictures.add(hvl_al_fig, top=sheet.range('A251').top, left=sheet.range('A245').left, name='Al', update=True, width=figure_width, height=figure_height)
    #Chart 2 Title
    sheet.range('C273').value = "Figure 2: Calibration coefficients for " + kwgs["model"] + " serial number " + kwgs["serial"] + " versus HVL (mm Al)"

    #Chart 3: N vs HVL Chart (mm Cu) @ Cell A272
    sheet.pictures.add(hvl_cu_fig, top=sheet.range('A278').top, left=sheet.range('A272').left, name='Cu', update=True, width=figure_width, height=figure_height)
    #Chart 3 Title
    sheet.range('C300').value = "Figure 3: Calibration coefficients for " + kwgs["model"] + " serial number " + kwgs["serial"] +" versus HVL (mm Cu)"

    #Footer Values
    sheet.range('A59').value = "Calibration No: " + kwgs["cal_num"] #CAL Number
    sheet.range('I59').value = "Report Date: " + kwgs["report_date"] #CAL Number

    wb.save(doc_path)
    wb.close()

    doc_pdf = os.path.join(temp_folder, 'document.pdf')

    excel = win32com.client.Dispatch("Excel.Application")
    try:
        print('Start conversion to PDF')
        wb = excel.Workbooks.Open(doc_path)
        wb_list = [1]
        wb.Worksheets(wb_list).Select()
        wb.ActiveSheet.ExportAsFixedFormat(0, doc_pdf)
    except com_error as e:
        logger.error('Failed', exc_info=e)
    finally:
        wb.Close()

    return doc_pdf

    # MacOS doesn't support win32com.
    # if you're going to test the PDF generation, please use the code below
    # note that the quality of pictures would get blurred

    # import comtypes.client
    # app = comtypes.client.CreateObject('Excel.Application')
    # app.Visible = False

    # infile = os.path.join(templateFilePath)
    # outfile = os.path.join(path, 'ClientReport.pdf')

    # doc = app.Workbooks.Open(infile)
    # doc.ExportAsFixedFormat(0, outfile, 1, 0)
    # doc.Close()
    # app.Quit()

    
    