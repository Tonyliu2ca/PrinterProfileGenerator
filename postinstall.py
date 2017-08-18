#!/usr/bin/python
'''
Refreshes MCX for all users in /Users
'''
from os import listdir
from subprocess import call

for user in listdir('/Users'):
    if user != "Shared" and user != ".localized":
        print user
        call(['/usr/bin/mcxrefresh', '-n', user])


print "All Users mcxprinters refreshed!"
