from Tkinter import *
from tkFileDialog import askopenfilename
import tkMessageBox
import ttk
import os
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
connected = False
ser = serial.Serial()
ser.baudrate = 60                                   # baud rate from Arduino

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
midi_out.open_port(0)

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

    # a.set_ylim(0,1023)                                        # sets the y axis limits
    a.set_ylim(0, 35)
    a.set_xlim(0, window_size/(1000/period))
    # a.set_title("Arduino Reading")
    # a.grid(True)

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

    a.set_ylabel('Force')
    a.set_xlabel('Time')



def animate(i):

    global lines, plot_data, pad1_record, pad2_record, pad_records


    force_mapping = {}
    force_mapping["force"] = [0, 1.08, 2.13, 3.28, 4.14, 5.04, 5.97, 6.9, 7.76, 8.51, 9.33, 10.04, 10.86, 11.64, 12.35, 13.1, 13.88, 14.48, 15.04, 15.45, 15.75, 16.12, 16.38, 16.68, 16.94, 17.2, 17.46, 17.8, 18.13, 18.47, 18.88, 19.4, 20, 20.52, 21.01, 21.68, 22.39, 23.02, 23.81, 24.55, 25, 25.6, 26.19, 26.94, 27.65, 28.4, 29.18, 29.85, 30.34]
    force_mapping["reading"] = [6.43, 15.01, 25.74, 36.46, 42.9, 49.33, 57.91, 64.34, 72.92, 83.65, 94.37, 98.66, 113.67, 128.69, 147.99, 169.44, 201.61, 231.64, 263.81, 298.12, 328.15, 368.9, 401.07, 433.24, 471.85, 499.73, 538.34, 572.65, 598.39, 624.13, 647.72, 671.31, 684.18, 694.91, 701.34, 709.92, 718.5, 724.93, 733.51, 742.09, 746.38, 752.82, 759.25, 765.68, 772.12, 780.7, 787.13, 793.57, 802.14]

    velocity_mapping = {}
    # velocity_mapping["force"] = np.arange(0, 31)
    # velocity_mapping["velocity"] = map(int, np.arange(0, 128, 4.233))
    velocity_mapping["force"] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
    velocity_mapping["velocity"] = [0, 4, 8, 13, 17, 21, 25, 30, 34, 38, 42, 47, 51, 55, 59, 64, 68, 72, 76, 80, 85, 89, 93, 97, 102, 106, 110, 114, 119, 123, 127]


    def force_mapping_func(myNumber):
        temp = min(force_mapping["reading"], key=lambda x:abs(x-int(myNumber)))
        tempIndex = force_mapping["reading"].index(temp)
        return force_mapping["force"][tempIndex]


    def velocity_mapping_func(myNumber):
        temp = min(velocity_mapping["force"], key=lambda x:abs(x-int(myNumber)))
        tempIndex = velocity_mapping["force"].index(temp)
        return velocity_mapping["velocity"][tempIndex]

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

        # plot_data[colName].append(int(temp[padLocation]))
        plot_data[colName].append(force_mapping_func(int(temp[padLocation])))                                     # append new pressure data to list (0-1023)
        plot_data[colName].pop(0)                                                   # remove first element from list
        # velocity[i] = int(temp[padLocation])/8
        velocity[i] = velocity_mapping_func(force_mapping_func(int(temp[padLocation])))
        lines["line{0}".format(i+1)][0].set_ydata((plot_data["pad{0}".format(i+1)]))
        # pad_records["pad{0}".format(i+1)].append(int(temp[padLocation]))
        pad_records["pad{0}".format(i+1)].append(force_mapping_func(int(temp[padLocation])))

        if ((plot_data[colName][-1] > 0) & (pad_active[i] == False)):
            midi_out.send_message([0xC0 + i, instrument[i]])                        # use channel i
            midi_out.send_message([0x90 + i, pitch[i], velocity[i]])                # Note on
            pad_active[i] = True
            print "play"

        elif ((plot_data[colName][-1]  > 0) & (pad_active[i] == True)):
            midi_out.send_message([0xB0 + i, 0x07, velocity[i]])                    # change volume
            # print "vol"
        elif ((plot_data[colName][-1]  == 0) & (pad_active[i] == True)):
            midi_out.send_message([0x90 + i, pitch[i], 0])                 # Note off
            pad_active[i] = False

    # for i in range(0, total_pads):
    #     # pad_records["pad{0}".format(i+1)].append = int(temp[i])
    #     lines["line{0}".format(i+1)][0].set_ydata((plot_data["pad{0}".format(i+1)]))

    # plt.draw()
    # plt.pause(0.01)
    a.plot()


    print temp




class Application(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        global ser
        global connected
        # print str(ser.port) + " " + str(connected)

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
            # print str(ser.port) + " " + str(connected)
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
