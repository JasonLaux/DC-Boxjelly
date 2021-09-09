"""
  The test file need to be run inside the gui_testing directory,
  with application centered on the (1920,1080) resolution main screen.
  The test cases are for the system testing, with the tests visulized.
  The test cases are testing the user story 4, mainly with the functionalities
  regarding:
    1. After client add an equipment and a run, the application could pop up the analysis.
    2. The client could add two runs, select multiple runs to be analyzed.

  Note that the opencv is limited to access the information within the text field, which
  means the tests aren't 100 percent assured. The current way is to screenshot the user
  input and the equipment page for comparison.

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

class TestUserStory4(unittest.TestCase):
  """The user story 4 related system testing

  Args:
      unittest ([type]): [The default testing module from Python]
  """
  @classmethod
  def setUpClass(self):
    """Create or replace previous folders
    """
    try:
      folder = os.getcwd() + "\\US04 Fail"
      shutil.rmtree(folder)
    except:
      print("[There's no such directory]")

    try:
      folder = os.getcwd() + "\\US04 Success"
      shutil.rmtree(folder)
    except:
      print("[There's no such directory]")

    try:
      folder = os.getcwd() + "\\US04"
      shutil.rmtree(folder)
    except:
      print("[There's no such directory]")

    try:
      self.cwd = os.getcwd() # for printing the current directory
      # print(self.cwd)
      os.mkdir("US04")
      os.chdir("US04") # cd to the directory for saving screenshots
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
        os.rename("US02", "US04 Fail")
        return
    os.chdir("..")
    os.rename("US02", "US04 Success")

  def test_a_single_run(self):
    """A client add a equipment, add a set of data, then analyze
    """
    # use the existing test cases, but would show up "[Fail to locate the folder]"
    # since the screenshots are presumed to be saved in the US01 folder
    test_US01.TestUserStory1.test_a_add_new_client(self)
    test_US01.TestUserStory1.test_b_add_equipment(self)
    test_US01.TestUserStory1.test_c_add_new_run(self)

    pg.moveTo(649, 575, 0.7)
    pg.click()

    btn_analyze = pg.locateOnScreen(
      os.path.join(CWD, 'screenshot', 'main_win_equip', 'equip_analyze.png'),
      grayscale=False,
      confidence = .7
    )

    pg.moveTo(btn_analyze)
    pg.click()

    sleep(3) # waiting the window to pop up

    pg.screenshot(
      os.path.join(CWD,'US02', 'test single analyze success .png'),
      region=(345, 36, (1569-520), (960-36))
    )

    pg.moveTo(1532, 60, 0.7) # cross tab
    pg.click()

    pg.moveTo(905, 534, 0.7) # yes
    pg.click()

    sleep(1)
    test_US01.TestUserStory1.test_e_del_client(self)

  def test_b_two_runs(self):
    """A client add a equipment, add two set of data, then analyze
    """
    test_US01.TestUserStory1.test_a_add_new_client(self)
    test_US01.TestUserStory1.test_b_add_equipment(self)
    test_US01.TestUserStory1.test_c_add_new_run(self)

    # add another run
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
      pg.moveTo(674, 470, 0.7) # client file tab
      pg.click()

      pg.moveTo(910, 613, 0.7) # file
      pg.click()

      pg.moveTo(1281, 912, 0.7) # open
      pg.click()

      pg.moveTo(669, 539, 0.7) # lab file tab
      pg.click()

      pg.moveTo(910, 638, 0.7) # file
      pg.click()

      pg.moveTo(1281, 912, 0.7) # open
      pg.click()

      pg.moveTo(967, 601, 0.7) #submit
      pg.click()
    except:
      print("[Fail to locate the folder]")

    pg.moveTo(671, 717, 0.7) # empty space
    pg.click()
    # hotkey to select all runs
    pg.hotkey('ctrl','a')

    # locate the analyze button
    try:
      btn_analyze = pg.locateOnScreen(
      os.path.join(CWD, 'screenshot', 'main_win_equip', 'equip_analyze.png'),
      grayscale=False,
      confidence = .7
      )

      pg.moveTo(btn_analyze)
      pg.click()
    except:
      print("[Fail to locate the picture]")

    try:
      sleep(3) # waiting the window to pop up

      pg.screenshot(
        os.path.join(CWD,'US02', 'test two runs analyze success .png'),
        region=(345, 36, (1569-520), (960-36))
      )

      pg.moveTo(1532, 60, 0.7) # cross tab
      pg.click()

      pg.moveTo(905, 534, 0.7) # yes
      pg.click()
    except:
      print("[Fail to locate the folder]")

    sleep(1)
    test_US01.TestUserStory1.test_e_del_client(self)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUserStory4)
    unittest.TextTestRunner(verbosity=2).run(suite)
