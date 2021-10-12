"""
The UI element names are stored as CSV files in the temp_data folder.
Please check the CSV for the specific UI element name on different UI pages.
The testing logic is to screenshot the application and get the text, and see if 
the specific text would appear after the certain action.

In the US07, the goal is to generate the PDF with clicks.
1. Testing the homepage routes to the client info page.
2. Testing the client info page to the equipment info page.
3. Testing the equipment info page to the analysis page.
4. Testing the "Generate PDF" button to the saving window.
5. Testing the required output PDF name format.
"""

import pyautogui as pq
from utils import UI
import utils
import pandas as pd
import unittest
import os
import shutil
from time import sleep

# W0311: bad indentation; E1101:no-member; C0325: Unnecessary parens
# pylint: disable=W0311, E1101, C0325

# use the current directory, where the script exists
CWD = os.path.dirname(os.path.realpath(__file__))

class TestUserStory7(unittest.TestCase):
  """The user story 7 related system testing

  Args:
      unittest ([type]): [The default testing module from Python]
  """
  @classmethod
  def setUpClass(self):
    """ Create or replace previous folder """
    try:
      folder = os.getcwd() + "\\US07 Fail"
      shutil.rmtree(folder)
    except FileNotFoundError:
      print("[There's no such directory]")

    try:
      folder = os.getcwd() + "\\US07 Success"
      shutil.rmtree(folder)
    except FileNotFoundError:
      print("[There's no such directory]")

    try:
      folder = os.getcwd() + "\\US07"
      shutil.rmtree(folder)
    except FileNotFoundError:
      print("[There's no such directory]")

    try:
      self.cwd = os.getcwd() # for printing the current directory
      # print(self.cwd)
      os.mkdir("US07")
      os.chdir("US07") # cd to the directory for saving screenshots
      self.storage = '%s/' % os.getcwd() # escape the cwd string
    except:
      print("[Something is wrong when creating the directory]")

  @classmethod
  def tearDownClass(self):
    """ End the test, determine if tests succeed or fail
    Then, rename the folder.
    """
    file_list = os.listdir()
    # print(file_list)
    # iterate through the filename string, if there's a keyword "fail", rename the folder
    for filename in file_list:
      if "fail" in filename:
        # print("Some tests failed")
        os.chdir("..")
        os.rename("US07", "US07 Fail")
        return
    os.chdir("..")
    os.rename("US07", "US07 Success")

  
  def test_a_gen_pdf(self):
    # homepage
    utils.screenshot_app_window('homepage')
    utils.get_text('homepage')

    homepage_ui = UI('../temp_data/homepage.csv', 'string')
    cli_A_x, cli_A_y = homepage_ui.get_pos("ClientA", "app")
    select_x, select_y = homepage_ui.get_pos("Select Client", "app")

    pq.moveTo(cli_A_x+1, cli_A_y+1,1)
    pq.click()

    pq.moveTo(select_x+1, select_y+1, 1)
    pq.click() # route to the next page

    # route to client_info page
    # assert if the string 5122 on the screen
    try:
      utils.screenshot_app_window('client_info')
      utils.get_text('client_info')

      client_ui = UI('../temp_data/client_info.csv', 'string')
      lst = utils.get_string_list(client_ui)

      self.assertTrue("5122" in lst)
      pq.screenshot(
        os.path.join(CWD,'US07', 'to the client_page success .png'),
        region=(utils.APP_START_X, utils.APP_START_Y, (1446-utils.APP_START_X), (888-utils.APP_START_Y))
      )
    except:
      print("[Assertion error, the page doesn't route]")
      pq.screenshot(
        os.path.join(CWD,'US07', 'to the client_page fail .png'),
        region=(utils.APP_START_X, utils.APP_START_Y, (1446-utils.APP_START_X), (888-utils.APP_START_Y))
      )
      raise
    
    # client_info page
    serial_x, serial_y = client_ui.get_pos("5122", "app")
    choose_x, choose_y = client_ui.get_pos("Choose Equipment", "app")
    pq.moveTo(serial_x+1, serial_y+1, 1)
    pq.click()

    pq.moveTo(choose_x+1, choose_y+1, 1)
    pq.click() # route the next page

    # route to the equipment info
    # assert if the string Duncan Butler on the screen 
    try:
      utils.screenshot_app_window('equipment_info')
      utils.get_text('equipment_info')

      equipment_ui = UI('../temp_data/equipment_info.csv', 'string')
      lst = utils.get_string_list(equipment_ui)
      
      self.assertTrue("Duncan Butler" in lst)
      pq.screenshot(
        os.path.join(CWD,'US07', 'to the equipment_page success .png'),
        region=(utils.APP_START_X, utils.APP_START_Y, (1446-utils.APP_START_X), (888-utils.APP_START_Y))
      )
    except:
      print("[Assertion error, the page doesn't route]")
      pq.screenshot(
        os.path.join(CWD,'US07', 'to the equipment_page fail .png'),
        region=(utils.APP_START_X, utils.APP_START_Y, (1446-utils.APP_START_X), (888-utils.APP_START_Y))
      )
      raise
    # equipment_info page
    operator_x, operator_y = equipment_ui.get_pos("Duncan Butler", "app")
    analyse_x, analyse_y = equipment_ui.get_pos("Analyse Run", "app")

    pq.moveTo(operator_x+1, operator_y+1, 1)
    pq.click()

    pq.moveTo(analyse_x+1, analyse_y+1, 1)
    pq.click()

    sleep(2)

    # route to the analysis page
    # assert the string Generate PDF on the screen
    try:
      utils.screenshot_app_window('analysis', utils.ANA_START_X, utils.ANA_START_Y, 1820, 948)
      utils.get_text('analysis')

      analysis_ui = UI('../temp_data/analysis.csv', 'string')
      lst = utils.get_string_list(analysis_ui)
      self.assertTrue("Generate PDF" in lst)
      
      pq.screenshot(
        os.path.join(CWD,'US07', 'to the analysis_page success .png'),
        region=(utils.ANA_START_X, utils.ANA_START_Y, (1820-utils.ANA_START_X), (948-utils.ANA_START_Y))
      )
    except:
      print("[Assertion error, the page doesn't route]")
      pq.screenshot(
        os.path.join(CWD,'US07', 'to the analysis_page fail .png'),
        region=(utils.ANA_START_X, utils.ANA_START_Y, (1820-utils.ANA_START_X), (948-utils.ANA_START_Y))
      )
      raise
    # analysis page
    gen_pdf_x, gen_pdf_y = analysis_ui.get_pos("Generate PDF", "analysis")

    pq.moveTo(gen_pdf_x+1,gen_pdf_y+1, 1)
    pq.click()

    sleep(2)
    # route to the saving page
    # assert the string Save on the screen
    try:
      utils.screenshot_app_window('save', utils.SAVE_START_X, utils.SAVE_START_Y, 1250, 675)
      utils.get_text('save')

      save_ui = UI('../temp_data/save.csv', 'string')
      lst = utils.get_string_list(save_ui)

      self.assertTrue("Save" in lst)
      pq.screenshot(
        os.path.join(CWD,'US07', 'to the saving window success .png'),
        region=(utils.ANA_START_X, utils.ANA_START_Y, (1820-utils.ANA_START_X), (948-utils.ANA_START_Y))
      )
    except:
      print("[Assertion error, the page doesn't route]")
      pq.screenshot(
        os.path.join(CWD,'US07', 'to the saving window fail .png'),
        region=(utils.ANA_START_X, utils.ANA_START_Y, (1820-utils.ANA_START_X), (948-utils.ANA_START_Y))
      )
      raise

    # save page
    save_x, save_y = save_ui.get_pos("Save", "save")

    pq.moveTo(save_x+1, save_y+1, 1)
    pq.click()