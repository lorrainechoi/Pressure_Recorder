'''
Reads in data over a serial connection and plots the results live. Before closing, the data is saved to a .txt file.
'''

import serial
import matplotlib.pyplot as plt
import numpy as np
import win32com.client

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


plt.ion()                                   #sets plot to animation mode

window_size = 600                           # sets the duration of data shown
period = 100                                # period (in ms) between each message

pad1 = [0]*window_size
pad2 = [0]*window_size

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

    data = ser.readline()                   #reads until it gets a carriage return. MAKE SURE THERE IS A CARRIAGE RETURN OR IT READS FOREVER

    if counter == 0:
        data = ser.readline()

    # print data
    data = data.rstrip('\x00')
    # print data
    temp = data.split()                     #splits string into a list at the tabs
    # print temp

    pad1.append(int(temp[0]))               #add new value as int to current list
    pad2.append(int(temp[1]))

    pad1.pop(0)                             # remove head element
    pad2.pop(0)

    xline.set_xdata(np.arange(time_min, window_size/(1000/period), (float(period)/1000)))                   #sets xdata to new list length
    yline.set_xdata(np.arange(time_min, window_size/(1000/period), (float(period)/1000)))

    xline.set_ydata(pad1)                   #sets ydata to new list
    yline.set_ydata(pad2)

    plt.draw()                              #draws new plot

    plt.pause(0.000001)                     #in seconds
    counter = counter + 1

    if counter > window_size :
        time_min = time_min + (period/1000)
        plt.xlim(time_min, window_size/(1000/period)+(period/1000))
        # time.pop(0)
        # time.append(time[-1] + period/1000)






#rows = zip(x, y, z)                        #combines lists together
rows = zip(x, y)

row_arr = np.array(rows)                    #creates array from list

np.savetxt("C:\\Users\\USER\\Desktop\\Documents\\test_radio2.txt", row_arr) #save data in file (load w/np.loadtxt())

ser.close() #closes serial connection (very important to do this! if you have an error partway through the code, type this into the cmd line to close the connection)
