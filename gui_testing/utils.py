"""
The class is a supplementary tool to the PYAutoGUI to automate the GUI testing.
The purpose is to move the mouse to the UI element location based on its text.
PyAutoGUI currently can be used only on the main screen, where the start point
is set to be the top-left corner as (0,0).

Note that the application window might scale to different size

PyAutoGUI: https://pyautogui.readthedocs.io/en/latest/
"""

import pandas as pd
import ast
import easyocr
import pyautogui as pq
import os

# the parameters could be various depends on the device
# adjust the value to fit the screen

# (left, top), start point
APP_START_X = 471
APP_START_Y = 108

ANA_START_X = 296
ANA_START_Y = 43

SAVE_START_X = 306
SAVE_START_Y = 85

# use the current directory, where the script exists
CWD = os.path.dirname(os.path.realpath(__file__))

class UI:
  """
  The UI class parse the CSV file to turn the data into a dictionary.
  The data is generated using the libaray easy_ocr to scrape the texts
  on the image. Please see the README.md in the scrape folder.
  """
  def __init__(self, data, index):
    """
    The class takes the CSV file and the desired column as index
    """
    self.df = pd.DataFrame(pd.read_csv(data, index_col=index))
    # change the string to a list
    self.df['pos'] = self.df['pos'].apply(lambda s: list(ast.literal_eval((s))))
    self.dict = self.df.to_dict()
    self.__APP_START_X = APP_START_X
    self.__APP_START_Y = APP_START_Y
    self.__ANA_START_X = ANA_START_X
    self.__ANA_START_Y = ANA_START_Y
    self.__SAVE_START_X = SAVE_START_X
    self.__SAVE_START_Y = SAVE_START_Y
  
  def get_pos(self, button_name, window):
    """
    The function generates the start point of the UI element.
    The button_name is in the data folder.
    :param: str button_name: The UI element text
    :param: str window: app, analysis, save
    """
    # the position is based on the screenshots
    # the bounding box of the easyocr: (tl, tr, br, bl)
    ui_start_x = self.dict['pos'][button_name][0][0]
    ui_start_y = self.dict['pos'][button_name][0][1]
    if window == "app":
      # adjust the position to the actual position on the screen
      ui_start_x_real = ui_start_x + self.__APP_START_X
      ui_start_y_real = ui_start_y + self.__APP_START_Y
      return ui_start_x_real,  ui_start_y_real
    elif window == "analysis":
      ui_start_x_real = ui_start_x + self.__ANA_START_X
      ui_start_y_real = ui_start_y + self.__ANA_START_Y
      return ui_start_x_real,  ui_start_y_real
    elif window == "save":
      ui_start_x_real = ui_start_x + self.__SAVE_START_X
      ui_start_y_real = ui_start_y + self.__SAVE_START_Y
      return ui_start_x_real,  ui_start_y_real
  
def get_text(image):
  """
  Get the image text from the temp_screenshots folder and save the CSV information in the temp_data.
  """
  reader = easyocr.Reader(['en']) # be able to use CUDA, much faster than CPU
  allow_list = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 '
  result = reader.readtext(f'../temp_screenshots/{image}.png', detail=1, allowlist = allow_list)
    
  df = pd.DataFrame(result)
  df.columns = ['pos', 'string', 'confidence']
  df.to_csv(f'../temp_data/{image}.csv', index=False)


def get_string_list(ui_obj):
  """
  Return the screenshot text into a list.
  """
  return pd.Series(ui_obj.df.index.values).tolist()

def screenshot_app_window(name, start_x=APP_START_X, start_y=APP_START_Y, end_x=1446, end_y=888):
  """
  Default to screenshot the homepage.
  """
  pq.screenshot(
    os.path.join(CWD,'temp_screenshots', f'{name}.png'),
    region=(start_x, start_y, (end_x-start_x), (end_y-start_y))
  )