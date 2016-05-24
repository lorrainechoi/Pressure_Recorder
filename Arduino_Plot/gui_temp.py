from Tkinter import *
from tkFileDialog import askopenfilename
import os

class Application(Frame) :

    def __init__(self, master):
        """Initilise the Frame"""
        Frame.__init__(self, master)
        self.grid()
        self.filename = ''
        self.filepath = ''
        self.create_browse_button()

    def create_browse_button(self):
        """Create Browse Button"""
        self.browse_label = Label(self, text = "Save csv file in:")
        self.browse_label.grid(row = 0, column = 0, sticky = 'E', padx = 5, pady = 4)

        self.browse_filepath = Entry(self, width = 70, textvariable = self.filepath)
        self.browse_filepath.grid(row = 0, column = 1, sticky = 'E', columnspan = 25, padx = 5, pady = 4)

        self.browse_button = Button(self, text = "Browse", command = self.askopenfile)
        self.browse_button.grid(row = 0, column = 27, padx = 5, pady = 4)
        print self.filename

    def askopenfile(self):
        """ Method to locate file path and display in entry box """
        self.filename = askopenfilename()
        self.filepath = os.path.dirname(self.filename)
        self.browse_filepath.delete(0, END)
        self.browse_filepath.insert(0, self.filepath)
        # print self.filepath

root = Tk()
root.title("Pressure Touch Music")
root.geometry("800x500")
app = Application(root)
root.mainloop()
