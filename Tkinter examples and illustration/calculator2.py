# importing Tkinter and math
from tkinter import *
import math

# calc class


class calc:

  def getandreplace(self):
    """replace x with * and ÷ with /"""
    self.expression = self.e.get()
    self.newtext = self.expression.replace('/', '/')
    self.newtext = self.newtext.replace('x', '*')

  def equals(self):
    """when the equal button is pressed"""
    self.getandreplace()
    try:
      # evaluate the expression using the eval function
      self.value = eval(self.newtext)
    except SyntaxError or NameError:
      self.e.delete(0, END)
      self.e.insert(0, 'Invalid Input!')
    else:
      self.e.delete(0, END)
      # self.e.insert(0, self.value) # comment out here to show the GUI bug, but the unit test passed
    return self.value

  def squareroot(self):
    """squareroot method"""
    self.getandreplace()
    try:
      # evaluate the expression using the eval function
      self.value = eval(self.newtext)
    except SyntaxError or NameError:
      self.e.delete(0, END)
      self.e.insert(0, 'Invalid Input!')
    else:
      self.sqrtval = math.sqrt(self.value)
      self.e.delete(0, END)
      self.e.insert(0, self.sqrtval)

  def square(self):
    """square method"""
    self.getandreplace()
    try:
      # evaluate the expression using the eval function
      self.value = eval(self.newtext)
    except SyntaxError or NameError:
      self.e.delete(0, END)
      self.e.insert(0, 'Invalid Input!')
    else:
      self.sqval = math.pow(self.value, 2)
      self.e.delete(0, END)
      self.e.insert(0, self.sqval)

  def clearall(self):
    """when clear button is pressed,clears the text input area"""
    self.e.delete(0, END)

  def clear1(self):
    self.txt = self.e.get()[:-1]
    self.e.delete(0, END)
    self.e.insert(0, self.txt)

  def action(self, argi):
    """pressed button's value is inserted into the end of the text area"""
    self.e.insert(END, argi)

  def callback(self, e):
    print(e.widget) # print out the button clicked https://stackoverflow.com/questions/4299145/getting-the-widget-that-triggered-an-event
    e.widget.invoke()
    return e.widget

  def __init__(self, master):
      """Constructor method"""
      master.title('Calculator')
      master.geometry()
      self.e = Entry(master)
      self.e.grid(row=0,column=0,columnspan=6,pady=3)
      
      self.e.focus_set() #Sets focus on the input text area

      # Generating Buttons; careful to the Nonetype object returned when chaining methods
      # reference: https://stackoverflow.com/questions/1101750/tkinter-attributeerror-nonetype-object-has-no-attribute-attribute-name

      self.btn_equal = Button(master,text="=",width=11,height=3, fg="red", bg="light green",command=lambda:self.equals())
      self.btn_equal.grid(row=4, column=4,columnspan=2)

      self.btn_AC = Button(master,text='AC',width=5,height=3,fg="red", bg="light green", command=lambda:self.clearall())
      self.btn_AC.grid(row=1, column=4)

      self.btn_C = Button(master,text='C',width=5,height=3, fg="red",bg="light green", command=lambda:self.clear1())
      self.btn_C.grid(row=1, column=5)

      self.btn_plus = Button(master,text="+",width=5,height=3, fg="blue",bg="orange", command=lambda:self.action('+'))
      self.btn_plus.grid(row=4, column=3)

      self.btn_muliply = Button(master,text="x",width=5,height=3, fg="blue",bg="orange", command=lambda:self.action('x'))
      self.btn_muliply.grid(row=2, column=3)

      self.btn_minus = Button(master,text="-",width=5,height=3, fg="blue",bg="orange", command=lambda:self.action('-'))
      self.btn_minus.grid(row=3, column=3)

      self.btn_divide = Button(master,text="÷",width=5,height=3, fg="blue",bg="orange", command=lambda:self.action('/'))
      self.btn_divide.grid(row=1, column=3)

      self.btn_percent = Button(master,text="%",width=5,height=3, fg="red",bg="light green", command=lambda:self.action('%'))
      self.btn_percent.grid(row=4, column=2)

      self.btn_7 = Button(master,text="7",width=5,height=3, fg="blue",bg="orange", command=lambda:self.action(7))
      self.btn_7.grid(row=1, column=0)

      self.btn_8 = Button(master,text="8",width=5,height=3, fg="blue",bg="orange", command=lambda:self.action(8))
      self.btn_8.grid(row=1, column=1)

      self.btn_9 = Button(master,text="9",width=5,height=3, fg="blue",bg="orange", command=lambda:self.action(9))
      self.btn_9.grid(row=1, column=2)

      self.btn_4 = Button(master,text="4",width=5,height=3, fg="blue",bg="orange", command=lambda:self.action(4))
      self.btn_4.grid(row=2, column=0)

      self.btn_5 = Button(master,text="5",width=5,height=3, fg="blue",bg="orange", command=lambda:self.action(5))
      self.btn_5.grid(row=2, column=1)

      self.btn_6 = Button(master,text="6",width=5,height=3, fg="blue",bg="orange", command=lambda:self.action(6))
      self.btn_6.grid(row=2, column=2)

      self.btn_1 = Button(master,text="1",width=5,height=3, fg="blue",bg="orange", command=lambda:self.action(1))
      self.btn_1.grid(row=3, column=0)

      self.btn_2 = Button(master,text="2",width=5,height=3, fg="blue",bg="orange", command=lambda:self.action(2))
      self.btn_2.grid(row=3, column=1)

      self.btn_3 = Button(master,text="3",width=5,height=3, fg="blue",bg="orange", command=lambda:self.action(3))
      self.btn_3.grid(row=3, column=2)

      self.btn_0 = Button(master,text="0",width=5,height=3, fg="blue",bg="orange", command=lambda:self.action(0))
      self.btn_0.grid(row=4, column=0)

      self.btn_dot = Button(master,text=".",width=5,height=3, fg="red",bg="light green", command=lambda:self.action('.'))
      self.btn_dot.grid(row=4, column=1)

      self.btn_leftparen = Button(master,text="(",width=5,height=3, fg="white",bg="blue", command=lambda:self.action('('))
      self.btn_leftparen.grid(row=2, column=4)

      self.btn_rightparen = Button(master,text=")",width=5,height=3, fg="white",bg="blue", command=lambda:self.action(')'))
      self.btn_rightparen.grid(row=2, column=5)

      self.btn_sqroot = Button(master,text="√",width=5,height=3, fg="white",bg="blue", command=lambda:self.squareroot())
      self.btn_sqroot.grid(row=3, column=4)

      self.btn_sqr = Button(master,text="x²",width=5,height=3, fg="white",bg="blue", command=lambda:self.square())
      self.btn_sqr.grid(row=3, column=5)

def start_application():
  root = Tk()
  app = calc(root)
  root.bind_class("Button", "<Button-1>", app.callback)
  return root

def return_object():
  root = Tk()
  app = calc(root)
  root.bind_class("Button", "<Button-1>", app.callback)
  return app

if __name__ == "__main__":
  start_application().mainloop()

