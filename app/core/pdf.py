import logging
import os
import comtypes.client
import xlwings as xw
import sys
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
figure_width = 450
figure_height = 264

def get_pdf(path, **kwgs):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    templateFilePath = os.path.join(base_path, 'app', 'core', 'testing.xlsx')

    tablePath = os.path.join(path, 'pdf_table.xlsx')
    hvl_al_fig = os.path.join(path, 'HVL_Al.png')
    hvl_cu_fig = os.path.join(path, 'HVL_Cu.png')
    kvp_fig = os.path.join(path, 'kVp.png')

    try:
        subtable_df = pd.read_excel(tablePath, sheet_name='subset')
        total1_df = pd.read_excel(tablePath, sheet_name='total-1')
        total2_df = pd.read_excel(tablePath, sheet_name='total-2')
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

    sheet.range('G21').value = kwgs["address1"] # Address 1
    sheet.range('G22').value = kwgs["address2"] # Address 2

    sheet.range('G25').value = kwgs["model"] + ' ' + kwgs["serial"] # Chamber Information
    sheet.range('G106').value = kwgs["model"] + ' ' + kwgs["serial"] # Chamber Information

    sheet.range('G27').value = kwgs["period"] #Date of Measurement: Option -> 2-6 July 2021 or Option 2-> 2 July 2021 to 6 July 2021
    sheet.range('G118').value = kwgs["period"] #Date of Measurement: Option -> 2-6 July 2021 or Option 2-> 2 July 2021 to 6 July 2021

    sheet.range('G31').value = kwgs["operator"] #Name of Operator of latest run
    sheet.range('G32').value = kwgs["operator"] #Name of Operator of latest run

    sheet.range('G33').value = kwgs["report_date"] + ' ' #Report generation date/current

    sheet.range('G107').value = kwgs["ic_hv"] #Client RAW File, IC HV Value

    sheet.range('G108').value = kwgs["polarity"] #if above is negative, then here is positive

    #insert table 1 @ Cell A122 or Replace NK value from Q124 to Q134

    # sheet.range('Q124:Q134').value = subtable_df["NK [2]"].to_list()
    sheet.range('A124').options(transpose=True).value = subtable_df["Beam code"].to_list()
    sheet.range('C124').options(transpose=True).value = subtable_df["Tube voltage"].to_list()
    sheet.range('E124').options(transpose=True).value = subtable_df["Added filter(mm Al)"].to_list()
    sheet.range('G124').options(transpose=True).value = subtable_df["Added filter(mm Cu)"].to_list()
    sheet.range('I124').options(transpose=True).value = subtable_df["HVL(mm Al)"].to_list()
    sheet.range('K124').options(transpose=True).value = subtable_df["HVL(mm Cu)"].to_list()
    sheet.range('M124').options(transpose=True).value = subtable_df["Nominal effective energy [1]"].to_list()
    sheet.range('O124').options(transpose=True).value = subtable_df["Nominal air kerma rate"].to_list()
    sheet.range('Q124').options(transpose=True).value = subtable_df["NK [2]"].to_list()
    sheet.range('S124').options(transpose=True).value = subtable_df["U %"].to_list()


    #insert table 2 @ Cell A145 or Replace NK value from Q147 to Q186
    # sheet.range('Q147:Q186').value = total1_df["NK [2]"].to_list()
    sheet.range('A147').options(transpose=True).value = total1_df["Beam code"].to_list()
    sheet.range('C147').options(transpose=True).value = total1_df["Tube voltage"].to_list()
    sheet.range('E147').options(transpose=True).value = total1_df["Added filter(mm Al)"].to_list()
    sheet.range('G147').options(transpose=True).value = total1_df["Added filter(mm Cu)"].to_list()
    sheet.range('I147').options(transpose=True).value = total1_df["HVL(mm Al)"].to_list()
    sheet.range('K147').options(transpose=True).value = total1_df["HVL(mm Cu)"].to_list()
    sheet.range('M147').options(transpose=True).value = total1_df["Nominal effective energy [1]"].to_list()
    sheet.range('O147').options(transpose=True).value = total1_df["Nominal air kerma rate"].to_list()
    sheet.range('Q147').options(transpose=True).value = total1_df["NK [2]"].to_list()
    sheet.range('S147').options(transpose=True).value = total1_df["U %"].to_list()

    #insert table 2-A @ Cell A192 or Replace NK value from Q194 to Q215
    # sheet.range('Q194:Q215').value = total2_df["NK [2]"].to_list()
    sheet.range('A194').options(transpose=True).value = total2_df["Beam code"].to_list()
    sheet.range('C194').options(transpose=True).value = total2_df["Tube voltage"].to_list()
    sheet.range('E194').options(transpose=True).value = total2_df["Added filter(mm Al)"].to_list()
    sheet.range('G194').options(transpose=True).value = total2_df["Added filter(mm Cu)"].to_list()
    sheet.range('I194').options(transpose=True).value = total2_df["HVL(mm Al)"].to_list()
    sheet.range('K194').options(transpose=True).value = total2_df["HVL(mm Cu)"].to_list()
    sheet.range('M194').options(transpose=True).value = total2_df["Nominal effective energy [1]"].to_list()
    sheet.range('O194').options(transpose=True).value = total2_df["Nominal air kerma rate"].to_list()
    sheet.range('Q194').options(transpose=True).value = total2_df["NK [2]"].to_list()
    sheet.range('S194').options(transpose=True).value = total2_df["U %"].to_list()


    #Chart 1: N vs KvP Chart @ Cell A220
    sheet.pictures.add(kvp_fig, top=sheet.range('A220').top, left=sheet.range('A220').left, name='kVp', update=True, width=figure_width, height=figure_height)
    #Chart 2: N vs HVL Chart (mm Al) @ Cell A245
    sheet.pictures.add(hvl_al_fig, top=sheet.range('A244').top, left=sheet.range('A245').left, name='Al', update=True, width=figure_width, height=figure_height)
    #Chart 3: N vs HVL Chart (mm Cu) @ Cell A272
    sheet.pictures.add(hvl_cu_fig, top=sheet.range('A271').top, left=sheet.range('A272').left, name='Cu', update=True, width=figure_width, height=figure_height)


    #Footer Values
    sheet.range('A56').value = "Calibration No: " + kwgs["cal_num"] #CAL Number
    sheet.range('I56').value = "Calibration No: " + kwgs["cal_num"] #CAL Number

    app = xw.apps.active
    wb.save(templateFilePath) # excel template file path
    app.quit()

    app = comtypes.client.CreateObject('Excel.Application')
    app.Visible = False

    infile = os.path.join(templateFilePath)
    outfile = os.path.join(path, 'ClientReport.pdf')

    doc = app.Workbooks.Open(infile)
    doc.ExportAsFixedFormat(0, outfile, 1, 0)
    doc.Close()
    app.Quit()