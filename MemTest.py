#! /usr/bin/env python
"""
MemTest.py
Memory testing class to connect to Arduino
Use with memory_test_v2.ino

Created by Jeremy Smith on 2015-06-19
University of California, Berkeley
j-smith@ecs.berkeley.edu
"""

import os
import sys
import time
import serial
import numpy as np
from myfunctions import dataOutputHead


class MemTest():
	"""Class for running memory test sequence on Arduino"""

	v_ratio = 5.0/1023
	time_step = 0.5

	def __init__(self, serialport, program, wordline=0, bitline=0, pattern=0, rtime=100, ftime=200, loop=1, baud=115200):
		_progdict = {'camread': 1, 'form': 2, 'writezero': 3, 'writeone': 4, 'stdread': 5}
		try:
			self._prognum = _progdict[program]    # Program number
		except KeyError:
			print "Specify program (camread, form, writezero, writeone, stdread) for MemTest\n"
			sys.exit()

		self._serialport = serialport             # Serial port
		self._program = program                   # Program name
		self._wordline = wordline                 # Word line number
		self._bitline = bitline                   # Bit line number
		self._pattern = pattern                   # Data pattern to match
		self._rtime = rtime                       # Read/write pulse time
		self._ftime = ftime                       # Forming/precharge pulse time
		self._loop = loop                         # Number of loops
		self._baud = baud                         # Arduino serial port bit rate

		self._connected = False
		self._datastring = ""
		self._headlist = []

		self._headlist.append("Program: {:d} {:s}".format(self._prognum, program))
		self._headlist.append("Address: WL {:d}   BL {:d}".format(wordline, bitline))
		self._headlist.append("Data Pattern: {:03b}".format(pattern))
		self._headlist.append("Read/write time: {:d} ms".format(rtime))
		self._headlist.append("Form/precharge time: {:d} ms".format(ftime))
		self._headlist.append("Number of read/write pulses: {:d}".format(loop))

	def __repr__(self):
		return '\n'.join(self._headlist)

	def run(self, printout=True):
		"""Connects to Arduino and runs program"""
		if printout:
			print self
		try:
			ser = serial.Serial(self._serialport, self._baud)   # Open the serial port that your Ardiono is connected to
		except OSError:
			print "\nPlease Connect Arduino via USB\n"
			sys.exit()

		print "Waiting to Connect..."
		while not self._connected:             # Loop until the Arduino tells us it is ready
			serin = ser.read()
			if serin == 'A':
				print "Connected to Arduino\n"
				self._connected = True

		time.sleep(0.5)
		ser.write(str(self._prognum))          # Write the commands to the Arduino
		ser.write(chr(self._wordline))
		ser.write(chr(self._bitline))
		ser.write(chr(self._pattern))
		ser.write(chr(self._rtime))
		ser.write(chr(self._ftime))
		ser.write(chr(self._loop))

		while self._connected:                 # Wait until the Arduino tells us it is finished
			serin = ser.read()
			if serin == 'A':
				continue
			if serin == 'Z':
				self._connected = False
				continue
			if printout:
				sys.stdout.write(serin)        # Writes output from Arduino to the stdout
			self._datastring += serin          # Stores the Arduino output as a string

		ser.close()                            # Close the port
		print "Disconnected successfully\n"
		return

	def outputfile(self, path, filename='output.txt'):
		"""Converts string from serial bus to a numpy array and outputs to 'results/output.txt'"""
		voltage_data = []
		if len(self._datastring) is not 0:
			for i in [x.strip().split(',') for x in self._datastring.strip().split('\n')[3:]]:
				if len(i) is not 2:
					continue
				voltage_data.append([float(i[0])*self.time_step, float(i[1])*self.v_ratio])

			voltage_data = np.array(voltage_data)

			if len(voltage_data) is not 0:
				dataOutputHead(filename, path, voltage_data.T, [self._headlist], format_d='%.1f\t %.4f\n')
				print "Data written to {:s}\n".format(filename)
			else:
				print "\nNo data file to output\n"
		else:
			print "\nProgram not run therefore no data file to output\n"
		return

	def reset(self):
		"""Resets status and empties stored data"""
		self._connected = False
		self._datastring = ""
		return
