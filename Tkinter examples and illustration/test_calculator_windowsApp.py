'''
    File name: test_calculator_windowsApp
    Author: Chien-Chih Wang
    Date created: 18/08/2020
    Python version: 3.9

    The file is built for the demonstration of end-to-end testing on Window calculator.
    The Windows application driver is the tool for testing the standalone application.
    The appium module can directly get the application attributes through the graphical user interface.
    For more details, see Windows application driver ( https://github.com/microsoft/WinAppDriver )

'''

import unittest
from appium import webdriver

class SimpleCalculatorTests(unittest.TestCase):

    @classmethod

    def setUpClass(self):
        #set up appium
        desired_caps = {}
        desired_caps["app"] = "Microsoft.WindowsCalculator_8wekyb3d8bbwe!App"
        self.driver = webdriver.Remote(
            command_executor='http://127.0.0.1:4723',
            desired_capabilities= desired_caps)

    @classmethod
    def tearDownClass(self):
        self.driver.quit()

    def getresults(self):
        displaytext = self.driver.find_element_by_accessibility_id("CalculatorResults").text
        displaytext = displaytext.strip("Display is " )
        displaytext = displaytext.rstrip(' ')
        displaytext = displaytext.lstrip(' ')
        return displaytext


    def test_initialize(self):
        self.driver.find_element_by_name("Clear").click()
        self.driver.find_element_by_name("Seven").click()
        self.assertEqual(self.getresults(),"7")
        self.driver.find_element_by_name("Clear").click()

    def test_addition(self):
        self.driver.find_element_by_name("One").click()
        self.driver.find_element_by_name("Plus").click()
        self.driver.find_element_by_name("Seven").click()
        self.driver.find_element_by_name("Equals").click()
        self.assertEqual(self.getresults(),"8")

    def test_combination(self):
        self.driver.find_element_by_name("Seven").click()
        self.driver.find_element_by_name("Multiply by").click()
        self.driver.find_element_by_name("Nine").click()
        self.driver.find_element_by_name("Plus").click()
        self.driver.find_element_by_name("One").click()
        self.driver.find_element_by_name("Equals").click()
        self.driver.find_element_by_name("Divide by").click()
        self.driver.find_element_by_name("Eight").click()
        self.driver.find_element_by_name("Equals").click()
        self.assertEqual(self.getresults(),"8")

    def test_division(self):
        self.driver.find_element_by_name("Eight").click()
        self.driver.find_element_by_name("Eight").click()
        self.driver.find_element_by_name("Divide by").click()
        self.driver.find_element_by_name("One").click()
        self.driver.find_element_by_name("One").click()
        self.driver.find_element_by_name("Equals").click()
        self.assertEqual(self.getresults(),"8")

    def test_multiplication(self):
        self.driver.find_element_by_name("Nine").click()
        self.driver.find_element_by_name("Multiply by").click()
        self.driver.find_element_by_name("Nine").click()
        self.driver.find_element_by_name("Equals").click()
        self.assertEqual(self.getresults(),"81") 

    def test_subtraction(self):
        self.driver.find_element_by_name("Nine").click()
        self.driver.find_element_by_name("Minus").click()
        self.driver.find_element_by_name("One").click()
        self.driver.find_element_by_name("Equals").click()
        self.assertEqual(self.getresults(),"8")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleCalculatorTests)
    unittest.TextTestRunner(verbosity=2).run(suite)