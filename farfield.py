# lifetime test plotting

import serial
import matplotlib.pyplot as plt
import pandas as pd
import statistics
import sys

from os import path

class ArduinoInterface:

    def __init__(self, interface):
        self.port = serial.Serial(interface)
        self.port.flushInput()

    def update(self):
        '''
        expect line to be 'angle, voltage'
        '''

        data = self.port.readline()
        print(data)

        try:
            datastring = data[0:len(data)-2].decode('utf-8')
            values = datastring.split(",")
            if len(values) != 2: return 0
            values_float = []
            for value in values: values_float.append(float(value))
            return values_float
        except:
            print("Received malformed data") # or any other error
            return 0

class LEDScan:

    def __init__(self, filename = 0):
        self.data = {} # dictionary of lists for each data point
        self.filename = filename
        if filename != 0:
            f = open(filename, "r")
            lines = []
            for line in f:
                linedata = line.split("\n")[0].split(",")[1:]
                linedata_float = []
                for el in linedata: linedata_float.append(float(el))
                lines.append(linedata_float)

            f.close()
            cols = list(zip(*lines[::-1]))
            cols_reversed = []
            for el in cols: cols_reversed.append(el[::-1])

            for el in cols_reversed: self.data[el[0]] = el[1:]

    def addpoint(self, data):

        if self.data == 0: return

        angle, voltage = data
        #print("adding to list",angle,voltage)

        if angle in self.data.keys():
            self.data[angle].append(voltage)
        else:
            self.data[angle] = [voltage]

    def tocsv(self):

        for el in self.data.keys():
            print(el, self.data[el])

        dataframe = pd.DataFrame.from_dict(self.data)

        index = 0
        while path.exists("farfield_"+str(index)+".csv"):
            index += 1

        dataframe.to_csv("farfield_"+str(index)+".csv");

    def plot(self):

        xvals = []
        yvals = []
        yvals_stdev = []

        for angle in self.data.keys():
            xvals.append(angle)
            voltages = self.data[angle]
            yvals.append(statistics.mean(voltages))
            if len(voltages) > 2: yvals_stdev.append(statistics.stdev(voltages))
            else: yvals_stdev.append(0)


        plt.figure(figsize=(15,10))
        plt.errorbar(xvals, yvals, yvals_stdev, fmt='none', color='black', alpha=0.5)
        plt.scatter(xvals, yvals, marker="_")
        if self.filename == 0: plt.title("farfield test: last scan")
        else: plt.title("farfield test: " + self.filename)
        plt.xlabel("angle (deg)")
        plt.ylabel("intensity (V)")
        plt.grid()
        plt.show()


# stuff that runs

scanendmarker = 0

if len(sys.argv) == 2: # where we just scan, this defines num passes

    arduino = ArduinoInterface("/dev/ttyACM0")
    scanner = LEDScan()

    numdesiredpasses   = int(sys.argv[1])
    numcompletedpasses = 0

    lastval = scanendmarker+1

    print("waiting for next pass...")
    while lastval != scanendmarker:
        data = arduino.update()

        if type(data) != int:
            lastval = data[0]

    print("starting sampling")
    while numdesiredpasses > numcompletedpasses:

        data = arduino.update()

        if type(data) != int:
            if data[0] == scanendmarker:
                numcompletedpasses += 1
                print("completed",numcompletedpasses,"passes")
            scanner.addpoint(data)

    scanner.tocsv()
    scanner.plot()

elif len(sys.argv) == 3: # where we plot. expect <script>.py plot <filename>

    plotter = LEDScan(sys.argv[2])
    plotter.plot()

else:
    print("usage:\nfarfield.py <numpasses> to scan numpasses times over angles set in Arduino script\nfarfield.py plot <filename> to plot a specific file")



