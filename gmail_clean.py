#!/usr/bin/env python
#
#
import sys
import imaplib
import getpass
import email
import email.header
import getopt

import re


import pandas as pd

EMAIL_ACCOUNT = ""
EMAIL_FOLDER = "[Gmail]/All Mail"
password = ''

try:
    opts, args = getopt.getopt(sys.argv[1:],"he:o:p:",["email=","ofile=","pwd="])
except getopt.GetoptError:
    print 'options: -e email -p password'
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print '-p password -e email'
        sys.exit()
    elif opt in ("-p", "--pwd"):
        password = arg
    elif opt in ("-e", "--email"):
        EMAIL_ACCOUNT = arg

output_file = EMAIL_ACCOUNT + ".csv"

if password == '':
    password = getpass.getpass()

addresses = {}
messages = []

def process_mailbox(M):
    """
    Do something with emails messages in the folder.  
    For the sake of this example, print some headers.
    """

    rv, data = M.search(None, "ALL")
    if rv != 'OK':
        print "No messages found!"
        return

    regExp = re.compile('.*<(.*)>')
    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print "ERROR getting message", num
            return

        msg = email.message_from_string(data[0][1])
        frm = msg['From']
        res = regExp.search(frm)
        addr = ''
        if res:
            addr = res.group(1)
        else:
            addr = frm
            
        if addresses.__contains__(addr):
            messages.append(num)
            print num, " ", frm, " will remove"
        else:
            print num, " ", frm, " will keep"


df1 = pd.DataFrame.from_csv(output_file)
df2 = df1[df1.Delete=='y']
addresses = { k for k in df2.index}
  
M = imaplib.IMAP4_SSL('imap.gmail.com')

try:
    rv, data = M.login(EMAIL_ACCOUNT, password )
except imaplib.IMAP4.error:
    print "LOGIN FAILED!!! "
    sys.exit(1)

print rv, data

try:
    rv, mailboxes = M.list()
    if rv == 'OK':
        print "Mailboxes:"
        print mailboxes

    rv, data = M.select(EMAIL_FOLDER)
    if rv == 'OK':
        print "Processing mailbox...\n"
        process_mailbox(M)
        
    else:
        print "ERROR: Unable to open mailbox ", rv

    for num in messages:
        M.store(num,'+X-GM-LABELS', '\\Trash')
        print num, " deleted"

except Exception:
    print "Error!"
    
M.logout()