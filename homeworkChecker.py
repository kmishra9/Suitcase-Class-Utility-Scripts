"""
Python Script designed to output names of all students who did not complete the homework

usage: python3 homeworkChecker.py [roster filename] [homework responses filename] [...]

example: python3 homeworkChecker.py roster.csv homework1Responses.csv homework2Responses.csv
"""

import numpy as np
from datascience import *

if __name__ == "main":

    assert len(sys.argv) >= 2
