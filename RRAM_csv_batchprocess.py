#! /usr/bin/env python
"""
RRAM_csv_batchprocess.py
Reads EasyExpert .csv files for RRAMs and extracts parameters

Created by Jeremy Smith on 2015-06-08
University of California, Berkeley
j-smith@ecs.berkeley.edu
"""

import os
import sys
import numpy as np
import myfunctions as mf

__author__ = "Jeremy Smith"
__version__ = "1.5"

data_path = os.path.dirname(__file__)    # Path name for location of script

files = os.listdir(data_path)   # All files in directory
data_summary = []

# Device/testing parameters
area = 1.8e-8    # Device area
r_series = 49.0  # Series resistor

# Voltages at which to extract average resistance values
vr_SET = 0.5      # For set sweep
vr_RESET = -0.6   # For reset sweep
vs = 2            # Range of points either side for average

# Filtering
ifilter = 1.0e-3    # Filter all devices with max current and max current differences below this level
vfilter = 0.1     # Filter all devices with Vswitch less than this level


def main():
	"""Main function"""

	print '\n'
	print "Batch importing .csv files..."
	print data_path
	print '\n'

	devicecount = 0
	filteredcount = 0
	v_set_list = []
	v_reset_list = []

	# Loops through each device file
	for d in files:
		print d
		if "I-V" not in d:
			continue
		devicecount += 1

		datad, headd = mf.csvImport(d, data_path, 12)
		deviceID = headd[4][1]       # Device name
		iMax = float(headd[11][2])   # Compliance current

		# Calculating adjacent point differences
		Ianode = np.array(datad["ABSIanode"])
		Janode = Ianode/area
		diff_Ianode = np.array(mf.numDifference(datad["ABSIanode"]))
		Vanode = np.array(datad["Vanode"])
		diff_resistance = abs(1/np.array(mf.numDiff(datad["ABSIanode"], datad["Vanode"]))) - r_series
		diff_resistance_smoothed = mf.adjAvSmooth(diff_resistance, N=2)

		# Filtering
		if max(Ianode) < ifilter:
			print "   FILTERED - low current"
			filteredcount += 1
			continue
		if max(abs(diff_Ianode)) < ifilter:
			print "   FILTERED - no switching (low diffI)"
			filteredcount += 1
			continue

		# Find switching voltages and resistances
		v_switch = Vanode[np.argmax(abs(diff_Ianode))]
		if v_switch > vfilter:
			v_set_list.append(v_switch)

			rpHRS = np.where(Vanode == vr_SET)[0][0]
			rpLRS = np.where(Vanode == vr_SET)[0][1]

			tp = "SET"
		elif v_switch < -vfilter:
			v_reset_list.append(v_switch)

			rpHRS = np.where(Vanode == vr_RESET)[0][1]
			rpLRS = np.where(Vanode == vr_RESET)[0][0]

			tp = "RESET"
		else:
			print "   FILTERED - no switching (low vswitch)"
			filteredcount += 1
			continue

		print "   Switched at", v_switch, "V"
		r_HRS = np.average(diff_resistance_smoothed[rpHRS-vs:rpHRS+vs+1])
		r_LRS = np.average(diff_resistance_smoothed[rpLRS-vs:rpLRS+vs+1])

		# Output
		mf.quickPlot(d[:-4]+"_RES", data_path, [Vanode, diff_resistance_smoothed], xlabel="V [V]", ylabel="R [ohms]", yscale="log")
		mf.quickPlot(d[:-4]+"_DIF", data_path, [Vanode, diff_Ianode], xlabel="V [V]", ylabel="diff I [A]", yscale="linear")
		mf.quickPlot(d[:-4]+"_IV", data_path, [Vanode, Ianode], xlabel="V [V]", ylabel="I [A]", yscale="log")

		data_summary.append([d[:-4], tp, v_switch, r_HRS, r_LRS])

		mf.dataOutput(d[:-4]+".txt", data_path, [Vanode, Ianode, Janode, diff_Ianode, diff_resistance, diff_resistance_smoothed], format="%.2f\t %.5e\t %.5e\t %.5e\t %.5e\t %.5e\n")

	deviceyield = 100*(1 - float(filteredcount)/float(devicecount))
	print "Yield:", deviceyield, "%"

	logdatasorted_set, weibull_set, datasorted_set, ecdf_set = mf.weibullPlot(v_set_list)
	logdatasorted_reset, weibull_reset, datasorted_reset, ecdf_reset = mf.weibullPlot(v_reset_list)

	mf.dataOutput("SET.txt", data_path, [datasorted_set[:-1], logdatasorted_set, weibull_set, ecdf_set], format="%.2f\t %.5e\t %.5e\t %.5f\n")
	mf.dataOutput("RESET.txt", data_path, [datasorted_reset[:-1], logdatasorted_reset, weibull_reset, ecdf_reset], format="%.2f\t %.5e\t %.5e\t %.5f\n")

	mf.dataOutput("summary.txt", data_path, map(list, zip(*data_summary)), format="%s\t %s\t %.2f\t %.3e\t %.3e\n")
	return


if __name__ == "__main__":
	sys.exit(main())
