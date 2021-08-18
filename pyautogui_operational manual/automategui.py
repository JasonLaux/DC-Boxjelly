'''
    File name: automategui
    Author: Chien-Chih Wang
    Date created: 18/08/2020
    Python version: 3.9

    This is the prototype to use pyautogui to generate the automatic demonstration and the screenshots.
    The Tkinter application pops out the window in the center of the primary monitor. The resolution is (1920, 1080).
    Please open the calculator before running the script, and make sure the GUI shown in the middle without other overlapping windows.

'''

import pyautogui

screenWidth, screenHeight = pyautogui.size()
# print(screenWidth, screenHeight) # 1920 1080

currentMouseX, currentMouseY = pyautogui.position()
# pyautogui.displayMousePosition() # constantly show the mouse position on the console


# click button AC
pyautogui.moveTo(1053, 495, duration=2)
pyautogui.click()

# click button 1
pyautogui.moveTo(838, 617, duration=2) # will move mouse even is not the primary monitor
pyautogui.click()

# click button plus
pyautogui.moveTo(994,703, duration=2)
pyautogui.click()

# click button 1
pyautogui.moveTo(838, 617, duration=2)
pyautogui.click()

# click equal
pyautogui.moveTo(1078, 700, duration=2)
pyautogui.click()

# screenshot on the calculator, specify the coornidates
# region(x=0 , y=0, width_extend_right, height_entend_down)
image_calc = pyautogui.screenshot('calculator.png', region=(791,378,353,360))