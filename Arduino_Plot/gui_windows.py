from Tkinter import *
from tkFileDialog import askopenfilename
import os
import ttk
# import time
from time import gmtime, strftime
import serial
import numpy as np
import win32com.client                                  # for windows only
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import rtmidi_python as rtmidi


# initialise: total no. of available pads & locations
style.use("ggplot")
total_location = 12
total_pads = 6
no_of_pads = 2
window_size = 600                                       # sets the duration of data shown
period = 200                                            # period (in ms) between each message

# initialise serial ports
global ser
global connected
connected = False
ser = serial.Serial()
ser.baudrate = 10                                   # baud rate from Arduino

# initialise plot variables
global line1, line2, line3, line4, line5, line6
plot_data = {}
pad1_record = []
pad2_record = []
pad3_record = []
pad4_record = []
pad5_record = []
pad6_record = []
velocity = [0]*total_pads
pad_active = [False]*total_pads
velocity = [0]*total_pads
instrument = [0]*total_pads                             # 64 = soprano sax
pitch = [60]*total_pads                                 # note C & E
# previous_pitch = [60, 64]

# set up midi ports
midi_out = rtmidi.MidiOut()                             # search for available midi ports
midi_out.open_port(0)

# set up plot structure & parameters
f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)


def init_plot():

    global line1, line2, line3, line4, line5, line6
    time_min = 0

    for i in range(1, total_pads+1):
        plot_data["pad{0}".format(i)] = [0]*window_size

    line1, = a.plot(plot_data["pad1"])
    line2, = a.plot(plot_data["pad2"])
    line3, = a.plot(plot_data["pad3"])
    line4, = a.plot(plot_data["pad4"])
    line5, = a.plot(plot_data["pad5"])
    line6, = a.plot(plot_data["pad6"])

    a.set_ylim(0,1023)                                        # sets the y axis limits
    a.set_xlim(0, window_size/(1000/period))
    # a.set_title("Arduino Reading")
    # a.grid(True)
    # a.legend([line1, line2], ['pad1', 'pad2'])

    if no_of_pads == 2:
        a.legend([line1, line2], ['pad1', 'pad2'])
    elif no_of_pads == 3:
        a.legend([line1, line2, line3], ['pad1', 'pad2', 'pad3'])
    elif no_of_pads == 4:
        a.legend([line1, line2, line3, line4], ['pad1', 'pad2', 'pad3', 'pad4'])
    elif no_of_pads == 5:
        a.legend([line1, line2, line3, line4, line5], ['pad1', 'pad2', 'pad3', 'pad4', 'pad5'])
    elif no_of_pads == 6:
        a.legend([line1, line2, line3, line4, line5, line6], ['pad1', 'pad2', 'pad3', 'pad4', 'pad5', 'pad6'])

    a.set_ylabel('Pressure')
    a.set_xlabel('Time')

    line1.set_xdata(np.arange(time_min, window_size/(1000/period), (float(period)/1000)))                   # initialise x axis data
    line2.set_xdata(np.arange(time_min, window_size/(1000/period), (float(period)/1000)))
    line3.set_xdata(np.arange(time_min, window_size/(1000/period), (float(period)/1000)))
    line4.set_xdata(np.arange(time_min, window_size/(1000/period), (float(period)/1000)))
    line5.set_xdata(np.arange(time_min, window_size/(1000/period), (float(period)/1000)))
    line6.set_xdata(np.arange(time_min, window_size/(1000/period), (float(period)/1000)))



def animate(i):

    global line1, line2, line3, line4, line5, line6, plot_data, pad1_record, pad2_record

    if connected:
        try:
            data = ser.readline()
            data = data.rstrip('\x00')
            temp = data.split()
            if len(temp) < no_of_pads:
                temp = [0]*no_of_pads

            if no_of_pads < total_pads:
                zero_pad = [0]*(total_pads-no_of_pads)
                temp.extend(zero_pad)

            for i in range(0, total_pads):
                colName = "pad" + str(i+1)
                plot_data[colName].append(int(temp[i]))                                     # append new pressure data to list (0-1023)
                plot_data[colName].pop(0)                                                   # remove first element from list

                velocity[i] = int(temp[i])/8

                if ((plot_data[colNacd ][-1] > 0) & (pad_active[i] == False)):
                    midi_out.send_message([0xC0 + i, instrument[i]])                        # use channel i
                    midi_out.send_message([0x90 + i, pitch[i], velocity[i]])                # Note on
                    pad_active[i] = True
                    # previous_pitch[i] = pitch[i]
                    print "play"

                elif ((plot_data[colName][-1]  > 0) & (pad_active[i] == True)):
                    midi_out.send_message([0xB0 + i, 0x07, velocity[i]])                    # change volume
                    print "vol"
                elif ((plot_data[colName][-1]  == 0) & (pad_active[i] == True)):
                    midi_out.send_message([0x90 + i, pitch[i], 0])                 # Note off
                    pad_active[i] = False


            pad1_record.append(int(temp[0]))        # for data logging
            pad2_record.append(int(temp[1]))
            pad3_record.append(int(temp[2]))
            pad4_record.append(int(temp[3]))
            pad5_record.append(int(temp[4]))
            pad6_record.append(int(temp[5]))

            line1.set_ydata(plot_data["pad1"])
            line2.set_ydata(plot_data["pad2"])
            line3.set_ydata(plot_data["pad3"])
            line4.set_ydata(plot_data["pad4"])
            line5.set_ydata(plot_data["pad5"])
            line6.set_ydata(plot_data["pad6"])

            plt.draw()
            plt.pause(0.01)

        except serial.SerialException:
            print "not connected"

    else:
        temp = [0]*total_pads
        line1.set_ydata(plot_data["pad1"])
        line2.set_ydata(plot_data["pad2"])
        line3.set_ydata(plot_data["pad3"])
        line4.set_ydata(plot_data["pad4"])
        line5.set_ydata(plot_data["pad5"])
        line6.set_ydata(plot_data["pad6"])
        plt.draw()
        plt.pause(0.05)

    print temp




class Application(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        global ser
        global connected
        print str(ser.port) + " " + str(connected)

        # Tk.iconbitmap(self, default = "icon.ico")
        Tk.wm_title(self, "Pressure Touch Music")

        container = Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        container.padOn = {}
        container.padPitch = {}
        container.padInstrument = {}
        container.padLocation = {}
        container.saveFilePath = ''
        # container.comPort = StringVar()
        # container.connected = BooleanVar()
        # container.connected = False

        for i in range(1, total_pads+1):
            container.padOn["pad{0}".format(i)] = BooleanVar()
            container.padPitch["pad{0}".format(i)] = StringVar()
            container.padInstrument["pad{0}".format(i)] = StringVar()
            container.padLocation["pad{0}".format(i)] = IntVar()

        self.frames = {}

        for F in (InitialisePage, PlotPage):
            frame = F(container, self)
            # ser.port = container.comPort.get()
            # connected = container.connected
            print str(ser.port) + " " + str(connected)
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

        self.create_header_row()
        self.create_pad_checkbox(master)
        self.create_pitch_list(master)
        self.create_instrument_list(master)
        self.create_location_list(master)
        self.create_browse_button()
        self.create_connect_button(master)
        self.create_confirm_button(master, controller)


    def create_header_row(self):
        """Create header row"""
        colNames = ["Pitch", "Instrument", "Location"]

        for i in range(0, 3):
            column1_label = ttk.Label(self, text = colNames[i], font = ("", "10", "bold"))
            column1_label.grid(row = 1, column = 1+i)


    def create_pad_checkbox(self, master):
        """Create checkbox to indicate active pads"""
        for i in range(1, total_pads+1):
            colName = "pad" + str(i)
            buttonName = "Pad " + str(i)
            pad_check_button = ttk.Checkbutton(self, text = buttonName, variable = master.padOn[colName], onvalue = True, offvalue = False)
            pad_check_button.grid(row = i+1, column = 0, sticky = 'E')


    def create_pitch_list(self, master):
        """Create dropdown list for pitch selection"""
        pitch = ["C", "D", "E", "F", "G", "A", "B", "C'"]

        for i in range(1, total_pads+1):
            colName = "pad" + str(i)
            pad_pitch_list = ttk.OptionMenu(self, master.padPitch[colName], *pitch)
            pad_pitch_list.grid(row = i+1, column = 1, sticky = 'EW')


    def create_instrument_list(self, master):
        """Create instrument selection list per pad"""
        instrument = ["Piano", "Violin", "Flute", "Trumpet", "Xylophone", "Cymbals"]        # [0, 40, 73, 56, 13, 119]

        for i in range(1, total_pads+1):
            colName = "pad" + str(i)
            pad_instrument_list = ttk.OptionMenu(self, master.padInstrument[colName], *instrument)
            pad_instrument_list.grid(row = i+1, column = 2, sticky = 'EW')


    def create_location_list(self, master):
        """Create pad location selection list"""
        location = range(1,13)

        for i in range(1, total_pads+1):
            colName = "pad" + str(i)
            pad_location_list = ttk.OptionMenu(self, master.padLocation[colName], *location)
            pad_location_list.grid(row = i+1, column = 3, sticky = 'EW')


    def create_browse_button(self):
        self.filepath = StringVar()
        self.filename = StringVar()
        self.filename.set(str(strftime("%d-%m-%Y_%H%M", gmtime())) + '.csv')
        # print self.filename.get()

        """Create Browse Button"""
        browse_label = ttk.Label(self, text = "Save csv file in:")
        browse_label.grid(row = 9, column = 0, sticky = 'E', padx = 5, pady = 4)
        self.browse_filepath = ttk.Entry(self, textvariable = self.filepath)
        self.browse_filepath.grid(row = 9, column = 1, sticky = 'EW', columnspan = 3)
        browse_button = ttk.Button(self, text = "Browse", command = self.askopenfile)
        browse_button.grid(row = 9, column = 4, padx = 5, sticky = 'W')

        filename_label = ttk.Label(self, text = "Csv filename:")
        filename_label.grid(row = 10, column = 0, sticky = 'E', padx = 5, pady = 4)
        self.saveFileName = ttk.Entry(self, textvariable = self.filename)
        self.saveFileName.grid(row = 10, column = 1, sticky = 'EW', columnspan = 3)


    def askopenfile(self):
        """ Method to locate file path and display in entry box """
        filename = askopenfilename()
        self.filepath = os.path.dirname(filename)
        self.browse_filepath.delete(0, END)
        self.browse_filepath.insert(0, self.filepath)


    def create_connect_button(self, master):
        self.comPort = StringVar()

        self.find_com_port(master)
        global connected

        showComPortLabel = ttk.Label(self, text = "Arduino COM port:")
        showComPortLabel.grid(row = 11, column = 0, sticky = 'E', padx = 5, pady = 4)
        showComPort = ttk.Entry(self, textvariable = self.comPort)
        showComPort.grid(row = 11, column = 1, sticky = 'EW', columnspan = 3)

        connectButton = ttk.Button(self, text = "Connect", command = self.connect_arduino_windows)
        connectButton.grid(row = 11, column = 4, padx = 5, sticky = 'W')


    def find_com_port(self, master):
        # finds COM port that the Arduino is on (assumes only one Arduino is connected)
        wmi = win32com.client.GetObject("winmgmts:")
        for port in wmi.InstancesOf("Win32_SerialPort"):
            if "Arduino" in port.Name:
                self.comPort.set(str(port.DeviceID))


    def connect_arduino_windows(self):
        global ser
        global connected
        # print ser
        # print connected
        try:
            ser.port = self.comPort.get()
            # print ser
            ser.open()                                       # sets up serial connection (make sure baud rate is correct - matches Arduino)
            # print ser
            if not connected:
                serin = ser.read()
                connected = True
                # print connected
                connectedMsg = ttk.Label(self, text = "Connected to Arduino!                   ")
                connectedMsg.grid(row = 12, column = 1, sticky = 'W', columnspan = 3)
        except serial.SerialException:
            connected = False
            # print connected
            connectedMsg = ttk.Label(self, text = "Failed to connect to Arduino")
            connectedMsg.grid(row = 12, column = 1, sticky = 'W', columnspan = 3)


    def create_confirm_button(self, master, controller):
        def callback():
            master.saveFilePath = self.browse_filepath.get() + "/" + self.saveFileName.get()
            # master.test_const.set('clicked')
            # print test_const.get()
            controller.show_frame(PlotPage)

        confirm_button = ttk.Button(self, text = "Confirm", command = callback)
        confirm_button.grid(row = 13, column = 0, columnspan = 5)



class PlotPage(Frame):

    def __init__(self, master, controller):
        global ser
        Frame.__init__(self, master)
        self.title = ttk.Label(self, text = "Pressure Reading from Pads")
        self.title.pack(pady = 10, padx = 10)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)

        # toolbar = NavigationToolbar2TkAgg(canvas, self)
        # toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)



if __name__ == "__main__":
    app = Application()
    app.geometry("800x500")
    ani = animation.FuncAnimation(f, func = animate, init_func = init_plot, interval=50)
    app.mainloop()
