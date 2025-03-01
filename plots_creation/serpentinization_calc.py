import time
import alive_progress
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.interpolate import interp1d
from scipy.signal import find_peaks
import os

print(' ** Read the information correctly to run this code and Follow the instructions ** '+ '\n')
print('ℹ️ You need continum removed file for serpentine (SEPERATE FILE).')
print('ℹ️ You need continum removed file for Olivine (SEPERATE FILE).')
print('ℹ️ You need continum removed file for ALL MINERALS' + '\n')

print(' ** Be specific with the file names, they should be saved with the same file name inside the folder ** '+ '\n')
print('ℹ️ DEFAULT NAMES OF FILES:')
print('Serpentine file name (contium removed) --> continuum removed srp,spec 26.txt')
print('Olivine file name (contium removed) --> countinuum removed oli, spec 25.txt')
print('EXCEL FILE FOR ALL MINERALS CONTINUM REMOVED --> continum_removed.xlsx' + '\n')
print('\n')

def find_trough_after_wavelength(wavelengths, reflectance, target_wavelength):
    # Find all troughs
    troughs, _ = find_peaks(-reflectance)

    # Find the index of the first wavelength greater than the target_wavelength
    valid_troughs = []
    for i in troughs:
        if (target_wavelength - 0.007) < wavelengths[i] < (target_wavelength + 0.02):
            valid_troughs.append(i)

        else:
            if wavelengths[i] > target_wavelength:
                valid_troughs.append(i)

    if not valid_troughs:
        return None, None

    # Find the closest trough after the target wavelength
    closest_trough_idx = valid_troughs[0]

    return wavelengths[closest_trough_idx], reflectance[closest_trough_idx]


def find_absorption_depth(wavelengths, continuum_removed_reflectance, absorption_feature):
    global continuum_points_wavelengths

    peaks, _ = find_peaks(continuum_removed_reflectance, height=0.9)

    # Find Troughs (invert the signal to find minima)
    troughs, _ = find_peaks(-continuum_removed_reflectance)

    peak_wavelengths = wavelengths[peaks]
    peak_reflectance = continuum_removed_reflectance[peaks]

    trough_wavelength, trough_reflectance = find_trough_after_wavelength(wavelengths, continuum_removed_reflectance,
                                                                         absorption_feature)

    continuum_points_wavelengths = np.array([absorption_feature - 0.5, absorption_feature + 1.2])

    closest_value_start = wavelengths.iloc[(wavelengths - continuum_points_wavelengths[0]).abs().idxmin()]
    closest_value_end = wavelengths.iloc[(wavelengths - continuum_points_wavelengths[1]).abs().idxmin()]

    continuum_points_reflectance = continuum_removed_reflectance[
        (wavelengths == closest_value_start) | (wavelengths == closest_value_end)]

    #spline = UnivariateSpline(peak_wavelengths, peak_reflectance)

    # Interpolate the continuum
    continuum_interp = interp1d(continuum_points_wavelengths, continuum_points_reflectance,
                                kind='linear',
                                fill_value='extrapolate')

    #continuum = continuum_interp(wavelengths)
    #continuum_spline = spline(wavelengths)

    #print(f"Trough Wavelength: {trough_wavelength}, Trough Reflectance: {trough_reflectance}")
    absorption_depth = 1 - continuum_removed_reflectance

    absorption_feature_index = np.where(wavelengths == trough_wavelength)[0]
    # r1 = absorption_depth[absorption_feature_index]
    # r2 = 1 - continuum[absorption_feature_index]

    #r_res = r1 - r2
    # print('r1', r1)
    # print('r2', r2)
    # print('r_res', r_res)
    # print('absorption_depth[absorption_feature_index]', absorption_depth[absorption_feature_index])
    return absorption_depth[
        absorption_feature_index], trough_wavelength, trough_reflectance


absorption_feature_values = [1.0, 1.4, 1.9, 2.3]

text_file_path_1 = input(' Please provide path address where this  [example: continuum removed srp,spec 26.txt] is stored for serpentine: ')

# text_file_path_1 = Path(
#     '/home/abhinav/lenovo_backup/Lenovo/E/asd_files')
txtfile_1 = 'continuum removed srp,spec 26.txt'  # Olivine#Serpantinite 1

if not os.path.exists(Path(text_file_path_1) / txtfile_1):
    raise ValueError(f'❌ File is not found, check the path again: {Path(text_file_path_1) / txtfile_1}')

print(f' ** Preparing the Dataframe {txtfile_1} ** ')

with open(Path(text_file_path_1) / txtfile_1, 'r') as file:
    # Read the entire contents of the file
    columns = [line.strip().split(':')[1].strip() for line in file.readlines()[:3]]

df_1 = pd.read_csv(Path(text_file_path_1)  / txtfile_1, sep=r'\s+', skiprows=4, header=None,
                   names=columns)
df_temp_1 = df_1.copy()

text_file_path_2 = input(' Please provide path address where this  [example: countinuum removed oli, spec 25.txt] is stored for olivine: ')

# text_file_path_2 = Path(
#     '/home/abhinav/lenovo_backup/Lenovo/E/asd_files')
txtfile_2 = 'countinuum removed oli, spec 25.txt'

if not os.path.exists(Path(text_file_path_2) / txtfile_2):
    raise ValueError(f'❌ File is not found, check the path again: {Path(text_file_path_2) / txtfile_2}')

print(f'Preparing the Dataframe {text_file_path_2}')
with open(Path(text_file_path_2) / txtfile_2, 'r') as file:
    columns = [line.strip().split(':')[1].strip() for line in file.readlines()[:3]]

df_2 = pd.read_csv(Path(text_file_path_2)  / txtfile_2, sep=r'\s+', skiprows=4, header=None,
                   names=columns)
df_temp_2 = df_2.copy()
df_temp_1[df_temp_1.columns[0]] = df_temp_1[df_temp_1.columns[0]] / 1000
df_temp_2[df_temp_2.columns[0]] = df_temp_2[df_temp_2.columns[0]] / 1000

file_path_for_txt = input('Enter the path where you want to save the file: ')
filename = input('Enter the File Name (example: Serpentinization): ')

with open(Path(file_path_for_txt) / f'{filename}.txt', 'a') as file:
    file.write('--' * 100 + '\n')
    file.write('        **************** Calculated using peaks and troughs method ****************         ' + '\n')
    file.write('--' * 100 + '\n')

text_file_path_3 = input(' Please provide path address where this continum removed file which contains all minerals in one file: ' )
excel_file = 'continum_removed.xlsx'

if not os.path.exists(Path(text_file_path_3) / excel_file):
    raise ValueError(f'❌ File is not found, check the path again: {Path(text_file_path_2) / txtfile_2}')

with alive_progress.alive_bar(total = len(range(1,8)), force_tty=True, bar='blocks', spinner='waves') as bar:
    for j in range(1, 8):
        if j == 1 or j == 2:
            excel_ = pd.read_excel(Path(text_file_path_3) / excel_file, header=None,
                                   sheet_name=f'loc {j}')
        else:
            excel_ = pd.read_excel(Path(text_file_path_3) / excel_file, header=None,
                                   sheet_name=f'Sheet{j}')

        with open(Path(file_path_for_txt) / f'{filename}.txt', 'a') as file:
            file.write('--' * 50 + '\n')
            file.write(f'Sheet {j}' + '\n')

        for i in range(1, len(excel_.columns)):
            dictonery = {}
            dictonery_trough_wavelength = {}
            dictonery_trough_reflectance = {}

            for feature_value in absorption_feature_values:
                ad, trough_wavelength, trough_reflectance = find_absorption_depth(excel_[excel_.columns[0]],
                                                                                  excel_[excel_.columns[i]],
                                                                                  absorption_feature=feature_value)
                dictonery[f'{i}_{feature_value}'] = ad.to_numpy()[0]
                dictonery_trough_wavelength[f'{i}_{feature_value}'] = trough_wavelength
                dictonery_trough_reflectance[f'{i}_{feature_value}'] = trough_reflectance

            average_value = (dictonery[f'{i}_{absorption_feature_values[1]}']
                             + dictonery[f'{i}_{absorption_feature_values[2]}']
                             + dictonery[f'{i}_{absorption_feature_values[3]}']) / 3

            ad_1_0 = dictonery[f'{i}_{absorption_feature_values[0]}']
            ad_1_4 = dictonery[f'{i}_{absorption_feature_values[1]}']
            ad_1_9 = dictonery[f'{i}_{absorption_feature_values[2]}']
            ad_2_3 = dictonery[f'{i}_{absorption_feature_values[3]}']

            tw_1_0 = dictonery_trough_wavelength[f'{i}_{absorption_feature_values[0]}']
            tw_1_4 = dictonery_trough_wavelength[f'{i}_{absorption_feature_values[1]}']
            tw_1_9 = dictonery_trough_wavelength[f'{i}_{absorption_feature_values[2]}']
            tw_2_3 = dictonery_trough_wavelength[f'{i}_{absorption_feature_values[3]}']

            tref_1_0 = dictonery_trough_reflectance[f'{i}_{absorption_feature_values[0]}']
            tref_1_4 = dictonery_trough_reflectance[f'{i}_{absorption_feature_values[1]}']
            tref_1_9 = dictonery_trough_reflectance[f'{i}_{absorption_feature_values[2]}']
            tref_1_3 = dictonery_trough_reflectance[f'{i}_{absorption_feature_values[3]}']

            calc = round(ad_1_0 * 100, 2) + round(ad_1_4 * 100, 2) + round(ad_1_9 * 100, 2) + round(ad_2_3 * 100, 2)

            if calc > 100:
                excess_ = calc - 100
                actual_1_4 = (round(ad_1_4 * 100, 2) / (round(ad_1_4 * 100, 2) + round(ad_1_9 * 100, 2))) * 100
                actual_1_9 = (round(ad_1_9 * 100, 2) / (round(ad_1_4 * 100, 2) + round(ad_1_9 * 100, 2))) * 100

            else:
                actual_1_4 = round(ad_1_4 * 100, 2)
                actual_1_9 = round(ad_1_9 * 100, 2)

            three_comb = round(ad_1_4 * 100, 2) + round(ad_1_9 * 100, 2) + round(ad_2_3 * 100, 2)
            Expected_ = 100 - round(ad_1_0 * 100, 2)

            exceeded = three_comb - Expected_
            sum_1_4_1_9 = round(ad_1_4 * 100, 2) + round(ad_1_9 * 100, 2)
            new_a_1_4 = round(ad_1_4 * 100, 2) - ((round(ad_1_4 * 100, 2) / sum_1_4_1_9) * exceeded)
            new_a_1_9 = round(ad_1_9 * 100, 2) - ((round(ad_1_9 * 100, 2) / sum_1_4_1_9) * exceeded)

            calc_check = round(ad_1_4 * 100, 2) + round(ad_1_9 * 100, 2) + round(ad_2_3 * 100, 2)

            with open(Path(file_path_for_txt) / f'{filename}.txt', 'a') as file:
                file.write('--' * 50 + '\n')
                file.write(f' Sample No. {i}' + '\n')
                file.write(
                    f'Absorption depth value at 1.0 at wavelength {tw_1_0} and continued removed refelectance {tref_1_0}: {round(ad_1_0 * 100, 2)}' + '\n')
                file.write(
                    f'Absorption depth value at 1.4 at wavelength {tw_1_4} and continued removed refelectance {tref_1_4}: {round(ad_1_4 * 100, 2)}' + '\n')
                file.write(
                    f'Absorption depth value at 1.4 at wavelength {tw_1_4} and continued removed refelectance {tref_1_4}_new: {round(new_a_1_4, 2)}' + '\n')

                # file.write(f'Absorption depth *ACTUAL* value at 1.4 at wavelength {tw_1_4} and continued removed refelectance {tref_1_4}: {actual_1_4}' + '\n')
                # file.write(f'Absorption depth *ACTUAL* value at 1.9 at wavelength {tw_1_9} and continued removed refelectance {tref_1_9}: {actual_1_9}' + '\n')

                file.write(
                    f'Absorption depth value at 1.9 at wavelength {tw_1_9} and continued removed refelectance {tref_1_9}: {round(ad_1_9 * 100, 2)}' + '\n')
                file.write(
                    f'Absorption depth value at 1.9 at wavelength {tw_1_9} and continued removed refelectance {tref_1_9}_new: {round(new_a_1_9, 2)}' + '\n')

                file.write(
                    f'Absorption depth value at 2.3 at wavelength {tw_2_3} and continued removed refelectance {tref_1_3}: {round(ad_2_3 * 100, 2)}' + '\n')
                # file.write(
                #    f'Average value after combining absorption depths from 1.0, 1.4 and 2.3: {round(average_value * 100, 2)}' + '\n')
                file.write(
                    f'Total Sum:  {calc}' + '\n')
                file.write(
                    f'Total Sum 1_4,1_9,2_3:  {calc_check}' + '\n')

                file.write(
                    f'new 1_4,1_9:  {new_a_1_4}__{new_a_1_9}' + '\n')

                file.write(
                    f'Degree of Serpentinization : (100-(olivine_1.0))= {100 - round(ad_1_0 * 100, 2)}' + '\n')
                file.write('--' * 50 + '\n')

        time.sleep(0.1)
        bar()
exit(' ** SUCCESSFUL: PROCESS COMPLETED ** ')
