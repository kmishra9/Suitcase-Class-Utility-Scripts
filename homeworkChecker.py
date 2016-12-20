"""
Python Script designed to output names of all students who did not complete the homework

usage: python3 homeworkChecker.py [roster filename] [homework 1 responses filename] [...]

example: python3 homeworkChecker.py roster.csv homework1Responses.csv homework2Responses.csv

Outputs the name of each student who missed a homework, sorted by their UGSI and the number of homework assignments missed

Dependencies: use python3 -m pip install [package]
    numpy
    datascience
    matplotlib
    pandas
    scipy
"""

import sys
import numpy as np
from datascience import *

print(sys.argv)

#Ensuring that enough file paths have been passed into the script
assert len(sys.argv) >= 3, "Improper arguments passed in - 'python3 homeworkChecker.py [roster filename] [homework 1 responses filename] [...]'"

#Getting the roster and homework response paths
roster_path = sys.argv[1]
homework_response_paths = []

for homework_response_path in sys.argv[2:]:
    homework_response_paths.append( homework_response_path )

#Putting them into tables
roster_table = Table.read_table(roster_path)
homework_tables = []

for homework_response_path in homework_response_paths:

    #TODO: Ensure timestamp and email are always 0 and 1 columns
    homework_tables.append( Table.read_table(homework_response_path).select(0, 1) )
