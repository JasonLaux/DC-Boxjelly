# Overview
The folder includes the test scripts and the element screenshots. Each script would
test the functionalities specified in the sprint one user-story backlog. More details
and workflows are specified in the scripts.

# Tools
There are two main tools used in GUI (graphical user interface) testing.
  - PyautoGUI
    The library automates and mimics the user behaviors while using the application.
    Please see its documentation for more details (https://pyautogui.readthedocs.io/en/latest/).
  
  - OpenCV
    The library detects the cropped images, screenshots and records the screen.
    Please see its documentation for more details (https://docs.opencv.org/master/).

# US0X Success/Fail folder
The folders are generated during the tests. According to its test cases, the folder name would
be the user story number with the "Success" or "Fail" string. The screenshots inside the folder
are evidence for the test cases.

# Others
  - to use one test case only inside a script
    - py -m unittest test_US01.TestUserStory1.test_e_del_client