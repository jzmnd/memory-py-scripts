# memory-py-scripts

Python scripts and Arduino files for controlling MUXs for testing of memory circuits.

MemTest.py contains the class for connecting to Arduino and running programs.

memory_test_v2.ino is the Arduino file.

Memoryfunctions.cpp is the Arduino library required in memory_test_v2.ino file.

Example of python script usage:

`python ./memory_test_v2.py -w=0 -a=2 -t='1100' -r=100 -p=200 -g=100 -l=1 "filename_of_dut"`
