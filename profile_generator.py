#!/usr/bin/python
import os
import sys
import argparse
import re

from uuid import uuid4

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(sys.argv[0])))

def replace_words(base_text, profile_values):
    for key, val in profile_values.items():
        base_text = base_text.replace(key, val)
    return base_text

parser = argparse.ArgumentParser(description='Generate a Configuration Profile for printer installation.')
parser.add_argument('--printername', help='Name of printer queue. May not contain spaces, tabs, # or /. Required.')
parser.add_argument('--driver', help='Name of driver file in /Library/Printers/PPDs/Contents/Resources/. Can be relative or full path. Required.')
parser.add_argument('--address', help='IP or DNS address of printer. If no protocol is specified, defaults to socket://. Required.')
parser.add_argument('--location', help='Location name for printer. Optional. Defaults to printername.')
parser.add_argument('--displayname', help='Display name for printer (and Munki pkginfo). Optional. Defaults to printername.')
parser.add_argument('--version', help='Version number of Munki pkginfo. Optional. Defaults to 1.0.', default='1.0')
#parser.add_argument('--csv', help='Path to CSV file containing printer info. If CSV is provided, all other options are ignored.')
args = parser.parse_args()
if not args.printername:
    print >> sys.stderr, (os.path.basename(sys.argv[0]) + ': error: argument --printername is required')
    parser.print_usage()
    sys.exit(1)
if not args.driver:
    print >> sys.stderr, (os.path.basename(sys.argv[0]) + ': error: argument --driver is required')
    parser.print_usage()
    sys.exit(1)
if not args.address:
    print >> sys.stderr, (os.path.basename(sys.argv[0]) + ': error: argument --address is required')
    parser.print_usage()
    sys.exit(1)

if re.search(r"[\s#/]", args.printername):
    # printernames can't contain spaces, tabs, # or /.  See lpadmin manpage for details.
    print >> sys.stderr, ("ERROR: Printernames can't contain spaces, tabs, # or /.")
    sys.exit(1)

if args.displayname:
    displayName = args.displayname
else:
    displayName = str(args.printername)

if args.location:
    location = args.location
else:
    location = args.printername

if args.version:
    version = str(args.version)
else:
    version = "1.0"

#if args.options:
#    optionsString = getOptionsString(args.options[0])
#else:
#    optionsString = ''

if args.driver.startswith('/Library'):
    # Assume the user passed in a full path rather than a relative filename
    driver = args.driver
else:
    # Assume only a relative filename
    driver = os.path.join('/Library/Printers/PPDs/Contents/Resources', args.driver)

if '://' in args.address:
    # Assume the user passed in a full address and protocol
    address = args.address
else:
    # Assume the user wants to use the default, socket://
    address = 'socket://' + args.address

#profile = open("AddPrinter_" + args.printername + "_" + version + '.mobileconfig', 'w')
template = open(os.path.relpath("Template_Profile.mobileconfig"))

uuid1 = str(uuid4())
uuid2 = str(uuid4())
model = driver.rsplit('/', 1)[1][:-4]


replacements = {"$UUID1$": uuid1, "$UUID2$": uuid2, "$PRINTERNAME$": args.printername, "$DISPLAYNAME$": displayName, "$LOCATION$":location, "$VERSION$":version, "$PPD$":driver,"$URI$":address, "$MODEL$": model}
#print model
#with open("Template_Profile.mobileconfig") as template, open("AddPrinter_" + args.printername + "_" + version + '.mobileconfig', 'w') as profile:
tempprofile = template.read()
newprofile = replace_words(tempprofile, replacements)


profile = open("AddPrinter_" + args.printername + "_" + version + '.mobileconfig', 'w')
profile.write(newprofile)
profile.close()
template.close()
#print len(replacements)
