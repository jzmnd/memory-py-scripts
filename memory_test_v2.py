#! /usr/bin/env python
"""
memory_test_v2.py
Memory testing python script
Use with memory_test_v2.ino

Created by Jeremy Smith on 2015-06-18
University of California, Berkeley
j-smith@ecs.berkeley.edu
"""

import os
import sys
import time
import numpy as np
from argparse import ArgumentParser
from MemTest import *

__author__ = "Jeremy Smith"
__version__ = "2.0"

# Define constants
serialport = '/dev/cu.usbmodem1421'

# Path name for location of script
path = os.path.dirname(os.path.abspath(__file__))


class Arguments(ArgumentParser):
	"""Class for parsing variables"""

	def __init__(self):
		super(Arguments, self).__init__()

		self.add_argument('-w', default=0, type=int, choices=xrange(0, 3), help="Word line read number")

		self.add_argument('-a', default=2, type=int, help="Array size")
		self.add_argument('-t', default='1100', type=str, help="Pattern to write into array")

		self.add_argument('-r', default=100, type=int, help="Write pulse time in ms")
		self.add_argument('-p', default=200, type=int, help="Precharge time in ms")
		self.add_argument('-l', default=1, type=int, help="Number of read/write pulses")

		self.add_argument('filename', nargs='?', type=str, default='output', help="Output file name")

	def parse(self):
		a = vars(self.parse_args())
		if len(a['t']) != a['a']**2:
			self.error("Array size and write pattern do not match")
		if a['a'] == 1:
			a['filename'] += '_1x1_w{:s}-a{:b}.txt'
		elif a['a'] == 2:
			a['filename'] += '_2x2_w{:s}-a{:02b}.txt'
		else:
			a['filename'] += '_3x3_w{:s}-a{:03b}.txt'
		return a


def main():
	"""Main function"""

	print "\n================================"
	print "Memory test program"
	print __author__
	print "Version {:s}".format(__version__)
	print "Email: j-smith@eecs.berkeley.edu"
	print "================================\n"

	args = Arguments().parse()
	writelist = []                                       # List of write objects

	for i, c in enumerate(args['t']):                    # Creates list of write objects for each CRS device
		if c == '0':
			writelist.append(MemTest(serialport, 'writezero', wordline=i//args['a'], bitline=i%args['a'], rtime=args['r'], loop=args['l']))
		elif c == '1':
			writelist.append(MemTest(serialport, 'writeone', wordline=i//args['a'], bitline=i%args['a'], rtime=args['r'], loop=args['l']))
		else:
			print "Write pattern error - use 0 or 1"

	for a in range(2**args['a']):
		applypattern = MemTest(serialport, 'camread', wordline=args['w'], pattern=a, ftime=args['p'], loop=1)
		raw_input("\nSet WRITE voltage. Press Enter to continue...")
		for write in writelist:
			write.run()
		raw_input("\nSet READ voltage. Press Enter to continue...")
		applypattern.run()
		applypattern.outputfile(path, args['filename'].format(args['t'], a))

	print "\n===================="
	print "MEMORY TEST COMPLETE"
	print "====================\n"
	return


if __name__ == "__main__":
	sys.exit(main())
