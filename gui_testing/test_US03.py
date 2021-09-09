"""
  The test file need to be run inside the gui_testing directory,
  with application centered on the (1920,1080) resolution main screen.
  The test cases are for the system testing, with the tests visulized.
  The test cases are testing the user story 3, mainly with the functionalities
  regarding:
    1. The data is correctly saved.
    2. The data shows up when open the application next time.

"""

import unittest
import os
import shutil
from time import sleep
import pyautogui as pg
import test_US01

# W0311: bad indentation; E1101:no-member; C0325: Unnecessary parens
# pylint: disable=W0311, E1101, C0325

# use the current directory, where the script exists
CWD = os.path.dirname(os.path.realpath(__file__))

class TestUserStory3(unittest.TestCase):
  """The user story 3 related system testing

  Args:
      unittest ([type]): [The default testing module from Python]
  """
  @classmethod
  def setUpClass(self):
    try:
      folder = os.getcwd() + "\\US03 Fail"
      shutil.rmtree(folder)
    except:
      print("[There's no such directory]")

    try:
      folder = os.getcwd() + "\\US03 Success"
      shutil.rmtree(folder)
    except:
      print("[There's no such directory]")

    try:
      folder = os.getcwd() + "\\US03"
      shutil.rmtree(folder)
    except:
      print("[There's no such directory]")

    try:
      self.cwd = os.getcwd() # for printing the current directory
      # print(self.cwd)
      os.mkdir("US03")
      os.chdir("US03") # cd to the directory for saving screenshots
      self.storage = '%s/' % os.getcwd() # escape the cwd string
    except:
      print("[Something is wrong when creating the directory]")

  @classmethod
  def tearDownClass(self):
    file_list = os.listdir()
    # print(file_list)
    # iterate through the filename string, if there's a keyword "fail", rename the folder
    for filename in file_list:
      if "fail" in filename:
        # print("Some tests failed")
        os.chdir("..")
        os.rename("US03", "US03 Fail")
        return
    os.chdir("..")
    os.rename("US03", "US03 Success")

  def test_a_keep_client_data(self):
    """Add a client, a equipment, and a run, information kept
    Before the test, the folder should be brought to the background.
    The mouse position might need adjustment. See gif illustration.
    """
    test_US01.TestUserStory1.test_a_add_new_client(self)
    test_US01.TestUserStory1.test_b_add_equipment(self)
    test_US01.TestUserStory1.test_c_add_new_run(self)

    # screenshot the run id for opencv detection later
    # data
    try:
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
    except:
      print("[Saving file failed]")

    # the task need to locate the folder to re-open the application again
    pg.moveTo(1360, 150, 0.7) # cross tab to close the application
    pg.click()

    pg.moveTo(906, 537, 0.7) # yes tab
    pg.click()

    sleep(1)

    pg.moveTo(1332, 581, 0.7) # empty place in the folder
    pg.click() # focus in the folder

    pg.moveTo(370, 840, 0.7) # where the application in the folder
    pg.doubleClick()

    # TODO: it needs approximately 15-30 seconds to open the application in my computer
    sleep(35)

    # the application should pop up and focused

    try:
      cal_num = pg.locateOnScreen(os.path.join(CWD,'screenshot', 'main_win', 'cal_CAL0004.png'))
      print(f"The cal num position: {cal_num}")
    except:
      print("[Fail to locate the picture, or the client information missing]")
      raise

    # choose client
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

    # choose equipment
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


    sleep(1) # prepare for picture locating
    try:
      run_data = pg.locateOnScreen(
        os.path.join(CWD, 'screenshot', 'main_win_equip', 'equip_data.png'),
        grayscale=False,
      )
      print(f"The run data position: {run_data}")
    except:
      print("[Fail to locate the picture, or equipment runs data missing]")

    try:
      pg.screenshot(
      os.path.join(CWD,'US03', 'test_a_keep_client_data success .png'),
      region=(520, 127, (1405-520), (870-127))
      )
    except:
      pg.screenshot(
      os.path.join(CWD,'US03', 'test_a_keep_client_data fail .png'),
      region=(520, 127, (1405-520), (870-127))
      )
    # the last step, delete the client
    test_US01.TestUserStory1.test_e_del_client(self)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUserStory3)
    unittest.TextTestRunner(verbosity=2).run(suite)
