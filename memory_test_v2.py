#! /usr/bin/env python
"""
memory_test_v2.py
Memory testing python script
Use with memory_test_v3.ino

Created by Jeremy Smith on 2015-06-18
University of California, Berkeley
j-smith@ecs.berkeley.edu
"""

import os
import sys
import time
import numpy as np
from Arguments import *
from MemTest import *

__author__ = "Jeremy Smith"
__version__ = "2.3"

# Define constants
serialport = '/dev/cu.usbmodem1421'

# Path name for location of script
path = os.path.dirname(os.path.abspath(__file__))


def main():
	"""Main function"""

	print "\n================================"
	print "Memory test program"
	print __author__
	print "Version {:s}".format(__version__)
	print "Email: j-smith@eecs.berkeley.edu"
	print "================================\n"

	args = Arguments().parse()        # Command line arguements 
	writelist = []                    # List of write objects

	# Creates list of write objects for each CRS device
	for i, c in enumerate(args['pattern']):
		if c == '0':
			writelist.append(MemTest(serialport, 'writezero', wordline=i//args['arraysize'], bitline=i%args['arraysize'], rtime=args['writepulse'], loop=args['loop'], gtime=args['gndpulse']))
		elif c == '1':
			writelist.append(MemTest(serialport, 'writeone', wordline=i//args['arraysize'], bitline=i%args['arraysize'], rtime=args['writepulse'], loop=args['loop'], gtime=args['gndpulse']))
		else:
			print "Write pattern error - use 0 or 1"

	# Runs writes and then does CAM read
	for a in range(2**args['arraysize']):
		applypattern = MemTest(serialport, 'camread', wordline=args['wordline'], pattern=a, ftime=args['prechargepulse'])
		raw_input("\nSet WRITE voltage. Press Enter to continue...")
		for write in writelist:
			write.run()
		raw_input("\nSet READ voltage. Press Enter to continue...")
		applypattern.run()
		applypattern.outputfile(path, args['filename'].format(args['pattern'], a))

	print "\n===================="
	print "MEMORY TEST COMPLETE"
	print "====================\n"
	return


if __name__ == "__main__":
	sys.exit(main())
