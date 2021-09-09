# Overview
The script in the folder is for screenshot the elements on the application screen.
The application opens in the (1920, 1080) resolution, the centered main screen. Note that
the application might automatically be resized that the script could've cropped the wrong
position. The screenshots are saved in the folders by using the same-named Python script.

# Purpose
The screenshots are used in the tests to locate the element by using OpenCV.
It could be handy to assert if a component exists, such as button elements, without specifying
element location. 

# Usage
To crop a picture, the starting location (x, y) and the width, height is necessary with the PyAutoGUI
library. Please see its documentation for more details ( https://pyautogui.readthedocs.io/en/latest/ ).
