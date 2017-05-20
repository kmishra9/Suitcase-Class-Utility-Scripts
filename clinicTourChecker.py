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

Example: python3 -m pip install numpy datascience matplotlib pandas scipy fuzzywuzzy

Example of Application Submissions File: https://docs.google.com/spreadsheets/d/1dfNlANsLDBeqmFl-hD4bBg_gYhxK3KzBEf-ZEP5ENS0/edit?usp=sharing
Example of Clinic Tour Attendees File: https://docs.google.com/spreadsheets/d/1RZRdkwvCBKodHu1bFmEE1K9G1NBMdOdDyh0rlWQm2-o/edit?usp=sharing
"""

import sys
import numpy as np
import pandas as pd 
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
    
    assert "Email" in df.columns and "Name" in df.columns, "The input file given did not have the correct structure -- it needs (at least) an 'Email' and 'Name' column but these were the columns given: " + str(df.columns.values.tolist())
    print(".\n..\n...\nSuccess -- loading complete!\n")
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

try:
    print("")
    application_submissions_url = input("Please input the URL of the Google Sheet with Application Submissions:\n")
    application_submissions     = load_data_into_frame(application_submissions_url)
    
    clinic_tour_attendances_url = input("Please input the URL of the Google Sheet with Clinic Tour Attendees:\n")
    clinic_tour_attendances     = load_data_into_frame(clinic_tour_attendances_url)

except:
    error_msg  = "Uh oh... Something went wrong while trying to load the data in from the URL you provided.\n"
    error_msg += "Make sure:\n\t1) the URL is from the **URL BAR** at the top of your browser \n\t2) you have clicked 'Share' and 'Get Shareable Link' in the top right of the sheet -- the sheet needs to not be locked down and private for us to access it here\n"
    print(error_msg)
    quit()


#Getting students who submitted an application but didn't attend clinic tours
all_student_emails          = set( application_submissions['Email'] )
submitted_student_emails    = set( clinic_tour_attendances['Email'] )
students_without_submissions= find_fuzzy_matches(all_student_emails, submitted_student_emails)

#Creating a table of students without submissions
output = application_submissions[ application_submissions['Email'].isin(students_without_submissions) ]


print(output[["Name", "Email"]].head(len(students_without_submissions)))

#Outputting emails into a file
path = "students_without_submissions.txt"

output.to_csv( path, columns=["Email"], index=False )

# file = open(path, 'w')
# emails = output.column("Email")

# file.write( emails[0] )

# for email in emails[1:]:
#     file.write( ", " )
#     file.write( email )

# file.close()

if __name__ == "__main__":
    import doctest
    doctest.testmod()