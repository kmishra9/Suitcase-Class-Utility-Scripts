"""
Python Script designed to notify all students who did not complete the homework

usage: python3 notifyByEmail.py [students_without_submissions filename]

example: python3 notifyByEmail.py students_without_submissions.txt

Given a file containing a set of emails for students who are missing submissions, emails them a generic message letting them know we didn't receive the homework and that they need to complete the HW ASAP.

Dependencies: use python3 -m pip install [package1] [package2] [...]
    TBD

Example: python3 -m pip install TBD


Resources
    http://naelshiab.com/tutorial-send-email-python/
    https://docs.python.org/3/library/email-examples.html
"""

import smtplib
from email.mime.text import MIMEText
import termcolor

def get_recipients():
    return ['kunalmishra9@gmail.com', 'kmishra9@berkeley.edu']


server = smtplib.SMTP('smtp.gmail.com:587')
server.ehlo()
server.starttls()
user_email, user_pass = 'suitcaseclass@gmail.com', 'sweetcaseclass!'
server.login(user_email, user_pass)                                             #Fixes any login issues: https://accounts.google.com/DisplayUnlockCaptcha

homework_number    = input("What homework number are you emailing about?\n").strip()
assert 0 <= int(homework_number) <= 16, 'Invalid homework number inputted -- should be an integer between 0 and 16. Quitting...'
CD_initials        = input("What are the CD Initials for this semester?\n").strip().upper()
assert len(CD_initials) == 4

recipients = get_recipients()

for recipient in recipients:

    #Example email body: https://docs.google.com/document/d/1ZIb9yZK-MxvVsqHYSn7jzIarDoOGT6oZ-0_9DRtYM4M/edit?usp=sharing
    msg = "Hey y'all,\n\n"
    msg+= "Just reaching out to let you know we didn't receive a HW" +homework_number+ " submission from you.\n\n"
    msg+= "If you think this is a mistake, please let us know. Otherwise, please complete last week's homework as soon as you can.\n\n"
    msg+= CD_initials
    
    msg = MIMEText(msg)
    
    msg['Subject'] = '[Action Required] HW' + homework_number + ' Submission Missing'
    msg['From']    = user_email
    msg['To']      = recipient

    server.send_message(msg)
    
print("Reminder emails have been sent!")

server.quit()