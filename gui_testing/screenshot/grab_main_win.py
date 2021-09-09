"""
  The screen resolution is (1920,1080). The script aims for cropping the images
  from the application main window.
  
  The reason using the pyautogui instead of creenshot using Windows 10 bulit-in
  snip & sketch tools is that the image might not be recognized by opencv.
"""

import os
import pyautogui as pg

# W0311: bad indentation; E1101:no-member; C0325: Unnecessary parens; C0103: upper case naming
# pylint: disable=W0311, E1101, C0325, C0103

try:
  os.mkdir('main_win')
except OSError:
  print("[The directory already existed]")

# button add_new_client
btn_add_new_client_x = 820
btn_add_new_client_y = 368
pg.screenshot(
  'main_win/add_new_client.png',
  region=(
    btn_add_new_client_x,
    btn_add_new_client_y,
    (1098-btn_add_new_client_x),
    (416-btn_add_new_client_y)
  )
)

# button choose client
btn_choose_client_x = 540
btn_choose_client_y = 368
pg.screenshot(
  'main_win/choose_client.png',
  region=(
    btn_choose_client_x,
    btn_choose_client_y,
    (817-btn_choose_client_x),
    (416-btn_choose_client_y)
  )
)

# button delete client
btn_delete_client_x = 1101
btn_delete_client_y = 368
pg.screenshot(
  'main_win/delete_client.png',
  region=(
    btn_delete_client_x,
    btn_delete_client_y,
    (1383-btn_delete_client_x),
    (416-btn_delete_client_y)
  )
)

# fake data for checking function
field_cal_number_x = 542
field_cal_number_y = 465
pg.screenshot(
  'main_win/cal_CAL0004.png',
  region=(
    field_cal_number_x,
    field_cal_number_y,
    (957 - field_cal_number_x),
    (499 - field_cal_number_y)
  )
)
