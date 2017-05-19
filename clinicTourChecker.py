"""
Python Script designed to output names of all students who submitted an application by did not attend clinic tours 

usage: python3 clinicTourChecker.py [application submissions filename] [clinic tour attendees filename]

example: python3 clinicTourChecker.py SampleSubmissions.csv 

Outputs the name of each student who submitted an application *but did not attend clinic tours*

*************This is a port over from the homeworkChecker so variable names may be kinda weird 

Dependencies: use python3 -m pip install [package1] [package2] [...]
    numpy
    datascience
    matplotlib
    pandas
    scipy
    fuzzywuzzy

Example: python3 -m pip install numpy datascience matplotlib pandas scipy fuzzywuzzy
"""

import sys
import numpy as np
from datascience import *
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


def find_fuzzy_matches(all_emails, submission_emails):
    """Given an array of all emails and an array of submission emails, uses fuzzy string matching to find all emails that did not submit
    
    ============Suite 1============
    >>> all_emails        = ['kunalmishra9@gmail.com', 'kmishra9@berkeley.edu', 'oski@berkeley.edu']
    >>> submission_emails = ['kunalmishra9@gmail.com', 'kmishra9@berkeley.edu', 'oski@berkeley.edu']
    >>> find_fuzzy_matches(all_emails, submission_emails)
    []
    >>> submission_emails = ['kunalmishra9@gmial', 'kmishra9@berkeley.edu', 'oski@berkeley.edu']
    >>> find_fuzzy_matches(all_emails, submission_emails)
    []
    >>> submission_emails = ['kunalmishra9@gmial ', 'kmishra9@berkeley', 'oski@berkeley.edu ']
    >>> find_fuzzy_matches(all_emails, submission_emails)
    []
    
    ============Suite 2============
    >>> all_emails        = ['kunalmishra9@gmail.com', 'kmishra9@berkeley.edu', 'oski@berkeley.edu']
    >>> submission_emails = ['oski@berkeley.edu ']
    >>> find_fuzzy_matches(all_emails, submission_emails)
    ['kunalmishra9@gmail.com', 'kmishra9@berkeley.edu']
    >>> submission_emails = ['kmishra9@berkeley ','oski@berkeley.edu ']
    >>> find_fuzzy_matches(all_emails, submission_emails)
    ['kunalmishra9@gmail.com']
    
    ============Suite 3============
    >>> all_emails        = ['kunalmishra9@gmail.com', 'kmishra9@berkeley.edu', 'oski@berkeley.edu']
    >>> submission_emails = ['kunalmishra9@gmail.com', 'kmishra9@berkeley.edu', 'oski@berkeley.edu', 'rando@berkeley']
    >>> find_fuzzy_matches(all_emails, submission_emails)
    []
    >>> submission_emails = ['kunalmishra9@gmail.com', 'oski@berkeley.edu', 'rando@berkeley']
    >>> find_fuzzy_matches(all_emails, submission_emails)
    **********
    Please check on kmishra9@berkeley.edu. The most similar email we found in the submissions was rando@berkeley with a similarity score of 86 out of 100. 
    **********
    ['kmishra9@berkeley.edu']
    """
    
    num_students, num_submissions = len(all_emails), len(submission_emails)
    
    matches = [ process.extract(query=student_email, choices=submission_emails) + [(student_email, -1)] for student_email in all_emails ] 
    
    #Removes all perfect matches -- need to take the top X matches, where X = submissions - perfect matches
    get_top_similarity_score = lambda processed_query: processed_query[0][1]
    get_most_similar_email   = lambda processed_query: processed_query[0][0]
    get_email                = lambda processed_query: processed_query[-1][0]

    
    missing_submissions = [processed_query for processed_query in matches if get_top_similarity_score(processed_query) != 100]
    num_missing_submissions = len(missing_submissions)
    
    #False negatives -- people inputted their email incorrectly
    if num_missing_submissions + num_submissions > num_students:
        num_false_negatives = num_missing_submissions + num_submissions - num_students 
        
        missing_submissions = sorted( missing_submissions, key=lambda processed_query: processed_query[0][1], reverse=True )
        
        
        count = 0
        flagged = []
        for missing_submission in missing_submissions:
            if (get_top_similarity_score(missing_submission) < 80 or get_most_similar_email(missing_submission)[0] != get_email(missing_submission)[0]) and count < num_false_negatives:
                print("**********" + "\nPlease check on " + get_email(missing_submission) + ". The most similar email we found in the submissions was " +
                get_most_similar_email(missing_submission) + " with a similarity score of " + str(get_top_similarity_score(missing_submission)) + " out of 100.", "\n**********" )
                
                flagged.append(missing_submission)
                
            count += 1
        
        #Getting rid of false negatives (people who were the closest fuzzy matches)
        missing_submissions = missing_submissions[num_false_negatives:] + flagged
        
    #Logical error or issue with input files    
    elif num_missing_submissions + num_submissions < num_students:
        error_msg =  "Something went wrong -- most likely, your roster is incomplete or a student submitted twice, please correct the input files\n\n"
        error_msg += "Here are the students with 'missing' submissions' " + str(missing_submissions) 
        assert False, error_msg
    
        
    
    missing_submissions = [get_email(processed_query) for processed_query in missing_submissions]
    
    return missing_submissions

#Ensuring that enough file paths have been passed into the script
improper_arg_msg = "Usage: 'python3 clinicTourChecker.py [application submissions filename] [clinic tour attendees filename]'"
assert len(sys.argv) == 3, improper_arg_msg

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
    students_without_submissions.append( find_fuzzy_matches(all_student_emails, submitted_student_emails) )

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
output = missed_homeworks_tbl.join("Email",roster_table).select("Name", "Email")

print(output.as_text())

#Outputting emails into a file
path = "students_without_submissions.txt"
if len(homework_response_paths) == 1:
    hw_number = [int(s) for s in homework_response_paths[0][::-1] if s.isdigit()]
    if len(hw_number) > 0:
        path = path[:-4] + "HW" + str(hw_number[0]) + ".txt"

    

file = open(path, 'w')
emails = output.column("Email")

file.write( emails[0] )

for email in emails[1:]:
    file.write( ", " )
    file.write( email )

file.close()

if __name__ == "__main__":
    import doctest
    doctest.testmod()