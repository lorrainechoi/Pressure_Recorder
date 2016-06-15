from Tkinter import *
from tkFileDialog import askopenfilename
import tkMessageBox
import ttk
import os
from time import gmtime, strftime
import serial
import numpy as np
import glob
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import rtmidi_python as rtmidi
from midiutil.MidiFile import MIDIFile


# initialise: total no. of available pads & locations
style.use("ggplot")
total_location = 12
total_pads = 6
# no_of_pads = 2
window_size = 600                                       # sets the duration of data shown
period = 200                                            # period (in ms) between each message

# initialise serial ports
global ser
global connected
global baudrate
baudrate = 60
connected = False
ser = serial.Serial()
ser.baudrate = baudrate                                   # baud rate from Arduino

# initialise plot variables
global instrument, pitch, no_of_pads, location
global lines, pad_records
lines = {}
plot_data = {}
pad_records = {}
velocity = [0]*total_pads
pad_active = [False]*total_pads
velocity = [0]*total_pads
instrument = [40]*total_pads                             # 40 = violin
no_of_pads = 0
pitch = [60]*total_pads                                 # note C
location = [0]*total_pads

for i in range(1, total_pads+1):
    pad_records["pad{0}".format(i)] = []

# set up midi ports
midi_out = rtmidi.MidiOut()                             # search for available midi ports
midi_out.midiout.open_virtual_port("Virtual Port")

# set up plot structure & parameters
f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)


def init_plot():

    global lines
    time_min = 0

    for i in range(1, total_pads+1):
        plot_data["pad{0}".format(i)] = [0]*window_size
        lines["line{0}".format(i)] = a.plot(plot_data["pad{0}".format(i)])
        lines["line{0}".format(i)][0].set_xdata(np.arange(time_min, window_size/(1000/period), (float(period)/1000)))
        # lines["line{0}".format(i+1)][0].set_ydata((plot_data["pad{0}".format(i+1)]))

    a.set_ylim(0,1023)                                        # sets the y axis limits
    a.set_xlim(0, window_size/(1000/period))
    # a.set_title("Arduino Reading")
    # a.grid(True)

    # if no_of_pads == 2:
    #     a.legend([line1, line2], ['pad1', 'pad2'])
    # elif no_of_pads == 3:
    #     a.legend([line1, line2, line3], ['pad1', 'pad2', 'pad3'])
    # elif no_of_pads == 4:
    #     a.legend([line1, line2, line3, line4], ['pad1', 'pad2', 'pad3', 'pad4'])
    # elif no_of_pads == 5:
    #     a.legend([line1, line2, line3, line4, line5], ['pad1', 'pad2', 'pad3', 'pad4', 'pad5'])
    # elif no_of_pads == 6:
    #     a.legend([line1, line2, line3, line4, line5, line6], ['pad1', 'pad2', 'pad3', 'pad4', 'pad5', 'pad6'])

    a.set_ylabel('Pressure')
    a.set_xlabel('Time')



def animate(i):

    global lines, plot_data, pad1_record, pad2_record, pad_records

    if connected:
        try:
            data = ser.readline()
            data = data.rstrip('\x00')
            temp = data.split()
            if len(temp) < total_location:
                temp = [0]*total_location

            # if no_of_pads < total_pads:
            #     zero_pad = [0]*(total_pads-no_of_pads)
            #     temp.extend(zero_pad)

        except serial.SerialException:
            print "not connected"

    else:
        temp = [0]*total_location


    for i in range(0, total_pads):
        colName = "pad" + str(i+1)
        padLocation = location[i]-1
        if padLocation == -1:
            continue

        plot_data[colName].append(int(temp[padLocation]))                                     # append new pressure data to list (0-1023)
        plot_data[colName].pop(0)                                                   # remove first element from list
        velocity[i] = int(temp[padLocation])/8
        lines["line{0}".format(i+1)][0].set_ydata((plot_data["pad{0}".format(i+1)]))
        pad_records["pad{0}".format(i+1)].append(int(temp[padLocation]))

        if ((plot_data[colName][-1] > 0) & (pad_active[i] == False)):
            midi_out.send_message([0xC0 + i, instrument[i]])                        # use channel i
            midi_out.send_message([0x90 + i, pitch[i], velocity[i]])                # Note on
            pad_active[i] = True
            # print "play"

        elif ((plot_data[colName][-1]  > 0) & (pad_active[i] == True)):
            midi_out.send_message([0xB0 + i, 0x07, velocity[i]])                    # change volume
            # print "vol"
        elif ((plot_data[colName][-1]  == 0) & (pad_active[i] == True)):
            midi_out.send_message([0x90 + i, pitch[i], 0])                 # Note off
            pad_active[i] = False

    a.plot()


    # print temp




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

        # container.padLocation = {}
        container.saveFilePath = ''

        # for i in range(1, total_pads+1):
        #     container.padLocation["pad{0}".format(i)] = IntVar()

        self.frames = {}

        for F in (InitialisePage, PlotPage):
            frame = F(container, self)
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

        self.padInstrument = {}
        self.padPitch = {}
        self.padOn = {}
        self.padLocation = {}

        for i in range(1, total_pads+1):
            self.padInstrument["pad{0}".format(i)] = StringVar()
            self.padPitch["pad{0}".format(i)] = StringVar()
            self.padOn["pad{0}".format(i)] = BooleanVar()
            # self.padLocation["pad{0}".format(i)] = StringVar()
            self.padLocation["pad{0}".format(i)] = IntVar()

        self.instrument_selection = {}
        self.instrument_selection["instrument"] = [" ", "Violin", "Flute", "Trumpet"]
        self.instrument_selection["index"] = [0, 40, 73, 56]

        self.pitch_selection = {}
        self.pitch_selection["pitch"] = [" ","C", "D", "E", "F", "G", "A", "B", "C'"]
        self.pitch_selection["index"] = [0, 60, 62, 64, 65, 67, 69, 71, 72]

        self.create_header_row()
        self.create_pad_checkbox()
        self.create_pitch_list()
        self.create_instrument_list()
        self.create_location_list()
        # self.create_browse_button()
        self.create_connect_button(master)
        self.create_confirm_button(master, controller)


    def create_header_row(self):
        """Create header row"""
        colNames = ["Pitch", "Instrument", "Location"]

        for i in range(0, 3):
            column1_label = ttk.Label(self, text = colNames[i], font = ("", "10", "bold"))
            column1_label.grid(row = 1, column = 1+i)


    def create_pad_checkbox(self):
        """Create checkbox to indicate active pads"""
        for i in range(1, total_pads+1):
            colName = "pad" + str(i)
            buttonName = "Pad " + str(i)
            pad_check_button = ttk.Checkbutton(self, text = buttonName, variable = self.padOn[colName], onvalue = True, offvalue = False)
            pad_check_button.grid(row = i+1, column = 0, sticky = 'E')


    def create_pitch_list(self):
        """Create dropdown list for pitch selection"""
        for i in range(1, total_pads+1):
            colName = "pad" + str(i)
            pad_pitch_list = ttk.OptionMenu(self, self.padPitch[colName], *self.pitch_selection["pitch"])
            pad_pitch_list.grid(row = i+1, column = 1, sticky = 'EW')


    def create_instrument_list(self):
        """Create instrument selection list per pad"""
        for i in range(1, total_pads+1):
            colName = "pad" + str(i)
            pad_instrument_list = ttk.OptionMenu(self, self.padInstrument[colName], *self.instrument_selection["instrument"])
            pad_instrument_list.grid(row = i+1, column = 2, sticky = 'EW')


    def create_location_list(self):
        """Create pad location selection list"""
        # location = [" "]
        # location.append(str(range(1,total_location+1)))
        location = range(1,total_location+1)


        for i in range(1, total_pads+1):
            colName = "pad" + str(i)
            pad_location_list = ttk.OptionMenu(self, self.padLocation[colName], " ", *location)
            pad_location_list.grid(row = i+1, column = 3, sticky = 'EW')


    def create_browse_button(self):
        self.filepath = StringVar()
        self.filename = StringVar()
        self.filename.set(str(strftime("%d-%m-%Y_%H%M", gmtime())) + '.mid')
        # print self.filename.get()

        """Create Browse Button"""
        browse_label = ttk.Label(self, text = "Save csv file in:")
        browse_label.grid(row = 9, column = 0, sticky = 'E', padx = 5, pady = 4)
        self.browse_filepath = ttk.Entry(self, textvariable = self.filepath)
        self.browse_filepath.grid(row = 9, column = 1, sticky = 'EW', columnspan = 3)
        browse_button = ttk.Button(self, text = "Browse", command = self.askopenfile)
        browse_button.grid(row = 9, column = 4, padx = 5, sticky = 'W')

        filename_label = ttk.Label(self, text = "MIDI filename:")
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
        global baudrate
        ports = glob.glob('/dev/tty.*')
        result = []
        for port in ports:
            try:
                s = serial.Serial(port, baudrate)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass

        if len(result) == 1:
            self.comPort.set(str(result[0]))


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
                # serin = ser.read()
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
            # master.saveFilePath = self.browse_filepath.get() + "/" + self.saveFileName.get()
            global instrument, pitch, no_of_pads

            no_of_pads = 0

            for i in range(0, total_pads):
                colName = "pad" + str(i+1)
                tempIndex = self.instrument_selection["instrument"].index(self.padInstrument[colName].get())
                instrument[i] = self.instrument_selection["index"][tempIndex]
                tempIndex = self.pitch_selection["pitch"].index(self.padPitch[colName].get())
                pitch[i] = self.pitch_selection["index"][tempIndex]
                # if self.padLocation[colName].get() != " ":
                #     location[i] = self.padLocation[colName].get()
                try:
                    location[i] = self.padLocation[colName].get()
                except:
                    continue

                if(self.padOn[colName].get()):
                    no_of_pads = no_of_pads + 1

            controller.show_frame(PlotPage)

        confirm_button = ttk.Button(self, text = "Confirm", command = callback)
        confirm_button.grid(row = 13, column = 0, columnspan = 5)



class PlotPage(Frame):

    def __init__(self, master, controller):

        def onClick(event):
            global pause
            pause ^= True

        global ser, instrument

        Frame.__init__(self, master)

        self.graphframe = Frame(self)
        self.graphframe.pack(side = TOP, fill=BOTH, expand=True)
        self.filenameframe = Frame(self)
        self.filenameframe.pack(side = BOTTOM, fill=BOTH, pady = 10)
        self.browseframe = Frame(self)
        self.browseframe.pack(side = BOTTOM, fill=BOTH, pady = 10)

        self.title = ttk.Label(self.graphframe, text = "Pressure Reading from Pads", font = ("", "14", "bold"))
        self.title.pack(pady = 10, padx = 10)


        # figure window
        canvas = FigureCanvasTkAgg(f, self.graphframe)
        canvas.show()
        canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
        canvas.mpl_connect('button_press_event', onClick)

        toolbar = NavigationToolbar2TkAgg(canvas, self.graphframe)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)

        self.filepath = StringVar()
        self.filename = StringVar()

        self.filename.set(str(strftime("%d-%m-%Y_%H%M", gmtime())) + '.mid')

        browse_label = ttk.Label(self.browseframe, text = "Save MIDI file in:")
        browse_label.pack(side = LEFT, fill=Y, padx = 5)
        self.browse_filepath = ttk.Entry(self.browseframe, textvariable = self.filepath)
        self.browse_filepath.pack(side = LEFT, fill=X, expand=True, padx = 5)
        browse_button = ttk.Button(self.browseframe, text = "Browse", command = self.askopenfile)
        browse_button.pack(side = LEFT, fill=BOTH, padx = 5)

        filename_label = ttk.Label(self.filenameframe, text = "MIDI filename:")
        filename_label.pack(side = LEFT, fill=Y, padx = 5)
        self.saveFileName = ttk.Entry(self.filenameframe, textvariable = self.filename)
        self.saveFileName.pack(side = LEFT, fill=X, expand=True, padx = 5)
        browse_button = ttk.Button(self.filenameframe, text = "Save", command = self.savefile)
        browse_button.pack(side = LEFT, fill=BOTH, padx = 5)


    def askopenfile(self):
        """ Method to locate file path and display in entry box """
        filename = askopenfilename()
        self.filepath = os.path.dirname(filename)
        self.browse_filepath.delete(0, END)
        self.browse_filepath.insert(0, self.filepath)



    def savefile(self):
        """Construct MIDI file and save"""
        global pad_records, instrument, pitch

        MyMIDI = MIDIFile(1)
        MyMIDI.addTempo(0, 0, 600)

        for i in range(0, total_pads):
            pad_active = False
            list_length = len(pad_records["pad{0}".format(i+1)])
            MyMIDI.addProgramChange(0, i, 0, instrument[i])                            # set channel instrument
            for j in range(0, list_length):
                velocity = pad_records["pad{0}".format(i+1)][j]/8
                if not pad_active and (velocity > 0):
                    MyMIDI.addNote(0, i, 60, 0, list_length-j, velocity)               # add note if velocity > 0 and pad not on
                    pad_active = True
                elif pad_active:
                    MyMIDI.addControllerEvent(0, i, j, 0x07, velocity)                 # change volume
                    if velocity == 0:
                        pad_active = False


        filename = self.browse_filepath.get() + "/" + self.saveFileName.get()
        try:
            binfile = open(filename, 'wb')
            MyMIDI.writeFile(binfile)
            binfile.close()
            # print "saved"
            tkMessageBox.showinfo(
                " ",
                "Saved MIDI file"
            )
        except:
            tkMessageBox.showerror(
                "Error",
                "Cannot save MIDI file"
            )










if __name__ == "__main__":
    app = Application()
    app.geometry("1600x800")
    ani = animation.FuncAnimation(f, func = animate, init_func = init_plot, interval=50)
    app.mainloop()
    # global instrument
    # print no_of_pads
    # print instrument
    # print pitch
