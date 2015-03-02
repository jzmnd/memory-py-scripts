# Memory testing python script
# Use with memory_test_v2.ino
# Jeremy Smith
# Version 1.0

import os, sys, time
import serial
import numpy as np
from myfunctions import dataOutput
from argparse import ArgumentParser

print "\n================================"
print "Memory test program"
print "Jeremy Smith"
print "Version 1.0"
print "Email: j-smith@eecs.berkeley.edu"
print "================================\n"

# Parse the variables
parser = ArgumentParser()
parser.add_argument('-p', '--program', default='1', choices=['1', '2', '3', '4', '5'], help="Program number ('1' = content addressable read, '2' = forming, '3' = write a zero, '4' = write a one, '5' = standard read)")
parser.add_argument('-w', '--wordl', default=0, type=int, choices=xrange(0,3), help="Word line number")
parser.add_argument('-b', '--bitl', default=0, type=int, choices=xrange(0,3), help="Bit line number")
parser.add_argument('-t', '--pattern', default=0b111, type=int, choices=xrange(0,8), help="Pattern data for bit lines as binary")
parser.add_argument('-r', '--rwtime', default=1, type=int, help="Read/write time in ms")
parser.add_argument('-f', '--fptime', default=200, type=int, help="Form/precharge time in ms")
args = vars(parser.parse_args())

# Path name for location of script
path = os.path.dirname(os.path.abspath(__file__))
print "Directory:", path

# Define constants
connected = False
serialport = '/dev/tty.usbmodem621'
v_ratio = 5.0/1023
time_step = 0.5
data_string = ""
voltage_data = []

print "Program number:", args['program']
print "Address: WL", args['wordl'], "  BL", args['bitl']
print "Data Pattern:", bin(args['pattern'])[2:]
print "Read/write time:", args['rwtime'], "ms"
print "Form/precharge time:", args['fptime'], "ms"
print '\n'

# Open the serial port that your Ardiono is connected to
try:
	ser = serial.Serial(serialport, 115200)
except OSError:
	print "Please Connect Arduino via USB\n"
	sys.exit()

# Loop until the Arduino tells us it is ready
print "Waiting to connect..."
while not connected:
	serin = ser.read()
	if serin == 'A':
		print "Connected to Arduino\n"
		connected = True

# Write the commands to the Arduino
time.sleep(1)
ser.write(args['program'])
ser.write(chr(args['wordl']))
ser.write(chr(args['bitl']))
ser.write(chr(args['pattern']))
ser.write(chr(args['rwtime']))
ser.write(chr(args['fptime']))

# Wait until the Arduino tells us it is finished
while connected:
	serin = ser.read()
	if serin == 'A':
		continue
	if serin == 'Z':
		connected = False
		continue
	sys.stdout.write(serin)   # Writes output from Arduino to the stdout
	data_string += serin    # Stores the Arduino output 

# Close the port
ser.close()

# Convert string from serial bus to a numpy array and output to "results/output.txt"
if len(data_string) is not 0:
	for i in [x.strip().split(',') for x in data_string.strip().split('\n')[3:]]:
		voltage_data.append([float(i[0])*time_step, float(i[1])*v_ratio])
	voltage_data = np.array(voltage_data)
	if len(voltage_data) is not 0:
		dataOutput("output.txt", path, voltage_data.T, format='%.1f\t %.4f\n')

print "DONE"

