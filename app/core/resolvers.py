"""
This file contains the code to do the calculation.

Each resolver receives a model and outputs the calculated result, which can
be a model or just a matrix.
"""
import pandas as pd
import warnings
import numpy as np

warnings.filterwarnings('ignore')

# the object to store data
class Processed_data():
    def __init__(self):
        self.df_before_mean = None
        self.df_mean = None
        self.df_after_mean = None


# Using object to save result in order to avoid too much returned elements
class result_data():
    def __init__(self):
        self.df_NK = None
        self.df_leakage = None
        self.highlight = []
        self.X = []
        self.Y = []


def calculator(client, lab):
    # extract data
    client_data, duplicate_num = extraction(client)
    lab_data, _ = extraction(lab)

    # order the lab beams to make sure that the further calculation will not have issue
    cats = client_data.df_mean.index.tolist()
    lab_data.df_mean.reset_index(inplace=True)
    lab_data.df_mean['Filter'] = pd.CategoricalIndex(lab_data.df_mean['Filter'], ordered=True, categories=cats)
    lab_data.df_mean = lab_data.df_mean.sort_values('Filter')
    lab_data.df_mean = lab_data.df_mean.set_index('Filter')

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
    constant = '.\\app\\core\\constant2.xlsx'
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
    df_beams = df_beams.sort_values('Filter')

    # get the filter which measure two times from KK
    df_beams_dupkicate = df_beams[df_beams.Filter.isin(client_data.df_mean.index[:duplicate_num])]
    cats = client_data.df_mean.index[:duplicate_num]
    df_beams_dupkicate['Filter'] = pd.CategoricalIndex(df_beams_dupkicate['Filter'], ordered=True, categories=cats)
    df_beams_dupkicate['Filter'] = [Filter + '*' for Filter in df_beams_dupkicate.Filter.tolist()]
    df_beams_dupkicate = df_beams_dupkicate.sort_values('Filter')

    # concat together so that KK will have the same order as client_data.df_mean
    df_KK = pd.concat([df_beams, df_beams_dupkicate], axis=0).set_index('Filter')['Product'].to_frame('NK')

    # Calculating NK
    NK = R2 * WE * df_KK * ((273.15 + TS2) / (273.15 + TM2)) * (0.995766667 + 0.000045 * H2) / (
                Ma * R1 * (273.15 + TA1) / (273.15 + TM1))
    NK = round(NK / 1000000, 2)
    NK.columns = ['NK']

    # leakage
    df_leakage = pd.DataFrame({"Current PA Before": [BgdMC1_Before, BgdIC1_Before, BgdMC2_Before, BgdIC2_Before],
                                  "Current PA After": [client_data.df_after_mean['Current1(pA)'].values[0],
                                                       client_data.df_after_mean['Current2(pA)'].values[0],
                                                       lab_data.df_after_mean['Current1(pA)'].values[0],
                                                       lab_data.df_after_mean['Current2(pA)'].values[0]]},
                                 index=["Monitor 1", "Chamber (client)", "Monitor 1", "Standard (MEFAC)"])

    # extract the effective energy for plotting the graph
    df_energy = pd.concat([df_beams, df_beams_dupkicate], axis=0).set_index('Filter')['E_eff'].to_frame()

    # create an object to save result
    result = result_data()

    # saving NK
    result.df_NK = NK

    # saving leakage
    result.df_leakage = df_leakage

    # get the coordinate which the cell need to be highlighted
    result.highlight = [(x, y) for x, y in zip(*np.where(abs(result.df_leakage.values) > 0.1))]

    # saving the graph required data
    result.X = df_energy['E_eff'].tolist()
    result.Y = NK['NK'].tolist()

    return result


def extraction(path):
    df = pd.read_csv(path, encoding='mac_roman')

    title_index = 0
    Backgrounds_num = 0
    Measurements_num = 0

    for i in range(len(df)):
        # get where the data start
        if 'DATA' in df.iloc[i].tolist()[0]:
            title_index = i + 1
            break

        # get the Background number
        elif 'Backgrounds' in df.iloc[i].tolist()[0]:
            Backgrounds_num = int(df.iloc[i].tolist()[2])

        # get the measurement number
        elif 'Measurements' in df.iloc[i].tolist()[0]:
            Measurements_num = int(df.iloc[i].tolist()[2])

    # store the title
    title = df.iloc[title_index].values.tolist()

    # extract all data
    df_total = df[title_index + 1:]
    df_total.columns = title
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
