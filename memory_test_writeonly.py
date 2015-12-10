#! /usr/bin/env python
"""
memory_test_writeonly.py
Memory testing python script (write states only with no read)
Use with memory_test_v3.ino

Created by Jeremy Smith on 2015-07-10
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
__version__ = "1.1"

# Define constants
serialport = '/dev/cu.usbmodem1421'

# Path name for location of script
path = os.path.dirname(os.path.abspath(__file__))


def main():
	"""Main function"""

	print "\n================================"
	print "Memory test program (write only)"
	print __author__
	print "Version {:s}".format(__version__)
	print "Email: j-smith@eecs.berkeley.edu"
	print "================================\n"

	args = Arguments().parse()
	writelist = []                                       # List of write objects

	for i, c in enumerate(args['pattern']):                    # Creates list of write objects for each CRS device
		if c == '0':
			writelist.append(MemTest(serialport, 'writezero', wordline=i//args['arraysize'], bitline=i%args['arraysize'], rtime=args['writepulse'], loop=args['loop'], gtime=args['gndpulse']))
		elif c == '1':
			writelist.append(MemTest(serialport, 'writeone', wordline=i//args['arraysize'], bitline=i%args['arraysize'], rtime=args['writepulse'], loop=args['loop'], gtime=args['gndpulse']))
		else:
			print "Write pattern error - use 0 or 1"

	raw_input("\nSet WRITE voltage. Press Enter to continue...")
	for write in writelist:
		write.run()

	print "\n===================="
	print "MEMORY TEST COMPLETE"
	print "====================\n"
	return


if __name__ == "__main__":
	sys.exit(main())
