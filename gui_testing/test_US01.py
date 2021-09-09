"""
  The test file need to be run inside the gui_testing directory,
  with application centered on the (1920,1080) resolution main screen.
  The test cases are for the system testing, with the tests visulized.
  The test cases are testing the user story 1, mainly with the functionalities
  regarding:
    1. add, delete, update client information; choose client to add equipments
    2. add, delete equipments; choose equipment to add new run with a pair of CSVs
    3. add, delete new run

"""

import unittest
import os
import shutil
from time import sleep
import pyautogui as pg

# W0311: bad indentation; E1101:no-member; C0325: Unnecessary parens
# pylint: disable=W0311, E1101, C0325

# use the current directory, where the script exists
CWD = os.path.dirname(os.path.realpath(__file__))

class TestUserStory1(unittest.TestCase):
  """The user story 1 related system testing

  Args:
      unittest ([type]): [The default testing module from Python]
  """
  @classmethod
  def setUpClass(self):
    """ Create or replace previous folder """
    try:
      folder = os.getcwd() + "\\US01 Fail"
      shutil.rmtree(folder)
    except FileNotFoundError:
      print("[There's no such directory]")

    try:
      folder = os.getcwd() + "\\US01 Success"
      shutil.rmtree(folder)
    except FileNotFoundError:
      print("[There's no such directory]")

    try:
      folder = os.getcwd() + "\\US01"
      shutil.rmtree(folder)
    except FileNotFoundError:
      print("[There's no such directory]")

    try:
      self.cwd = os.getcwd() # for printing the current directory
      # print(self.cwd)
      os.mkdir("US01")
      os.chdir("US01") # cd to the directory for saving screenshots
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
        os.rename("US01", "US01 Fail")
        return
    os.chdir("..")
    os.rename("US01", "US01 Success")
    # print("All tests passed")

  def test_a_add_new_client(self):
    ''' add a new client '''
    try:
      # The pyautogui doesn't recognize the pop up window -> use the coordination
      btn_add_new_client = pg.locateOnScreen(
        os.path.join(CWD, 'screenshot' ,'main_win' ,'add_new_client.png'),
        grayscale=False, confidence=.9)

      pg.moveTo(btn_add_new_client)
      pg.click()
    except:
      print("[There's no such button matching the picture]")
      raise
    # add a new client
    try:
      pg.moveTo(942, 464, 0.6) # cal number
      pg.click()
      pg.write("CAL00004")

      pg.moveTo(942, 502, 0.6) # client name
      pg.click()
      pg.write("Test client name")

      pg.moveTo(942, 540, 0.6) # address 1
      pg.click()
      pg.write("Test client address1")

      pg.moveTo(942, 577, 0.6) # address 2
      pg.click()
      pg.write("Test client address2")

      pg.moveTo(942, 634, 0.6)
      pg.click()
    except:
      print("[There's somthing wrong]")
    # locate the picture to see whether it exists
    try:
      pg.locateOnScreen(os.path.join(CWD,'screenshot', 'main_win', 'cal_CAL0004.png'))
      # succeeds, screenshot the application
      try:
        pg.screenshot(
          os.path.join(CWD,'US01', 'test add_new_client success .png'),
          region=(520, 127, (1405-520), (870-127))
        )
      except:
        print("[Fail to locate the folder]")
    except:
      print("[Fail to find the picture or add new client function fails]")
      pg.screenshot(
        os.path.join(CWD,'US01', 'test add_new_client success .png'),
        region=(520, 127, (1405-520), (870-127))
      )
      raise

  def test_b_add_equipment(self):
    ''' add an equipment, the information show up on GUI screen correctly'''
    # choose a client to add an equipment
    try:
      pg.moveTo(632, 487, 0.7)
      pg.click()

      btn_choose_client = pg.locateOnScreen(
        os.path.join(CWD, 'screenshot' ,'main_win' ,'choose_client.png'),
        grayscale=False, confidence=.9)
      pg.moveTo(btn_choose_client)
      pg.click()
    except:
      print("[Fail to find the picture or choose function fails]")
      raise

    # move to the button
    try:
      btn_add_new_equipment = pg.locateOnScreen(
        os.path.join(CWD, 'screenshot' ,'main_win_info' ,'info_add_new_equipment.png'),
        grayscale=False, confidence=.9)
      pg.moveTo(btn_add_new_equipment)
      pg.click()
    except:
      print("[Fail to find the picture or add new equipment function fails]")
      raise
    # finishing adding the equipment
    try:
      pg.moveTo(947, 473, 0.7)
      pg.click()
      pg.write("1234")

      pg.moveTo(999, 513, 0.7)
      pg.click()
      pg.write("test mode")

      pg.moveTo(962, 540, 0.7) # submit
      pg.click()
    except:
      print("[Fail to find the picture or add new equipment function fails]")
      raise

    try:
      pg.locateOnScreen(os.path.join(CWD, 'screenshot', 'main_win_info', 'info_id.png'))
      # print(result) # if successful, would print out the box area
      try:
        pg.screenshot(
          os.path.join(CWD,'US01', 'test add_new_equipemnt success .png'),
          region=(520, 127, (1405-520), (870-127))
        )
      except:
        print("[Fail to locate the folder]")
    except:
      print("[Fail to find the picture or add new equipment function fails]")
      pg.screenshot(
        os.path.join(CWD,'US01', 'test add_new_equipemnt fail .png'),
        region=(520, 127, (1405-520), (870-127))
      )
      raise

  def test_c_add_new_run(self):
    ''' add a pair of files to a run, timestamp marked, information on screen '''

    # check the equipment info correct or not
    try:
      pg.locateOnScreen(
        os.path.join(CWD, 'screenshot', 'main_win', 'cal_CAL0004.png'),
        grayscale=False,
        confidence = .7
      )
    except:
        raise("[CAL Number incorrect, or cannot locate the picture]")
    try:
      pg.locateOnScreen(
        os.path.join(CWD, 'screenshot', 'main_win_info', 'info_client_name.png'),
        grayscale=False,
        confidence = .7
      )
    except:
        raise("[client name incorrect, or cannot locate the picture]")
    try:
      pg.locateOnScreen(
        os.path.join(CWD, 'screenshot', 'main_win_info', 'info_serial.png'),
        grayscale=False,
        confidence = .7
      )
    except:
      raise("[serial number incorrect, or cannot locate the picture]")
    try:
      pg.locateOnScreen(
        os.path.join(CWD, 'screenshot', 'main_win_info', 'info_id.png'),
        grayscale=False,
        confidence = .7
      )
    except:
      raise("[id incorrect, or cannot locate the picture]")

    # if all data correctly shown on the form, choose an equipment to add new run
    try:
      pg.moveTo(604, 606, 0.7)
      pg.click()

      btn_choose_equipment = pg.locateOnScreen(
        os.path.join(CWD, 'screenshot' ,'main_win_info' ,'info_choose_equipment.png'),
        grayscale=False, confidence=.9)

      pg.moveTo(btn_choose_equipment)
      pg.click()
    except:
      print("[Fail to find the picture or choose equipment function fails]")
      raise

    # go on testing the add new run functions
    try:
      btn_add_new_run = pg.locateOnScreen(
        os.path.join(CWD, 'screenshot', 'main_win_equip', 'equip_add_new_run.png'),
        grayscale=False,
        confidence = .9
      )

      pg.moveTo(btn_add_new_run)
      pg.click()
    except:
      raise("cannot locate the button add new run")

    # check the submit is successful
    try:
      pg.moveTo(674, 470, 0.7) # client file
      pg.click()

      pg.moveTo(977, 560, 0.7) # file
      pg.click()

      pg.moveTo(1281, 912, 0.7) # open
      pg.click()

      pg.moveTo(669, 539, 0.7) # lab file
      pg.click()

      pg.moveTo(907, 589, 0.7) # file
      pg.click()

      pg.moveTo(1281, 912, 0.7)
      pg.click()

      pg.moveTo(967, 601, 0.7) #submit
      pg.click()

      pg.locateOnScreen(
        os.path.join(CWD, 'screenshot', 'main_win', 'cal_CAL0004.png'),
        grayscale=False,
        confidence = .7
      )
      try:
        pg.screenshot(
          os.path.join(CWD,'US01', 'test add_new_run success .png'),
          region=(520, 127, (1405-520), (870-127))
        )
      except:
        print("[Fail to locate the folder]")
    except:
      pg.screenshot(
        os.path.join(CWD,'US01', 'test add_new_run fail .png'),
        region=(520, 127, (1405-520), (870-127))
      )
      raise("[CAL Number incorrect, or cannot locate the picture, or submit fails]")

  def test_d_delete_run(self):
    ''' delete a run in the equipment page '''
    try:
      pg.moveTo(685, 568, 0.7) # row data
      pg.click()

      btn_del = pg.locateOnScreen(
        os.path.join(CWD, 'screenshot', 'main_win_equip', 'equip_del_run.png'),
        grayscale=False,
        confidence = .9
      )
      pg.moveTo(btn_del)
      pg.click()

      pg.moveTo(933, 534, 0.7) # confirm delete the run
      pg.click()

      # if cannot find the data id, meaning the data has been deleted successfully
      # directly screenshot the data id for scanning
      try:
        # data
        data_x = 543
        data_y = 555
        pg.screenshot(
          os.path.join(CWD, 'screenshot', 'main_win_equip', 'equip_data.png'),
          region=(
            data_x,
            data_y,
            (817 - data_x),
            (587 - data_y)
          )
        )
        # print(data)
      except:
        print("[Saving file failed]")

      sleep(1) # prepare for picture locating
      try:
        data = pg.locateOnScreen(
          os.path.join(CWD, 'screenshot', 'main_win_equip', 'equip_data.png'),
          grayscale=False,
        )
        if data is None:
          print("[Data successfully deleted]")
          sleep(1) # pop window image get screenshot
          pg.screenshot(
          os.path.join(CWD,'US01', 'test_delete_run success .png'),
          region=(520, 127, (1405-520), (870-127))
          )
        else:
          print("[Data deletion failed]")
          pg.screenshot(
          os.path.join(CWD,'US01', 'test_delete_run fail .png'),
          region=(520, 127, (1405-520), (870-127))
          )
      except:
        print("[Fail to locate the filepath]")

    except:
      pg.screenshot(
      os.path.join(CWD,'US01', 'test_delete_run fail .png'),
      region=(520, 127, (1405-520), (870-127))
      )
      raise("[Data deletion failed]")

  def test_e_del_client(self):
    """Return to homepage to delete a client
    """
    try:
      btn_home = pg.locateOnScreen(
        os.path.join(CWD, 'screenshot', 'main_win_info', 'info_home.png'),
        grayscale=False,
        confidence = .8
      )
      pg.moveTo(btn_home)
      pg.click()
      sleep(1)
    except:
      raise("[Fail to find the picture or home function fails]")

    try:
      pg.moveTo(669, 484, 0.7) # selecte one client
      pg.click()

      pg.moveTo(1235, 387, 0.7) # delete client button, fail to capture the picture
      pg.click()

      pg.moveTo(941, 533, 0.7)
      pg.click()
    except:
      raise("[Fail to find the picture delete function fails]")

    sleep(1) # for the picture locating precision
    try:
      image = pg.locateOnScreen(
        os.path.join(CWD, 'screenshot', 'main_win', 'cal_CAL0004.png'),
        grayscale=False,
        confidence = .9
      )
      # if image cannot be found, it would be None; otherwise screenshot the failure
      if image is None:
        print("[The client has been deleted successfully]")
        try:
          pg.screenshot(
            os.path.join(CWD,'US01', 'test_del_client success .png'),
            region=(520, 127, (1405-520), (870-127))
            )
        except:
          print("[Fail to locate the folder]")
      else:
        print("[Fail to delete the client, or the picture detection fail]")
        pg.screenshot(
          os.path.join(CWD,'US01', 'test_del_client fail .png'),
          region=(520, 127, (1405-520), (870-127))
          )
    except:
      print("[Fail to locate the filepath]")

# test the client update button -> manully, successful
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUserStory1)
    unittest.TextTestRunner(verbosity=2).run(suite)
