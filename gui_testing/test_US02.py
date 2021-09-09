"""
  The test file need to be run inside the gui_testing directory,
  with application centered on the (1920,1080) resolution main screen.
  The test cases are for the system testing, with the tests visulized.
  The test cases are testing the user story 2, mainly with the functionalities
  regarding:
    1. Checking the information typed by the client
    2. Search the CAL_num and client name functionality

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

class TestUserStory2(unittest.TestCase):
  """The user story 2 related system testing

  Args:
      unittest ([type]): [The default testing module from Python]
  """
  @classmethod
  def setUpClass(self):
      try:
        folder = os.getcwd() + "\\US02 Fail"
        shutil.rmtree(folder)
      except:
        print("[There's no such directory]")

      try:
        folder = os.getcwd() + "\\US02 Success"
        shutil.rmtree(folder)
      except:
        print("[There's no such directory]")

      try:
        folder = os.getcwd() + "\\US02"
        shutil.rmtree(folder)
      except:
        print("[There's no such directory]")

      try:
        self.cwd = os.getcwd() # for printing the current directory
        # print(self.cwd)
        os.mkdir("US02")
        os.chdir("US02") # cd to the directory for saving screenshots
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
        os.rename("US02", "US02 Fail")
        return
    os.chdir("..")
    os.rename("US02", "US02 Success")

  def test_a_information_correct(self):
    """Add a client, and check the info on the next page
    """
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
      pg.moveTo(942, 464, 0.5) # cal number
      pg.click()
      pg.write("CAL00005")

      pg.moveTo(942, 502, 0.5) # client name
      pg.click()
      pg.write("Alex")

      pg.moveTo(942, 540, 0.5) # address 1
      pg.click()
      pg.write("Sky island")

      pg.moveTo(942, 577, 0.5) # address 2
      pg.click()
      pg.write("The treasure cruise")

      # screenshot client information for checking
      # client number
      pg.screenshot(
        os.path.join(CWD,'screenshot', 'main_win' , 'cal_num.png'),
        region=(844, 454, (1279-844), (476-454))
      )

      # client name
      pg.screenshot(
        os.path.join(CWD,'screenshot', 'main_win' , 'client_name.png'),
        region=(844, 493, (1279-844), (512-493))
      )

      # client address1
      pg.screenshot(
        os.path.join(CWD,'screenshot', 'main_win' , 'cal_address1.png'),
        region=(844, 527, (1279-844), (548-527))
      )

      # client address2
      pg.screenshot(
        os.path.join(CWD,'screenshot', 'main_win' , 'cal_address2.png'),
        region=(844, 563, (1279-844), (584-563))
      )

      pg.screenshot(
        os.path.join(CWD,'US02', 'user information for comparison .png'),
        region=(520, 127, (1405-520), (870-127))
      )

      pg.moveTo(942, 634, 0.5) # submit
      pg.click()
    except:
      print("[There's somthing wrong]")

    # choose a client and go to equip page
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

    # check information
    # check cal_num
    try:
      cal_num = pg.locateOnScreen(
        os.path.join(CWD, 'screenshot' ,'main_win' ,'cal_num.png'),
        grayscale=False,
        confidence=.45)
      print(f"The client number position: {cal_num}")
    except:
      print("[Fail to locate the cilent number, or information incorrect]")
      raise

    # check client name
    try:
      cal_name = pg.locateOnScreen(
        os.path.join(CWD, 'screenshot' ,'main_win' ,'client_name.png'),
        grayscale=False,
        confidence=.9)
      print(f"The client name position: {cal_name}")
    except:
      print("[Fail to locate the cilent name, or information incorrect]")
      raise

    # check client address1
    try:
      cal_address1 = pg.locateOnScreen(
        os.path.join(CWD, 'screenshot' ,'main_win' ,'cal_address1.png'),
        grayscale=False,
        confidence=.9)
      print(f"The client address1 position: {cal_address1}")
    except:
      print("[Fail to locate the cilent address1, or information incorrect]")
      raise

    # check client address2
    try:
      cal_address2 = pg.locateOnScreen(
        os.path.join(CWD, 'screenshot' ,'main_win' ,'cal_address2.png'),
        grayscale=False,
        confidence=.9)
      print(f"The client address2 position: {cal_address2}")
    except:
      print("[Fail to locate the cilent address2, or information incorrect]")
      raise

    pg.screenshot(
      os.path.join(CWD,'US02', 'test_a_information_correct success .png'),
      region=(520, 127, (1405-520), (870-127))
    )

    # back to homepage for next testcase
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

  def test_b_search_bar(self):
    """Continue from test a, and another user to test the search bar
    The main page information shows the matching results; otherwise, blank
    """
    # the client "CAL0005 Alex sky island treasure cruise" has been added
    # by the previous testcase

    # create another user for testing search bar
    test_US01.TestUserStory1.test_a_add_new_client(self)

    pg.moveTo(645, 337, 0.7) # the search bar
    pg.click()
    pg.write("CAL00005")

    # data
    pg.screenshot(
      os.path.join(CWD,'screenshot', 'main_win' , 'search_CAL00005.png'),
      region=(544, 469, (955-544), (496-469))
    )

    try:
      search_CAL00005 = pg.locateOnScreen(
        os.path.join(CWD, 'screenshot' ,'main_win' ,'search_CAL00005.png'),
        grayscale=False,
        confidence=.9)
      print(f"The search CAL number result position: {search_CAL00005}")
      pg.screenshot(
        os.path.join(CWD,'US02', 'search CAL number success .png'),
        region=(520, 127, (1405-520), (870-127))
        )
    except:
      pg.screenshot(
        os.path.join(CWD,'US02', 'search CAL number fail .png'),
        region=(520, 127, (1405-520), (870-127))
        )
      print("[Fail to locate the picture, or information incorrect]")

    sleep(3) # stay for a while to be seen
    pg.click()

    # hotkey to delete the search text
    pg.hotkey('ctrl','a')
    pg.hotkey('delete')

    # search the client name
    pg.click()
    pg.write("Alex")
    # should see the search result

    sleep(3)

    # client name data
    pg.screenshot(
      os.path.join(CWD,'screenshot', 'main_win' , 'search_Alex.png'),
      region=(963, 469, (1364-963), (496-469))
    )

    sleep(1)

    try:
      search_Alex = pg.locateOnScreen(
        os.path.join(CWD, 'screenshot' ,'main_win' ,'search_Alex.png'),
        grayscale=False,
        confidence=.9)
      print(f"The search client name result position: {search_Alex}")

      pg.screenshot(
        os.path.join(CWD,'US02', 'search client name success .png'),
        region=(520, 127, (1405-520), (870-127))
        )
    except:
      pg.screenshot(
        os.path.join(CWD,'US02', 'search client name fail .png'),
        region=(520, 127, (1405-520), (870-127))
        )
      print("[Fail to locate the picture, or information incorrect]")

    sleep(1)
    pg.click()

    # hotkey to delete the search text
    pg.hotkey('ctrl','a')
    pg.hotkey('delete')

    # the case that the client information not in the list
    pg.click()
    pg.write("CAL00001")

    sleep(3)

    # hotkey to delete the search text
    pg.click()
    pg.hotkey('ctrl','a')
    pg.hotkey('delete')

    pg.screenshot(
      os.path.join(CWD,'US02', 'all information success .png'),
      region=(520, 127, (1405-520), (870-127))
      )
    # all the information should be back
    # delete two clients
    test_US01.TestUserStory1.test_e_del_client(self)
    test_US01.TestUserStory1.test_e_del_client(self)


if __name__ == '__main__':
  suite = unittest.TestLoader().loadTestsFromTestCase(TestUserStory2)
  unittest.TextTestRunner(verbosity=2).run(suite)
