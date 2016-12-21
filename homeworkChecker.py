"""
Python Script designed to output names of all students who did not complete the homework

usage: python3 homeworkChecker.py [roster filename] [homework 1 responses filename] [...]

example: python3 homeworkChecker.py SampleRoster.csv SampleHomeworkResponses.csv SampleHomeworkResponses2.csv

Outputs the name of each student who missed a homework, sorted by their UGSI and the number of homework assignments missed. In addition, creates a file named (students_without_submissions) that *only* contains their emails for easy copy/paste into an email reminder and or notification.

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


#Ensuring that enough file paths have been passed into the script
improper_arg_msg = "Improper arguments passed in - 'python3 homeworkChecker.py [roster filename] [homework 1 responses filename] [...]'"
assert len(sys.argv) >= 3, improper_arg_msg

#Getting the roster and homework response paths
roster_path = sys.argv[1]
homework_response_paths = []

for homework_response_path in sys.argv[2:]:
    homework_response_paths.append( homework_response_path )

#Putting them into tables
roster_table = Table.read_table(roster_path)
homework_tables = []

for homework_response_path in homework_response_paths:
    homework_tables.append( Table.read_table(homework_response_path).select("Email") )

#Getting students who are in class but didn't submit
all_student_emails = set( roster_table.column("Email") )
students_without_submissions = []

for homework_table in homework_tables:
    submitted_student_emails = set( homework_table.column("Email") )

    students_without_submissions.append( all_student_emails - submitted_student_emails )

#Figuring out the number of times each student missed a homework
missed_homeworks = dict()       #Maps from student's email -> # of missed homeworks

for student_set in students_without_submissions:
    for student in student_set:

        if student not in missed_homeworks:
            missed_homeworks[student] = 0
        missed_homeworks[student] += 1

#Creating a table with the missed_homeworks information
missed_homeworks_tbl = Table().with_columns(
    "Email",            [student                   for student in missed_homeworks],
    "Num missing",      [missed_homeworks[student] for student in missed_homeworks]
)

#Get all students who missed homework and sort them by their UGSI, and the number of homeworks they've missed
output = missed_homeworks_tbl.join("Email",roster_table).select("Name", "Email", "UGSI", "Num missing")

output = output.sort("Num missing", descending=True).sort("UGSI")

print(output)

#Outputting emails into a file
file = open("students_without_submissions.txt", 'w')
emails = output.column("Email")

file.write( emails[0] )

for email in emails[1:]:
    file.write( ", " )
    file.write( email )

file.close()
