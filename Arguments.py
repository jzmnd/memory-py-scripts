#! /usr/bin/env python
"""
Arguments.py
Class for parsing memory testing arguments
Use with memory_test_v3.ino

Created by Jeremy Smith on 2015-07-10
University of California, Berkeley
j-smith@ecs.berkeley.edu
"""

import os
import sys
from argparse import ArgumentParser


class Arguments(ArgumentParser):
	"""Class for parsing variables"""

	def __init__(self):
		super(Arguments, self).__init__()

		self.add_argument('-w', '--wordline', default=0, type=int, choices=xrange(0, 3), help="Word line read number")

		self.add_argument('-a', '--arraysize', default=2, type=int, help="Array size")
		self.add_argument('-t', '--pattern', default='1100', type=str, help="Pattern to write into array")

		self.add_argument('-r', '--writepulse', default=100, type=int, help="Write pulse time in ms")
		self.add_argument('-p', '--prechargepulse', default=200, type=int, help="Precharge time in ms")
		self.add_argument('-l', '--loop', default=1, type=int, help="Number of read/write pulses")
		self.add_argument('-g', '--gndpulse', default=100, type=int, help="Ground time in ms")

		self.add_argument('filename', nargs='?', type=str, default='output', help="Output file name")

	def parse(self):
		a = vars(self.parse_args())
		if len(a['pattern']) != a['arraysize']**2:
			self.error("Array size and write pattern do not match")
		if a['arraysize'] == 1:
			a['filename'] += '_1x1_w{:s}-a{:b}.txt'
		elif a['arraysize'] == 2:
			a['filename'] += '_2x2_w{:s}-a{:02b}.txt'
		else:
			a['filename'] += '_3x3_w{:s}-a{:03b}.txt'
		return a
