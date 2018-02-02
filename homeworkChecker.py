"""
Python Script designed to output names of all students who did not complete the homework

usage: python3 homeworkChecker.py

Outputs the name of each student who missed a homework, sorted by their UGSI and the number of homework assignments missed. In addition, creates a file named (students_without_submissions) that *only* contains their emails for easy copy/paste into an email reminder and or notification.

Dependencies: use python3 -m pip install [package1] [package2] [...]
    numpy
    datascience
    matplotlib
    pandas
    scipy
    fuzzywuzzy
    termcolor

Example: python3 -m pip install numpy datascience matplotlib pandas scipy fuzzywuzzy termcolor

Example of Homework Checking Roster File:   
    https://docs.google.com/spreadsheets/d/1w51h2umKCFJWbAVPUWw0HjtTaZVZ3H-qcj395t5oFZw/edit?usp=sharing
Example of Homework Submissions File:       
    https://docs.google.com/spreadsheets/d/1AwTrX-xcn-kTpx9yfBtdkU4McitKRSt6Ct8TSg33Xr8/edit?usp=sharing
"""

import sys
import numpy as np
import pandas as pd
import os
from termcolor import *
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def load_data_into_frame(url):
    #Doing some URL reformatting
    separated       = url.split(sep='/')
    gid             = separated[-1].split(sep='gid=')[-1]
    separated[-1]    = 'export?gid=' + gid + '&format=csv'
    reconstructed_url = '/'.join(separated)
    
    df = pd.read_csv(reconstructed_url)
    
    assert df is not None, "Data did not load!"

    if "Email Address" in df.columns:                               df["Email"] = df["Email Address"]
    if "First Name" in df.columns and "Last Name" in df.columns:    df["Name"]  = np.core.defchararray.add(df["First Name"].values.astype(str), df["Last Name"].values.astype(str))
    
    assert "Email" in df.columns, "The input file given did not have the correct structure -- it needs (at least) an 'Email' column but these were the columns given: " + str(df.columns.values.tolist())
    cprint(".\n..\n...\nSuccess -- loading complete!\n", 'green')
    return df

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
    # Sanitizing input email lists
    submission_emails = [email for email in submission_emails if type(email) == str]
    all_emails = [email for email in all_emails if type(email) == str]
    
    submission_emails = [student_email.split('@')[0] for student_email in submission_emails]
    
    num_students, num_submissions = len(all_emails), len(submission_emails)
    
    matches = [ process.extract(query=student_email.split('@')[0], choices=submission_emails) + [(student_email, -1)] for student_email in all_emails ] 
    
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
                cprint("**********", 'blue')
                cprint("Please check on " + get_email(missing_submission) + ". The most similar email we found was suspicious", 'red' )
                cprint("**********", 'blue')
                print("")
                
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

try:
    os.system('clear')

    roster_url = input("Please input the URL of the Google Sheet with the " + colored('Suitcase Class Roster', 'green') + ":\n")
    roster     = load_data_into_frame(roster_url)
    
    homework_responses = []
    while True:
        homework_response_url = input("Please input the URL of the Google Sheet with " + colored('each Homework submission', 'green') + " you would like to grade. Press 'Enter' after each one and press '.' when you are done:\n")
        if homework_response_url == "" or homework_response_url == ".":
            if len(homework_responses) == 0:    quit()
            else:                               break
            
        homework_responses.append( load_data_into_frame(homework_response_url) )

except:
    os.system('clear')
    error_msg  = colored('Something went wrong while trying to load the data', 'red') + ' in from the URL!\n\n'
    error_msg += "Make sure:\n\t1) the URL is from the " + colored("URL BAR", 'red') + " (for the sheet)"
    error_msg += "\n\t2) you have clicked " + colored('Share', 'red') + " and " + colored('Get Shareable Link', 'red') + " (for the sheet)\n"
    print(error_msg)
    quit()

#Getting students who are on class roster but didn't submit this homework
all_student_emails = set( roster['Email'] )
all_submitted_student_emails = [set(homework_response['Email']) for homework_response in homework_responses]
students_without_submissions = [find_fuzzy_matches(all_student_emails, submitted_student_emails) for submitted_student_emails in all_submitted_student_emails]

#Figuring out the number of times each student missed a homework
missed_homeworks = dict()       #Maps from student's email -> # of missed homeworks

for student_set in students_without_submissions:
    for student in student_set:

        if student not in missed_homeworks:
            missed_homeworks[student] = 0
        missed_homeworks[student] += 1

#Get all students who missed homework and sort them by their UGSI, and the number of homeworks they've missed
columns = ["Name", "Email", "UGSI"]
assert all(column in roster.columns for column in columns), "Structure of Roster File is incorrect -- need the following columns:\n\t" + str(columns)

output = roster[ roster['Email'].isin(missed_homeworks.keys()) ].reset_index()

output['Num missing'] = [ missed_homeworks[student] for student in output['Email'] ]

output = output.sort_values(by=["Num missing", "UGSI"], ascending=False)

cprint("========================================================================", 'blue')
print( output[columns+['Num missing']].head(len(output)) )
cprint("========================================================================", 'blue')

#Outputting emails into a file
path = "students_without_submissions.txt"
output.to_csv( path, columns=["Email"], index=False, header=False )

if __name__ == "__main__":
    #import doctest
    #doctest.testmod()
    ""