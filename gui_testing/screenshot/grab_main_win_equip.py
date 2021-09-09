"""
  The screen resolution is (1920,1080). The script aims for cropping the images
  from the application main window, run page.

  The reason using the pyautogui instead of creenshot using Windows 10 bulit-in
  snip & sketch tools is that the image might not be recognized by opencv.
"""

import os
import pyautogui as pg

# W0311: bad indentation; E1101:no-member; C0325: Unnecessary parens; C0103: upper case naming
# pylint: disable=W0311, E1101, C0325, C0103

try:
  os.mkdir('main_win_equip')
except OSError:
  print("[The directory already existed]")

# for buttons, which are aligned horizontally
start_y = 454
end_y = 506

# button analyze
btn_analyze_x = 536
btn_analyze_y = start_y
pg.screenshot(
  'main_win_equip/equip_analyze.png',
  region=(
    btn_analyze_x,
    btn_analyze_y,
    (747 - btn_analyze_x),
    (end_y - btn_analyze_y)
  )
)

# button add new run
btn_add_run_x = 747
btn_add_run_y = start_y
pg.screenshot(
  'main_win_equip/equip_add_new_run.png',
  region=(
    btn_add_run_x,
    btn_add_run_y,
    (958 - btn_add_run_x),
    (end_y - btn_add_run_y)
  )
)

# button delete run
btn_del_run_x = 958
btn_del_run_y = start_y
pg.screenshot(
  'main_win_equip/equip_del_run.png',
  region=(
    btn_del_run_x,
    btn_del_run_y,
    (1169 - btn_del_run_x),
    (end_y - btn_del_run_y)
  )
)

# button return
btn_return_x = 1169
btn_return_y = start_y
pg.screenshot(
  'main_win_equip/equip_return.png',
  region=(
    btn_return_x,
    btn_return_y,
    (1380 - btn_return_x),
    (end_y - btn_return_y)
  )
)
