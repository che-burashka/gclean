#!/usr/bin/env python

# use this one to scan your gmail mailbox and compile a list of 'from' addresses (with counts)
# edit this list using your favorite spreadsheet app and then use gmail_clean.py to move all messages from 
# selected senders to trash

import sys
import imaplib
import getpass
import email
import email.header
import getopt

import re


import pandas as pd

EMAIL_ACCOUNT = "andrei.goloubentsev@gmail.com"
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
       
        if addresses.has_key(addr):
            addresses.update({addr:addresses[addr]+1})
        else:
            addresses.update({addr:1})
        
        print addr,addresses[addr]
  
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
        M.close()
    else:
        print "ERROR: Unable to open mailbox ", rv



    M.logout()

    dat = [ (addresses[k],'n') for k in addresses.keys() ]
    idx = [ k for k in addresses.keys() ]
    df1 =pd.DataFrame(data=dat,columns=['Count','Delete'],index=idx)
    df1 = df1.sort('Count',ascending=False)
    df1.to_csv(output_file)

except Exception:
    print "Error!"
