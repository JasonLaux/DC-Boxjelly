"""
  The screen resolution is (1920,1080). The script aims for cropping the images
  from the application main window, equipment information page.

  The reason using the pyautogui instead of creenshot using Windows 10 bulit-in
  snip & sketch tools is that the image might not be recognized by opencv.
"""

import os
import pyautogui as pg

# W0311: bad indentation; E1101:no-member; C0325: Unnecessary parens; C0103: upper case naming
# pylint: disable=W0311, E1101, C0325, C0103

try:
  os.mkdir('main_win_info')
except OSError:
  print("[The directory already existed]")


# cal num
cal_num_x = 922
cal_num_y = 335
pg.screenshot(
  'main_win_info/info_client_cal_num.png',
  region=(
    cal_num_x,
    cal_num_y,
    (1066-cal_num_x),
    (361-cal_num_y)
  )
)

start_x = 692
end_x = 1289

# client name
client_name_x = start_x
client_name_y = 364
pg.screenshot(
  'main_win_info/info_client_name.png',
  region=(
    client_name_x,
    client_name_y,
    (end_x - client_name_x),
    (403 - client_name_y)
  )
)

# client address1
client_address_1_x = start_x
client_address_1_y = 403
pg.screenshot(
  'main_win_info/info_client_address1.png',
  region=(
    client_address_1_x,
    client_address_1_y,
    (end_x - client_address_1_x),
    (439 - client_address_1_y)
  )
)

# client address2
client_address_2_x = start_x
client_address_2_y = 439
pg.screenshot(
  'main_win_info/info_client_address2.png',
  region=(
    client_address_2_x,
    client_address_2_y,
    (end_x - client_address_2_x),
    (474 - client_address_2_y)
  )
)

# button choose equipment
btn_choose_client_x = 536
btn_choose_client_y = 495
pg.screenshot(
  'main_win_info/info_choose_equipment.png',
  region=(
    btn_choose_client_x,
    btn_choose_client_y,
    (748 - btn_choose_client_x),
    (548 - btn_choose_client_y)
  )
)

# button add new equipment
btn_add_new_equip_x = 750
btn_add_new_equip_y = 500
pg.screenshot(
  'main_win_info/info_add_new_equipment.png',
  region=(
    btn_add_new_equip_x,
    btn_add_new_equip_y,
    (958 - btn_add_new_equip_x),
    (543 - btn_add_new_equip_y)
  )
)

# button delete equipment
btn_del_equip_x = 958
btn_del_equip_y = 495
pg.screenshot(
  'main_win_info/info_del_equipment.png',
  region=(
    btn_del_equip_x,
    btn_del_equip_y,
    (1169 - btn_del_equip_x),
    (548 - btn_del_equip_y)
  )
)

# button return to main page
btn_return_x = 1169
btn_return_y = 495
pg.screenshot(
  'main_win_info/info_return.png',
  region=(
    btn_return_x,
    btn_return_y,
    (1382 - btn_return_x),
    (548 - btn_return_y)
  )
)

# button update
btn_update_x = 1292
btn_update_y = 377
pg.screenshot(
  'main_win_info/info_update.png',
  region=(
    btn_update_x,
    btn_update_y,
    (1368 - btn_update_x),
    (426 - btn_update_y)
  )
)

# home tab
btn_home_x = 540
btn_home_y = 180
pg.screenshot(
  'main_win_info/info_home.png',
  region=(
    btn_home_x,
    btn_home_y,
    (943 - btn_home_x),
    (753 - btn_home_y)
  )
)

# make/model
field_make_x = 545
field_make_y = 597
pg.screenshot(
  'main_win_info/info_make.png',
  region=(
    field_make_x,
    field_make_y,
    (817 - field_make_x),
    (624 - field_make_y)
  )
)

# serial num
field_serial_x = 826
field_serial_y = 597
pg.screenshot(
  'main_win_info/info_serial.png',
  region=(
    field_serial_x,
    field_serial_y,
    (1094 - field_serial_x),
    (624 - field_serial_y)
  )
)
