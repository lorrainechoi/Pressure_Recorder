'''
Reads in data over a serial connection and plots the results live. Before closing, the data is saved to a .txt file.
'''

import serial
import matplotlib.pyplot as plt
import numpy as np
import win32com.client
import rtmidi_python as rtmidi
# import Tkinter


connected = False

#finds COM port that the Arduino is on (assumes only one Arduino is connected)
wmi = win32com.client.GetObject("winmgmts:")
for port in wmi.InstancesOf("Win32_SerialPort"):
    #print port.Name #port.DeviceID, port.Name
    if "Arduino" in port.Name:
        comPort = port.DeviceID
        print comPort, "is Arduino"

ser = serial.Serial(comPort, 9600)          #sets up serial connection (make sure baud rate is correct - matches Arduino)

while not connected:
    serin = ser.read()
    connected = True


midi_out = rtmidi.MidiOut()
midi_out.open_port(0)


plt.ion()                                   #sets plot to animation mode

window_size = 600                           # sets the duration of data shown
period = 100                                # period (in ms) between each message

pad1 = [0]*window_size
pad2 = [0]*window_size

pad1_record = []
pad2_record = []

xline, = plt.plot(pad1)
yline, = plt.plot(pad2)

plt.ylim(0,1023)                            #sets the y axis limits
plt.xlim(0, window_size/(1000/period))
# plt.title("Arduino Reading")
# plt.grid(True)
plt.legend(loc='upper left')
plt.ylabel('Pressure (Pa)')
plt.xlabel('Time')

counter = 0
time_min = 0
# time = [x*(window_size/1000) for x in range(0, window_size)]


while True:                                 #while you are taking data
    while (ser.inWaiting() == 0):
        pass

    try:
        data = ser.readline()                   #reads until it gets a carriage return. MAKE SURE THERE IS A CARRIAGE RETURN OR IT READS FOREVER

        if counter == 0:
            data = ser.readline()

        data = data.rstrip('\x00')
        temp = data.split()                     #splits string into a list at the tabs

        pad1.append(int(temp[0]))               # add new value as int to current list
        pad2.append(int(temp[1]))

        pad1_record.append(int(temp[0]))        # for data logging
        pad2_record.append(int(temp[1]))

        pad1.pop(0)                             # remove head element
        pad2.pop(0)

        if pad1[-1] > 0:
            midi_out.send_message([0x90, 60, (pad1[-1]/4)]) # Note on; pitch = C (60)
        else:
            midi_out.send_message([0x80, 60, (pad1[-2]/4)]) # Note off

        if pad2[-1] > 0:
            midi_out.send_message([0x90, 64, (pad2[-1]/4)]) # Note on ; pitch = E (64)
        else:
            midi_out.send_message([0x80, 64, (pad2[-2]/4)]) # Note off


        xline.set_xdata(np.arange(time_min, window_size/(1000/period), (float(period)/1000)))                   #sets xdata to new list length
        yline.set_xdata(np.arange(time_min, window_size/(1000/period), (float(period)/1000)))

        xline.set_ydata(pad1)                   #sets ydata to new list
        yline.set_ydata(pad2)

        plt.draw()                              #draws new plot

        plt.pause(0.000001)                     #in seconds


    except KeyboardInterrupt:
        # board.exit()
        rows = zip(pad1_record, pad2_record)
        row_arr = np.array(rows)                    #creates array from list

        #save data in file (load w/np.loadtxt())
        np.savetxt("C:\\Users\\USER\\Desktop\\Documents\\test_file.txt", row_arr)
        ser.close() #closes serial connection (very important to do this! if you have an error partway through the code, type this into the cmd line to close the connection)
        break
