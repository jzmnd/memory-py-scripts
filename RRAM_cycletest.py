# RRAM cycle testing
# Jeremy Smith
# Version 1.0

import os, sys, time
from visa import *
import numpy as np
from myfunctions import *
from argparse import ArgumentParser

vset = 4.5          # Set voltage
vreset = -4.0       # Reset voltage
vread = 0.5         # Read voltage

smuanode = '1'        # SMU number of anode
smucathode = '3'      # SMU number of cathode

agilent4155 = instrument("GPIB::17")
agilent4155.ask("*IDN?")
agilent4155.ask("*OPT?")

agilent4155.write("*RST; *CLS")
agilent4155.write("US")             # Enter 4155c FLEX command control mode
agilent4155.write("FMT 1,1")        # Specify output data format ASCII w/ Header and source

agilent4155.write("CN %s,%s"%(smuanode, smucathode))         # Enables SMU1 and SMU3
agilent4155.write("MM 1,%s,%s"%(smuanode, smucathode))       # Set measurement mode to spot for SMU 1 and 3
agilent4155.write("CMM %s,1"%smuanode)                       # Set anode to measure current
agilent4155.write("CMM %s,1"%smucathode)                     # Set cathode to measure current




agilent4155.write("DV 3,0,voltage,Icomp")





agilent4155.write("XE")             # Trigger measurement




agilent4155.write("CL")             # 
agilent4155.write(":PAGE")          # Returns to the 4155c SCPI command control mode
