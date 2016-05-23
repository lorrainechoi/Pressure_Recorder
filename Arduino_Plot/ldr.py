'''
Reads in data over a serial connection and plots the results live. Before closing, the data is saved to a .txt file.
'''

import serial
import matplotlib.pyplot as plt
import numpy as np
import win32com.client                                  # for windows only
import rtmidi_python as rtmidi
# import Tkinter

# initialise variables
no_of_pads = 2                                          # number of connected touch pads
baud_rate = 115200                                      # baud rate from Arduino
window_size = 600                                       # sets the duration of data shown
period = 100                                            # period (in ms) between each message
connected = False
counter = 0
time_min = 0


# finds COM port that the Arduino is on (assumes only one Arduino is connected)
# for windows only
wmi = win32com.client.GetObject("winmgmts:")
for port in wmi.InstancesOf("Win32_SerialPort"):
    # print port.Name #port.DeviceID, port.Name
    if "Arduino" in port.Name:
        comPort = port.DeviceID
        # print comPort, "is Arduino"

ser = serial.Serial(comPort, baud_rate)                 # sets up serial connection (make sure baud rate is correct - matches Arduino)
while not connected:
    serin = ser.read()
    connected = True

# set up midi ports
midi_out = rtmidi.MidiOut()                             # search for available midi ports
# for port_name in midi_out.ports:
#     print port_name
midi_out.open_port(0)                                   # open midi port


# set up plot structure & parameters
plot_data = {}

for i in range(1, no_of_pads+1):
    plot_data["pad{0}".format(i)] = [0]*window_size

pad1_record = []
pad2_record = []
# pad3_record = []
# pad4_record = []
# pad5_record = []
# pad6_record = []

plt.ion()                                               # sets plot to animation mode

line1, = plt.plot(plot_data["pad1"])
line2, = plt.plot(plot_data["pad2"])
# line3, = plt.plot(plot_data["pad3"])
# line4, = plt.plot(plot_data["pad4"])
# line5, = plt.plot(plot_data["pad5"])
# line6, = plt.plot(plot_data["pad6"])

plt.ylim(0,1023)                                        # sets the y axis limits
plt.xlim(0, window_size/(1000/period))
plt.title("Arduino Reading")
plt.grid(True)
plt.legend([line1, line2], ['pad1', 'pad2'])
# plt.legend([line1, line2, line3, line4, line5, line6], ['pad1', 'pad2', 'pad3', 'pad4', 'pad5', 'pad6'])
plt.ylabel('Pressure (Pa)')
plt.xlabel('Time')

line1.set_xdata(np.arange(time_min, window_size/(1000/period), (float(period)/1000)))                   # initialise x axis data
line2.set_xdata(np.arange(time_min, window_size/(1000/period), (float(period)/1000)))
# line3.set_xdata(np.arange(time_min, window_size/(1000/period), (float(period)/1000)))
# line4.set_xdata(np.arange(time_min, window_size/(1000/period), (float(period)/1000)))
# line5.set_xdata(np.arange(time_min, window_size/(1000/period), (float(period)/1000)))
# line6.set_xdata(np.arange(time_min, window_size/(1000/period), (float(period)/1000)))

pad_active = [False]*no_of_pads
velocity = [0]*no_of_pads
instrument = [64, 64]                           # 64 = soprano sax
pitch = [60, 64]                                # note C & E
previous_pitch = [60, 64]

while True:
    while (ser.inWaiting() == 0):
        pass

    try:
        data = ser.readline()                   # reads until it gets a carriage return. MAKE SURE THERE IS A CARRIAGE RETURN OR IT READS FOREVER

        if counter == 0:
            data = ser.readline()

        data = data.rstrip('\x00')
        temp = data.split()                     # splits string into a list at the tabs

        for i in range(0, no_of_pads):
            colName = "pad" + str(i+1)
            plot_data[colName].append(int(temp[i]))                                     # append new pressure data to list (0-1023)
            plot_data[colName].pop(0)                                                   # remove first element from list

            velocity[i] = int(temp[i])/8                                                # vector of volume (0-127)
            # instrument[i] =
            # pitch[i] =

            if ((plot_data[colName][-1] > 0) & (pad_active[i] == False)):
                midi_out.send_message([0xC0 + i, instrument[i]])                        # use channel i
                midi_out.send_message([0x90 + i, pitch[i], velocity[i]])                # Note on
                pad_active[i] = True
                previous_pitch[i] = pitch[i]

            elif ((plot_data[colName][-1]  > 0) & (pad_active[i] == True)):
                midi_out.send_message([0xB0 + i, 0x07, velocity[i]])                    # change volume

            elif ((plot_data[colName][-1]  == 0) & (pad_active[i] == True)):
                midi_out.send_message([0x90 + i, previous_pitch[i], 0])                 # Note off
                pad_active[i] = False

            # print velocity
            # print pad_active

        pad1_record.append(int(temp[0]))        # for data logging
        pad2_record.append(int(temp[1]))
        # pad3_record.append(int(temp[2]))
        # pad4_record.append(int(temp[3]))
        # pad5_record.append(int(temp[4]))
        # pad6_record.append(int(temp[5]))

        line1.set_ydata(plot_data["pad1"])
        line2.set_ydata(plot_data["pad2"])
        # line3.set_ydata(plot_data["pad3"])
        # line4.set_ydata(plot_data["pad4"])
        # line5.set_ydata(plot_data["pad5"])
        # line6.set_ydata(plot_data["pad6"])

        plt.draw()                              #draws new plot
        plt.pause(0.000001)                     #in seconds


    except KeyboardInterrupt:
        # board.exit()
        rows = zip(pad1_record, pad2_record)
        # rows = zip(pad1_record, pad2_record, pad3_record, pad4_record, pad5_record, pad6_record)
        row_arr = np.array(rows)                    # creates array from list

        #save data in file (load w/np.loadtxt())
        np.savetxt("C:\\Users\\USER\\Desktop\\Documents\\test_file.txt", row_arr)
        ser.close() # closes serial connection (very important to do this! if you have an error partway through the code, type this into the cmd line to close the connection)
        break
