import unittest
from tkinter import *
from calculator2 import start_application
from calculator2 import calc

class TestCalculator2(unittest.TestCase):

  # start the application, test, and destroy at the end of the test
  async def _start_app(self):
    self.app.mainloop() # the root in Tkinter activates the mainloop(), but only _tkinter.tkapp return without calculator

  def setUp(self):
    self.app = start_application() # activate the root
    self.calc = calc(self.app) # instantiate the calculator
    self._start_app()

  def tearDown(self):
    self.app.destroy()

class TestCalculation(TestCalculator2):
  
  def test_startup(self):
    title = self.app.winfo_toplevel().title()
    expected = "Calculator"
    self.assertEqual(title, expected)

  def test_addition(self):
    self.calc.btn_AC.invoke()
    self.calc.btn_7.invoke()
    self.calc.btn_plus.invoke()
    self.calc.btn_5.invoke()
    result = self.calc.btn_equal.invoke()
    self.assertEqual(result, 12)