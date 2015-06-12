#! /usr/bin/env python
"""
memory_test_v1.py
Memory testing python script
Use with memory_test_v2.ino

Created by Jeremy Smith on 2015-06-07
University of California, Berkeley
j-smith@ecs.berkeley.edu
"""

import os
import sys
import time
import serial
import numpy as np
from myfunctions import dataOutputHead
from argparse import ArgumentParser

__author__ = "Jeremy Smith"
__version__ = "1.3"

# Define constants
serialport = '/dev/cu.usbmodem1421'
v_ratio = 5.0/1023
time_step = 0.5

# Path name for location of script
path = os.path.dirname(os.path.abspath(__file__))


class Arguments(ArgumentParser):
	"""Class for parsing variables"""

	def __init__(self):
		super(Arguments, self).__init__()
		self.add_argument('--camread', action='store_true', help="Content addressable read")
		self.add_argument('--form', action='store_true', help="Forming array")
		self.add_argument('--writezero', action='store_true', help="Write a zero state")
		self.add_argument('--writeone', action='store_true', help="Write a one state")
		self.add_argument('--stdread', action='store_true', help="Standard read")
		self.add_argument('--cycleread', action='store_true', help="Cycled content addressable read")

		self.add_argument('-w', default=0, type=int, choices=xrange(0, 3), help="Word line number")
		self.add_argument('-b', default=0, type=int, choices=xrange(0, 3), help="Bit line number")

		self.add_argument('-t', default=0b111, type=int, choices=xrange(0, 8), help="Pattern data for bit lines as binary")
		self.add_argument('-r', default=100, type=int, help="Read/write time in ms")
		self.add_argument('-f', default=200, type=int, help="Form/precharge time in ms")
		self.add_argument('-l', default=1, type=int, help="Number of read/write pulses")

		self.add_argument('filename', nargs='?', type=str, default='output.txt', help="Output file name")

	def parse(self):
		a = self.parse_args()
		p = [x for x, i in vars(a).items() if i is True]
		if len(p) is not 1:
			self.error("specify one program")
		return vars(a), p[0]


def main():
	"""Main function"""

	args, program = Arguments().parse()
	connected = False
	data_string = ""
	voltage_data = []
	head_list = []
	progdict = {'camread': 1, 'form': 2, 'writezero': 3, 'writeone': 4, 'stdread': 5, 'cycleread': 6}

	print "\n================================"
	print "Memory test program"
	print __author__
	print "Version {:s}".format(__version__)
	print "Email: j-smith@eecs.berkeley.edu"
	print "================================\n"

	head_list.append("Directory: {:s}".format(path))
	head_list.append("Output file: {:s}".format(args['filename']))
	head_list.append("Program: {:d} {:s}".format(progdict[program], program))
	head_list.append("Address: WL {:d}   BL {:d}".format(args['w'], args['b']))
	head_list.append("Data Pattern: {:03b}".format(args['t']))
	head_list.append("Read/write time: {:d} ms".format(args['r']))
	head_list.append("Form/precharge time: {:d} ms".format(args['f']))
	head_list.append("Number of read/write pulses: {:d}".format(args['l']))

	for h in head_list:
		print h
	print '\n'

	# Open the serial port that your Ardiono is connected to
	try:
		ser = serial.Serial(serialport, 115200)
	except OSError:
		print "Please Connect Arduino via USB\n"
		return 1

	# Loop until the Arduino tells us it is ready
	print "Waiting to connect..."
	while not connected:
		serin = ser.read()
		if serin == 'A':
			print "Connected to Arduino\n"
			connected = True
	# Write the commands to the Arduino
	time.sleep(1)
	ser.write(str(progdict[program]))
	ser.write(chr(args['w']))
	ser.write(chr(args['b']))
	ser.write(chr(args['t']))
	ser.write(chr(args['r']))
	ser.write(chr(args['f']))
	ser.write(chr(args['l']))

	# Wait until the Arduino tells us it is finished
	while connected:
		serin = ser.read()
		if serin == 'A':
			continue
		if serin == 'Z':
			connected = False
			continue
		sys.stdout.write(serin)   # Writes output from Arduino to the stdout
		data_string += serin      # Stores the Arduino output

	# Close the port
	ser.close()

	# Convert string from serial bus to a numpy array and output to "results/output.txt"
	if len(data_string) is not 0:
		for i in [x.strip().split(',') for x in data_string.strip().split('\n')[3:]]:
			if len(i) is not 2:
				continue
			voltage_data.append([float(i[0])*time_step, float(i[1])*v_ratio])
		voltage_data = np.array(voltage_data)
		if len(voltage_data) is not 0:
			dataOutputHead(args['filename'], path, voltage_data.T, [head_list], format_d='%.1f\t %.4f\n')
		else:
			print "\nNo data file to output"

	print "DONE"
	return 0


if __name__ == "__main__":
	sys.exit(main())
