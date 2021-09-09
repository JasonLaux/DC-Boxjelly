"""
  The record_gif aims for recording the part of the screen automatically
  during the GUI test. Then, the script ends the recording and convert the
  video to gif image under the same folder. It's complementary to the GUI
  user story acceptance criteria tests. The script would record a mp4 format
  video, and convert it to gif under the
  same folder.

  Note:
    1. The current solution doesn't record the the mouse position.
    2. The video-to-gif convertion need to download the ffmpeg.exe.
    ( https://ffmpeg.org/download.html)
    3. The solution is incomplete.

"""

import numpy as np
import cv2
from PIL import ImageGrab
import pyautogui as pg
import ffmpy

# W0311: bad indentation; E1101:no-member
# pylint: disable=W0311, E1101

RECORDING = True
FFMPEG_EXE_PATH = r"D:\Master of IT\Semester4\software project\ffmpeg\bin\ffmpeg.exe"

# reference: https://www.youtube.com/watch?v=KTlgVCrO7IQ&ab_channel=ibrahimokdadov
# the resolution must from bbox width, height below minus its starting point in the out;
# otherwise, video cannot be played

# TODO: display the mouse cursor while recording
TEST_NAME = "test"
VIDEO_NAME = TEST_NAME + '.mp4'

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
# output would be name of the video, video type, frame rate, (resolution)
out = cv2.VideoWriter(VIDEO_NAME, fourcc, 8, (1920-520-520, 1000-127-127))

while True:
  # bbox = (start_x, start_y, (end_x - start_x, end_y - start_y))
  # catch the exe window pop up place
  # TODO: the image here could try pyautogui -> get the mouse position
  img = ImageGrab.grab(bbox=(520, 127, (1920-520), (1000-127)))
  img_np = np.array(img)

  # covert the img_np array's color scheme
  frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)

  # show on the Screen window
  cv2.imshow("Screen", img_np)

  # the video would write the frame
  out.write(frame)

  # TODO: how to run the script with the test case?
  # the waitkey should use 1 instead of 0; otherwise cannot record
  if cv2.waitKey(1) & 0xFF == 27:
    break

out.release()
cv2.destroyAllWindows()

ff = ffmpy.FFmpeg(
  global_options=['-y'],
  executable = FFMPEG_EXE_PATH, # need to download the ffmpeg.exe
  inputs = {"Test.mp4": None},
  outputs = {"Test.gif": None},
)

ff.run()
