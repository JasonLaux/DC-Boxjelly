import pandas as pd
import warnings
import numpy as np
import os
import sys
import re
from app.core.resolvers import summary, pdf_table, calculator
from matplotlib import pyplot as plt
# python -m app.pdf.main

if __name__ == '__main__':
    results = []
    client_path = r'C:\D_Disk\projects\DC-Boxjelly\data\jobs\CAL00001\PTW 30013_5122\MEX\1\raw\client.csv'
    lab_path = r'C:\D_Disk\projects\DC-Boxjelly\data\jobs\CAL00001\PTW 30013_5122\MEX\1\raw\lab.csv'
    results.append(calculator(client=client_path, lab=lab_path))
    runs = ['run1']
    summary_table = summary(runs, results)

    table_pdf = pdf_table(summary_table, results[0].df_otherConstant)
    # print(table_pdf.columns.values)
    # ['Tube voltage' 'Added filter(mm Al)' 'Added filter(mm Cu)' 'HVL(mm Al)' 'HVL(mm Cu)' 'Nominal effective energy [1]' 'air kerma rate' 'NK [2]' 'U %']
    scd_figure_votages = [40, 50, 60, 70, 80, 90, 100, 120, 140, 150]
    third_figure_votages = [80, 90, 100, 120, 140, 150, 200, 250, 280, 300, 320]

    # print(table_pdf.index.to_list())
    plot1 = plt.figure(1)
    for vot in scd_figure_votages:
        match_text = "\D" + str(vot) + "$"
        beam_code = [name for name in table_pdf.index.to_list() if re.search(match_text, name)]
        x = table_pdf.loc[beam_code, 'HVL(mm Al)'].to_list()
        x = [np.round(item, 2) if item != '' else item for item in x]
        y = table_pdf.loc[beam_code, 'NK [2]'].to_list()
        plt.plot(x, y, '.-', label = str(vot) + " kVp")
        
    plt.xlabel(r'HVL (mm Al)', fontweight='bold')
    plt.ylabel(r'$\bfN_k$(mGy/nc)', fontweight='bold')
    # plt.xticks(np.arange(5, 15, 1.0))
    plt.legend(ncol=2)

    plot2 = plt.figure(2)
    for vot in third_figure_votages:
        match_text = "\D" + str(vot) + "$"
        beam_code = [name for name in table_pdf.index.to_list() if re.search(match_text, name)]
        x = table_pdf.loc[beam_code, 'HVL(mm Cu)'].to_list()
        x = [np.round(item, 2) if item != '' else item for item in x]
        y = table_pdf.loc[beam_code, 'NK [2]'].to_list()
        plt.plot(x, y, '.-', label = str(vot) + " kVp")
        
    plt.xlabel(r'HVL (mm Cu)', fontweight='bold')
    plt.ylabel(r'$\bfN_k$(mGy/nc)', fontweight='bold')
    # plt.xticks(np.arange(5, 15, 1.0))
    plt.legend(ncol=2)
    plt.show()