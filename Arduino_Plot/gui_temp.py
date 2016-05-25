from Tkinter import *
from tkFileDialog import askopenfilename
import os
import ttk

total_pads = 6
total_location = 12

class Application(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        # Tk.iconbitmap(self, default = "icon.ico")
        Tk.wm_title(self, "Pressure Touch Music")

        container = Frame(self)
        # container.grid()
        container.pack(side = "top", fill = "both", expand = True)

        # for i in range(0, 14):
        #     container.grid_rowconfigure(i, weight = 1)

        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        self.frames = {}

        for F in (InitialisePage, PlotPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = "nesw")

        self.show_frame(InitialisePage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()



class InitialisePage(Frame) :

    def __init__(self, master, controller):
        """Initilise the Frame"""
        Frame.__init__(self, master)

        grid_row = 15
        grid_column = 5

        self.grid(row = grid_row, column = grid_column, stick = 'nesw')

        title = ttk.Label(self, text = "Initialisation", font = ("", "14", "bold"))
        title.grid(row = 0, column = 0, sticky = 'EW', padx = 10)

        top = self.winfo_toplevel()

        for i in range(0, grid_row):
            top.rowconfigure(i, weight = 1)
            self.rowconfigure(i, weight = 1)

        for i in range(0, grid_column):
            top.columnconfigure(i, weight = 1)
            self.columnconfigure(i, weight = 1)

        self.filename = ''
        self.filepath = ''

        self.create_header_row()
        self.create_pad_checkbox()
        self.create_pitch_list()
        self.create_instrument_list()
        self.create_location_list()
        self.create_browse_button()

        confirm_button = ttk.Button(self, text = "Confirm", command = lambda: controller.show_frame(PlotPage))
        confirm_button.grid(row = 12, column = 0, columnspan = 5)


    def create_header_row(self):
        """Create header row"""
        column1_label = ttk.Label(self, text = "Pitch", font = ("", "10", "bold"))
        column2_label = ttk.Label(self, text = "Instrument", font = ("", "10", "bold"))
        column3_label = ttk.Label(self, text = "Location", font = ("", "10", "bold"))

        column1_label.grid(row = 1, column = 1)
        column2_label.grid(row = 1, column = 2)
        column3_label.grid(row = 1, column = 3)

    def create_pad_checkbox(self):
        """Create checkbox to indicate active pads"""
        self.padOn1 = BooleanVar()
        self.padOn2 = BooleanVar()
        self.padOn3 = BooleanVar()
        self.padOn4 = BooleanVar()
        self.padOn5 = BooleanVar()
        self.padOn6 = BooleanVar()

        pad1_check_button = ttk.Checkbutton(self, text="Pad 1", variable = self.padOn1, onvalue = True, offvalue = False)
        pad2_check_button = ttk.Checkbutton(self, text="Pad 2", variable = self.padOn2, onvalue = True, offvalue = False)
        pad3_check_button = ttk.Checkbutton(self, text="Pad 3", variable = self.padOn3, onvalue = True, offvalue = False)
        pad4_check_button = ttk.Checkbutton(self, text="Pad 4", variable = self.padOn4, onvalue = True, offvalue = False)
        pad5_check_button = ttk.Checkbutton(self, text="Pad 5", variable = self.padOn5, onvalue = True, offvalue = False)
        pad6_check_button = ttk.Checkbutton(self, text="Pad 6", variable = self.padOn6, onvalue = True, offvalue = False)

        pad1_check_button.grid(row = 2, column = 0, sticky = 'E')
        pad2_check_button.grid(row = 3, column = 0, sticky = 'E')
        pad3_check_button.grid(row = 4, column = 0, sticky = 'E')
        pad4_check_button.grid(row = 5, column = 0, sticky = 'E')
        pad5_check_button.grid(row = 6, column = 0, sticky = 'E')
        pad6_check_button.grid(row = 7, column = 0, sticky = 'E')


    def create_pitch_list(self):
        """Create dropdown list for pitch selection"""
        pitch = ["C", "D", "E", "F", "G", "A", "B", "C'"]

        pad1_pitch = StringVar()
        pad2_pitch = StringVar()
        pad3_pitch = StringVar()
        pad4_pitch = StringVar()
        pad5_pitch = StringVar()
        pad6_pitch = StringVar()

        pad1_pitch_list = ttk.OptionMenu(self, pad1_pitch, *pitch)
        pad2_pitch_list = ttk.OptionMenu(self, pad2_pitch, *pitch)
        pad3_pitch_list = ttk.OptionMenu(self, pad3_pitch, *pitch)
        pad4_pitch_list = ttk.OptionMenu(self, pad4_pitch, *pitch)
        pad5_pitch_list = ttk.OptionMenu(self, pad5_pitch, *pitch)
        pad6_pitch_list = ttk.OptionMenu(self, pad6_pitch, *pitch)

        pad1_pitch_list.grid(row = 2, column = 1, sticky = 'EW')
        pad2_pitch_list.grid(row = 3, column = 1, sticky = 'EW')
        pad3_pitch_list.grid(row = 4, column = 1, sticky = 'EW')
        pad4_pitch_list.grid(row = 5, column = 1, sticky = 'EW')
        pad5_pitch_list.grid(row = 6, column = 1, sticky = 'EW')
        pad6_pitch_list.grid(row = 7, column = 1, sticky = 'EW')


    def create_instrument_list(self):
        """Create instrument selection list per pad"""
        instrument = ["Piano", "Violin", "Flute", "Trumpet", "Xylophone", "Cymbals"]
        # [0, 40, 73, 56, 13, 119]

        pad1_instrument = StringVar()
        pad2_instrument = StringVar()
        pad3_instrument = StringVar()
        pad4_instrument = StringVar()
        pad5_instrument = StringVar()
        pad6_instrument = StringVar()

        pad1_instrument_list = ttk.OptionMenu(self, pad1_instrument, *instrument)
        pad2_instrument_list = ttk.OptionMenu(self, pad2_instrument, *instrument)
        pad3_instrument_list = ttk.OptionMenu(self, pad3_instrument, *instrument)
        pad4_instrument_list = ttk.OptionMenu(self, pad4_instrument, *instrument)
        pad5_instrument_list = ttk.OptionMenu(self, pad5_instrument, *instrument)
        pad6_instrument_list = ttk.OptionMenu(self, pad6_instrument, *instrument)

        pad1_instrument_list.grid(row = 2, column = 2, sticky = 'EW')
        pad2_instrument_list.grid(row = 3, column = 2, sticky = 'EW')
        pad3_instrument_list.grid(row = 4, column = 2, sticky = 'EW')
        pad4_instrument_list.grid(row = 5, column = 2, sticky = 'EW')
        pad5_instrument_list.grid(row = 6, column = 2, sticky = 'EW')
        pad6_instrument_list.grid(row = 7, column = 2, sticky = 'EW')


    def create_location_list(self):
        """Create pad location selection list"""
        location = range(1,13)

        pad1_location = IntVar()
        pad2_location = IntVar()
        pad3_location = IntVar()
        pad4_location = IntVar()
        pad5_location = IntVar()
        pad6_location = IntVar()

        pad1_location_list = ttk.OptionMenu(self, pad1_location, *location)
        pad2_location_list = ttk.OptionMenu(self, pad2_location, *location)
        pad3_location_list = ttk.OptionMenu(self, pad3_location, *location)
        pad4_location_list = ttk.OptionMenu(self, pad4_location, *location)
        pad5_location_list = ttk.OptionMenu(self, pad5_location, *location)
        pad6_location_list = ttk.OptionMenu(self, pad6_location, *location)

        pad1_location_list.grid(row = 2, column = 3, sticky = 'EW')
        pad2_location_list.grid(row = 3, column = 3, sticky = 'EW')
        pad3_location_list.grid(row = 4, column = 3, sticky = 'EW')
        pad4_location_list.grid(row = 5, column = 3, sticky = 'EW')
        pad5_location_list.grid(row = 6, column = 3, sticky = 'EW')
        pad6_location_list.grid(row = 7, column = 3, sticky = 'EW')


    def create_browse_button(self):
        """Create Browse Button"""
        browse_label = ttk.Label(self, text = "Save csv file in:")
        browse_label.grid(row = 9, column = 0, sticky = 'E', padx = 5, pady = 4)

        self.browse_filepath = ttk.Entry(self, textvariable = self.filepath)
        self.browse_filepath.grid(row = 9, column = 1, sticky = 'EW', columnspan = 3)

        browse_button = ttk.Button(self, text = "Browse", command = self.askopenfile)
        browse_button.grid(row = 9, column = 4, padx = 5, sticky = 'W')


    def askopenfile(self):
        """ Method to locate file path and display in entry box """
        self.filename = askopenfilename()
        self.filepath = os.path.dirname(self.filename)
        self.browse_filepath.delete(0, END)
        self.browse_filepath.insert(0, self.filepath)





class PlotPage(Frame):

    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.title = ttk.Label(self, text = "Pressure Reading from Pads")
        self.title.pack(pady = 10, padx = 10)

        self.back_button = ttk.Button(self, text = "Back", command = lambda: controller.show_frame(InitialisePage))
        self.back_button.pack()




if __name__ == "__main__":
    app = Application()
    app.geometry("800x500")
    # app.title("Pressure Touch Music")
    app.mainloop()
    # print app.filepath
    # print app.padOn1 + app.padOn2
    # print padOn1 + padOn2 + padOn3 + padOn4 + padOn5 + padOn6
    # root = Tk()
    # root.title("Pressure Touch Music")
    # root.geometry("800x500")
    # app = InitialisePage(root)
    # root.mainloop()
