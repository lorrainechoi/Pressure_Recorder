Pressure recorder is a arduino-python synthesizer that records pressure from different touch pads and plot real-time pressure data on the computer locally. Volume of output sound is determined by the amount of pressure applied on touch pads.

# Prerequisites
1. You will need Python 2.7 installed on your system.
2. Run: `git clone https://github.com/lorrainechoi/Pressure_Recorder` to clone the repo and then `cd Pressure_recorder` to navigate into the directory
3. Install Arduino IDE and upload the `test_midi.ino` file to the board
4. Install Python dependencies: `numpy`, `matplotlib`, `serial`, `rtmidi_python`, `win32com`, `midiutil`, `py2exe`
  * numpy: `pip install numpy`
  * matplotlib: `pip install matplotlib`
  * serial: https://pypi.python.org/pypi/pyserial
  * rtmidi_python: https://pypi.python.org/pypi/rtmidi-python
  * midiutil: https://code.google.com/archive/p/midiutil/downloads
  * py2exe: https://sourceforge.net/projects/py2exe/files/py2exe/0.6.9/

# Hardware Equipment
* Arduino Uno board
* Pressure Touch Pads / Force Sensing Resistors (FSR)
* Resistors

# How to run this project (Software)
1. Connect Arduino to laptop through USB
2. Upload Arduino code to Arduino board
3. Open terminal, cd to `Pressure_Sensor` file and run script: `python gui_windows.py`
<!-- 4. ctrl+C to terminate python script -->


# Next Steps
* Calibrate y-axis
* Mac friendly version

# Done
* Check MIDI - try to link to garageband (need to open virtual port)
* Build GUI: add stop button & and save csv file with file path input from GUI
* Build pressure sensing touch-pads
* Add MUX for location change

# Cancelled
* Make touch pads to work wirelessly
