"""
Python Script designed to output names of all students who submitted an application by did not attend clinic tours 

usage: python3 clinicTourChecker.py

Outputs the name of each student who submitted an application *but did not attend clinic tours*

Dependencies: use python3 -m pip install [package1] [package2] [...]
    numpy
    datascience
    matplotlib
    pandas
    scipy
    fuzzywuzzy
    termcolor

Example: python3 -m pip install numpy datascience matplotlib pandas scipy fuzzywuzzy

Example of Application Submissions File:    https://docs.google.com/spreadsheets/d/1dfNlANsLDBeqmFl-hD4bBg_gYhxK3KzBEf-ZEP5ENS0/edit?usp=sharing
Example of Clinic Tour Attendees File:      https://docs.google.com/spreadsheets/d/1RZRdkwvCBKodHu1bFmEE1K9G1NBMdOdDyh0rlWQm2-o/edit?usp=sharing

Sample URL to use for Prompt 1:             https://docs.google.com/spreadsheets/d/1dfNlANsLDBeqmFl-hD4bBg_gYhxK3KzBEf-ZEP5ENS0/edit#gid=1958005464
Sample URL to use for Prompt 2:             https://docs.google.com/spreadsheets/d/1RZRdkwvCBKodHu1bFmEE1K9G1NBMdOdDyh0rlWQm2-o/edit#gid=0
"""

import sys
import numpy as np
import pandas as pd 
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from termcolor import *

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
    
    assert "Email" in df.columns and "Name" in df.columns, "The input file given did not have the correct structure -- it needs (at least) an 'Email' and 'Name' column but these were the columns given: " + str(df.columns.values.tolist())
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
    application_submissions_url = input("Please input the URL of the Google Sheet with " + colored('Application Submissions', 'green') + ":\n")
    application_submissions     = load_data_into_frame(application_submissions_url)
    
    clinic_tour_attendances_url = input("Please input the URL of the Google Sheet with " + colored('Clinic Tour Attendees', 'green') + ":\n")
    clinic_tour_attendances     = load_data_into_frame(clinic_tour_attendances_url)

except:
    error_msg  = colored('Something went wrong while trying to load the data', 'red') + ' in from the URL!\n\n'
    error_msg += "Make sure:\n\t1) the URL is from the " + colored("URL BAR", 'red') + " (for the sheet)"
    error_msg += "\n\t2) you have clicked " + colored('Share', 'red') + " and " + colored('Get Shareable Link', 'red') + " (for the sheet)\n"
    print(error_msg)
    quit()


#Getting students who submitted an application but didn't attend clinic tours
all_student_emails          = set( application_submissions['Email'] )
submitted_student_emails    = set( clinic_tour_attendances['Email'] )
students_without_submissions= find_fuzzy_matches(all_student_emails, submitted_student_emails)

#Creating a table of students without submissions
output = application_submissions[ application_submissions['Email'].isin(students_without_submissions) ]

cprint("========================================================================", 'blue')
print(output[["Name", "Email"]].head(len(output)))
cprint("========================================================================", 'blue')


#Outputting emails into a file
path = "students_without_submissions.txt"
output.to_csv( path, columns=["Email"], index=False, header=False )