"""
This file contains the code to do the calculation.

Each resolver receives a model and outputs the calculated result, which can
be a model or just a matrix.
"""
import pandas as pd
import warnings
import numpy as np
import os
import sys
import re

warnings.filterwarnings('ignore')

class Header_data():
    """
    the object to store run info data which read from the head of the raw data
    """
    def __init__(self):
        self.CAL_num = ""
        self.Client_name = ""
        self.address_1 = ""
        self.address_2 = ""
        self.operator = ""
        self.serial = ""
        self.model = ""


class Processed_data():
    """
    the object to store data which read from the raw data
    """
    def __init__(self):
        self.df_before_mean = None
        self.df_mean = None
        self.df_after_mean = None


class result_data():
    """
    Using object to save result in order to avoid too much returned elements
    """
    def __init__(self):
        self.df_NK = None
        self.df_leakage = None
        self.highlight = []
        self.X = []
        self.df_otherConstant = None

class HeaderError(RuntimeError):
    def __init__(self, arg):
        self.args = arg


def calculator(client, lab):
    """
    This function will calculate one run of NK (calibration coefficient) and the leakage current values. Besides,
    the coordinate of the leakage value which need to be highlighted is needed so that the front-end will be easy to
    highlight the cell.

    :param client: the client raw data path
    :param lab   : the lab raw data path
    :return      : return a object of the result which includes NK dataframe, leakage value dataframe, the coordinate of
                   the leakage value which need to be highlighted (abs(value) > 0.2), the effective energy
                   dataframe (X), and the list of NK (Y). X and Y is used to plot on chart.
    """
    # extract data
    client_data, duplicate_num = extraction(client)
    lab_data, _ = extraction(lab)

    # order the lab beams to make sure that the further calculation will not have issue
    cats = client_data.df_mean.index.tolist()
    lab_data.df_mean.reset_index(inplace=True)
    lab_data.df_mean['Filter'] = pd.CategoricalIndex(lab_data.df_mean['Filter'], ordered=True, categories=cats)
    lab_data.df_mean.sort_values('Filter', inplace=True)
    lab_data.df_mean.set_index('Filter', inplace=True)

    # client calculation part
    BgdMC1_Before = client_data.df_before_mean['Current1(pA)'].values[0]
    BgdIC1_Before = client_data.df_before_mean['Current2(pA)'].values[0]

    MC1 = (client_data.df_mean['Current1(pA)'] - BgdMC1_Before).to_frame('NK')
    IC1 = (client_data.df_mean['Current2(pA)'] - BgdIC1_Before).to_frame('NK')
    R1 = (client_data.df_mean['Current2(pA)'] - BgdIC1_Before).to_frame('NK') / (client_data.df_mean['Current1(pA)'] - BgdMC1_Before).to_frame('NK')
    TM1 = client_data.df_mean['T(MC)'].to_frame('NK')
    TA1 = client_data.df_mean['T(Air)'].to_frame('NK')

    # lab calculation part
    BgdMC2_Before = lab_data.df_before_mean['Current1(pA)'].values[0]
    BgdIC2_Before = lab_data.df_before_mean['Current2(pA)'].values[0]

    MC2 = (lab_data.df_mean['Current1(pA)'] - BgdMC2_Before).to_frame('NK')
    IC2 = (lab_data.df_mean['Current2(pA)'] - BgdIC2_Before).to_frame('NK')
    R2 = (lab_data.df_mean['Current2(pA)'] - BgdIC2_Before).to_frame('NK') / (lab_data.df_mean['Current1(pA)'] - BgdMC2_Before).to_frame('NK')
    TM2 = lab_data.df_mean['T(MC)'].to_frame('NK')
    TS2 = lab_data.df_mean['T(SC)'].to_frame('NK')
    H2 = lab_data.df_mean['H(%)'].to_frame('NK')

    # read constant and KK from constant excel file
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    # dir_path = os.path.dirname(os.path.realpath(__file__))
    constant = os.path.join(base_path, 'constant.xlsx')
    df_constant = pd.read_excel(constant, sheet_name='constant')
    df_beams = pd.read_excel(constant, sheet_name='Beams')

    # get ma and WE
    Ma = df_constant['ma'].values[0]
    WE = df_constant['WE'].values[0]

    # reform the KK into the same order as client_data.df_mean so that it will be easy to calculate directly
    # (do not need to extract the same index to do calculation. We can just calculate on data frame).

    # get the filter of the first measurement from KK
    df_beams = df_beams[df_beams.Filter.isin(client_data.df_mean.index)]
    cats = client_data.df_mean.index[:-duplicate_num]
    df_beams['Filter'] = pd.CategoricalIndex(df_beams['Filter'], ordered=True, categories=cats)
    df_beams.sort_values('Filter', inplace=True)

    # get the filter which measure two times from KK
    df_beams_duplicate = df_beams[df_beams.Filter.isin(client_data.df_mean.index[:duplicate_num])]
    cats = client_data.df_mean.index[:duplicate_num]
    df_beams_duplicate['Filter'] = pd.CategoricalIndex(df_beams_duplicate['Filter'], ordered=True, categories=cats)
    df_beams_duplicate['Filter'] = [Filter + '*' for Filter in df_beams_duplicate.Filter.tolist()]
    df_beams_duplicate.sort_values('Filter', inplace=True)

    # concate the processed beams
    df_processBeams = pd.concat([df_beams, df_beams_duplicate], axis=0).set_index('Filter')

    # concat together so that KK will have the same order as client_data.df_mean
    df_KK = df_processBeams['Product'].to_frame('NK')

    # Calculating NK
    NK = R2 * WE * df_KK * ((273.15 + TS2) / (273.15 + TM2)) * (0.995766667 + 0.000045 * H2) / (
                Ma * R1 * (273.15 + TA1) / (273.15 + TM1))
    NK = round(NK / 1000000, 2)
    NK.columns = ['NK']

    # leakage
    df_leakage = pd.DataFrame({"Before": [BgdMC1_Before, BgdIC1_Before, BgdMC2_Before, BgdIC2_Before],
                                  "After": [client_data.df_after_mean['Current1(pA)'].values[0],
                                                       client_data.df_after_mean['Current2(pA)'].values[0],
                                                       lab_data.df_after_mean['Current1(pA)'].values[0],
                                                       lab_data.df_after_mean['Current2(pA)'].values[0]]},
                                 index=["Monitor 1", "Chamber (client)", "Monitor 2", "Standard (MEFAC)"])

    # extract the effective energy for plotting the graph
    df_energy = df_processBeams['E_eff'].to_frame()

    # create an object to save result
    result = result_data()

    # saving NK
    result.df_NK = NK

    # saving leakage
    result.df_leakage = round(df_leakage, 2) + 0  # +0 to remove -0.0

    # get the coordinate which the cell need to be highlighted
    result.highlight = [(x, y) for x, y in zip(*np.where(abs(result.df_leakage.values) > 0.2))]

    # saving the graph required data
    result.X = df_energy['E_eff'].to_frame('E_eff')

    # save other constant to result
    result.df_otherConstant = df_processBeams.drop(columns=['Product', 'E_eff']).fillna('')

    return result


def extraction(path):
    """
    This function use to extract the measurement data from the file.

    :param : path: the path of file
    :return: return the measurement data which is extracted from the file. Besides, return the number of
             beams quality which measure two times in order to use in the calculation part
    """
    Backgrounds_num = 0
    Measurements_num = 0
    df_total = None

    with open(path, newline='', encoding="ISO-8859-1") as f:
        for line in f:
            if 'DATA' in line:
                break
            # get the Background number
            elif 'Backgrounds' in line:
                Backgrounds_num = int(line.split(',')[2])

            # get the measurement number
            elif 'Measurements' in line:
                Measurements_num = int(line.split(',')[2])
        df_total = pd.read_csv(f)

    df_total.drop(['kV', 'mA', 'HVLFilter(mm)', 'N', 'P(kPa)', 'Comment'], axis=1, inplace=True)

    # change the column type to numeric
    df_total = df_total.apply(pd.to_numeric, errors='ignore')

    # dataframe of the before xray data
    df_before = df_total[:Backgrounds_num]

    # dataframe of the beam data with open xray
    df_data = df_total[Backgrounds_num:-Backgrounds_num]

    # check the number of measurement for each beam
    df_size = df_data.groupby(['Filter']).size().to_frame('count')

    # seperate the beam which measure two times
    duplicate_beam = list(df_size[df_size['count'] > Measurements_num].index)

    df_noDuplicate = df_data[~df_data.Filter.isin(duplicate_beam)]
    df_duplicate = df_data[df_data.Filter.isin(duplicate_beam)]
    df_first = df_duplicate[:Measurements_num * len(duplicate_beam)]
    df_last = df_duplicate[-Measurements_num * len(duplicate_beam):]

    # put * on the last measurements (which measure two times) of beams' name
    df_last.Filter = [Filter + '*' for Filter in df_last.Filter.tolist()]

    # dataframe of the after xray data
    df_after = df_total[-Backgrounds_num:]

    # average the data and store to object
    data = Processed_data()

    # put the filter which measure two times at the last
    data.df_mean = pd.concat([df_first.groupby(['Filter']).mean(), df_noDuplicate.groupby(['Filter']).mean(),
                              df_last.groupby(['Filter']).mean()], axis=0)

    data.df_before_mean = df_before.groupby(['Filter']).mean()
    data.df_after_mean = df_after.groupby(['Filter']).mean()

    # return number of duplicate_beam since kk need to know how many beams measure two times
    return data, len(duplicate_beam)


def summary(name_list, result_list):
    """
    This function is used to summary all runs of calibration coefficient.
    This function can deal with if the runs do not have same beam quality
    TODO: If all run's beam quality are the same. df_energy and df_result can be merged directly

    :param name_list  : a list of all names of runs. ex: ['run1', 'run2']
    :param result_list: a list of all NK of runs
    :param df_energy  : a dataframe of the effective energy
    :return           : return a dataframe of the summary
    """
    # get the first dataframe in order to merge with others
    df_result = result_list[0].df_NK

    # merge all results' dataframes into one dataframe
    for i in range(1, len(result_list)):
        df_result = pd.merge(df_result, result_list[i].df_NK, left_index=True, right_index=True, how='outer')

    # give the column name and average the all rows
    df_result.columns = name_list
    df_result['Average'] = round(df_result.mean(axis=1), 2)

    # all results' values divided by the average value
    for name in name_list:
        df_result[name+'/Average'] = round(df_result[name] / df_result['Average'], 3).map('{:,.3f}'.format)
        df_result[name] = df_result[name].map('{:,.2f}'.format)

        # let the format be consisted in the GUI
        df_result['Average'] = df_result['Average'].map('{:,.2f}'.format)

        # deal with effective energy
        df_energy = result_list[0].X
        df_energy = df_energy.applymap('{:,.2f}'.format)

        # merge the effective energy with summary
        df_summary = pd.merge(df_energy, df_result, left_index=True, right_index=True, how='outer')

        return df_summary


def pdf_table(df_summary, df_otherConstant):
    """
    Merge all the constants and NK together. Besides, the data will be placed by voltage and order by effective energy
    :param df_summary: Dataframe - the summary of the selected runs
    :param df_otherConstant: Dataframe - the other constants of the beam quality. Since all run will have same beams,
                             only one df_otherConstant needs to be passed
    :return: Dataframe - will return a dataframe which consist all the constants and NK
    """
    # find how many beams have measure two times
    duplicate_num = len([beam for beam in df_summary.index if '*' in beam])

    df_merge = pd.merge(df_otherConstant, df_summary['E_eff'].to_frame('Nominal effective energy [1]'), left_index=True,
                        right_index=True, how='outer')

    df_merge = pd.merge(df_merge, df_summary['Average'].to_frame('NK [2]'), left_index=True, right_index=True,
                        how='outer')

    # get the voltage for every beam and separate it into first measurement and second measurement
    df_merge['Tube voltage'] = [re.findall(r'\d+', beam)[0] for beam in df_merge.index]
    df_merge['Tube voltage'] = pd.to_numeric(df_merge['Tube voltage'])
    df_merge['Nominal effective energy [1]'] = pd.to_numeric(df_merge['Nominal effective energy [1]'])
    df_first = df_merge[:-duplicate_num]
    df_second = df_merge[-duplicate_num:]

    # sort the Tube voltage for the first measurement in order to put the beams together which have the same voltage
    df_first.sort_values(by='Tube voltage', inplace=True)

    # sort the energy for the first measurement in order to put the beams together which have the same voltage
    df_first_sort = None
    for voltage in df_first['Tube voltage'].unique():
        df_temp = df_first[df_first['Tube voltage'] == voltage]  # extract one voltage
        df_temp.sort_values(by='Nominal effective energy [1]', inplace=True)  # sort by energy
        df_first_sort = pd.concat([df_first_sort, df_temp], axis=0)  # concate with other voltage

    # sort the Tube voltage for the second measurement in order to put the beams together which have the same voltage
    df_second.sort_values(by='Tube voltage', inplace=True)
    df_merge = pd.concat([df_first_sort, df_second], axis=0)

    df_merge.index.name = 'Beam code'
    df_merge = df_merge.iloc[:, [7, 0, 1, 2, 3, 5, 4, 6]]

    # hard code U % value
    df_merge['U %'] = 1.4

    return df_merge.apply(pd.to_numeric).fillna('')

def extractionHeader(client_path: str, lab_path: str):
    """
    This function is used to extract the run info data from the file.
    """
    # check run num in file name (Disabled)

    # client_file_name = client_path.split('//')[-1]
    # lab_file_name = lab_path.split('//')[-1]
    # searchObj = re.search( r'Run[0-9]*', client_file_name, re.I)
    # run = searchObj.group()
    # if not re.search( run, lab_file_name, re.I):
    #     raise HeaderError("Not the same run")
    
    client_data = Header_data()
    lab_data = Header_data()
    
    # read data from header
    with open(client_path, newline='', encoding="ISO-8859-1") as f:
        for line in f:
            if 'DATA' in line:
                break
            elif 'CAL Number' in line:
                client_data.CAL_num = line.split(',')[2].strip()
            elif 'Client name' in line:
                client_data.Client_name = line.split(',')[2].strip()
            elif 'Address 1' in line:
                client_data.address_1 = line.split(',')[2].strip()
            elif 'Address 2' in line:
                client_data.address_2 = line.split(',')[2].strip()
            elif 'Operator' in line:
                client_data.operator = line.split(',')[2].strip()
            elif 'Chamber' in line:
                client_data.serial = line.split(',')[2].strip()[-4:]
                client_data.model = line.split(',')[2].strip()[:-4]
    
    with open(lab_path, newline='', encoding="ISO-8859-1") as f:
        for line in f:
            if 'DATA' in line:
                break
            elif 'CAL Number' in line:
                lab_data.CAL_num = line.split(',')[2].strip()
            elif 'Client name' in line:
                lab_data.Client_name = line.split(',')[2].strip()
            elif 'Address 1' in line:
                lab_data.address_1 = line.split(',')[2].strip()
            elif 'Address 2' in line:
                lab_data.address_2 = line.split(',')[2].strip()
            elif 'Operator' in line:
                lab_data.operator = line.split(',')[2].strip()
            elif 'Chamber' in line:
                lab_data.model = line.split(',')[2].strip()
    
    # data integrity check
    if client_data.model + client_data.serial == "MEFAC":
        raise HeaderError("Client file is a MEFAC run, please check!")
    elif lab_data.model != "MEFAC":
        raise HeaderError("Lab file is not MEFAC run, please check!")
    elif client_data.CAL_num == "":
        raise HeaderError("Client file does not contains CAL num, please check!")
    elif lab_data.CAL_num == "":
        raise HeaderError("Lab file does not contains CAL num, please check!")
    elif client_data.serial == "" or client_data.model == "":
        raise HeaderError("Client file does not contains model/serial, please check!")
    elif not re.match(r"\d{4}", client_data.serial):
        raise HeaderError("Invalid chamber in client file, please check!")
    elif lab_data.CAL_num != client_data.CAL_num:
        raise HeaderError("CAL num from Client file and Lab file not the same, please check!")
    
    return client_data