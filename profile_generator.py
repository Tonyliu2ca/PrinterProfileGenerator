#!/usr/bin/python
'''
Generates Printer Profile
'''
# Libraries
import os
import sys
import argparse
import re
from plistlib import writePlist
from uuid import uuid4


# Variables
profileuuid = str(uuid4())
payloaduuid = str(uuid4())

# Parser Options
parser = argparse.ArgumentParser(description='Generate a Configuration Profile for printer installation.')
parser.add_argument('--printername', help='Name of printer queue. May not contain spaces, tabs, # or /. Required.')
parser.add_argument('--driver', help='Name of driver file in /Library/Printers/PPDs/Contents/Resources/. Can be relative or full path. Required.')
parser.add_argument('--address', help='IP or DNS address of printer. If no protocol is specified, defaults to socket://. Required.')
parser.add_argument('--location', help='Location name for printer. Optional. Defaults to printername.')
parser.add_argument('--displayname', help='Display name for printer (and Munki pkginfo). Optional. Defaults to printername.')
parser.add_argument('--version', help='Version number of Munki pkginfo. Optional. Defaults to 1.0.', default='1.0')
parser.add_argument('--organization', help='Change Organization of Profile. Defaults to GitHub', default="GitHub")
parser.add_argument('--identifier', help='Change Profile + Payload Identifier before uuid. Payload UUID is appended to ensure it is unique. Defaults to com.github.wardsparadox', default="com.github.wardsparadox")
# Removed CSV for now.
#parser.add_argument('--csv', help='Path to CSV file containing printer info. If CSV is provided, all other options are ignored.')

# Main

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
    model = driver.rsplit('/', 1)[1].split('.', 1)[0]
else:
    # Assume only a relative filename
    driver = os.path.join('/Library/Printers/PPDs/Contents/Resources', args.driver)
    model = args.driver.split('.',1)[0]

if '://' in args.address:
    # Assume the user passed in a full address and protocol
    address = args.address
else:
    # Assume the user wants to use the default, socket://
    address = 'socket://' + args.address

if args.identifier:
    profileidentifier = args.identifier
else:
    profileidentifier = "com.github.wardsparadox.{0}".format(profileuuid)

# Actual Printer Info
Printer = {}
_printer = {}
_printer["DeviceURI"] = address
_printer["DisplayName"] = displayName
_printer["Location"] = location
_printer["Model"] = model
_printer["PPDURL"] = driver
_printer["PrinterLocked"] = False
Printer[args.printername] = _printer


# Payload Content
_payload = {}
_payload["PayloadDisplayName"] = "Printing"
_payload["PayloadEnabled"] = True
_payload["PayloadIdentifier"] = "com.github.wardsparadox.{0}".format(payloaduuid)
_payload["PayloadType"] = "com.apple.mcxprinting"
_payload["PayloadUUID"] = payloaduuid
_payload["PayloadVersion"] = 1
_payload["UserPrinterList"] = Printer

# Profile info
_profile = {}
_profile["PayloadDisplayName"] = "{0} Printer Profile {1}".format(displayName, version)
_profile["PayloadIdentifier"] = profileidentifier
_profile["PayloadOrganization"] = args.organization
_profile["PayloadRemovalDisallowed"] = False
_profile["PayloadScope"] = "System"
_profile["PayloadType"] = "Configuration"
_profile["PayloadUUID"] = profileuuid
_profile["PayloadVersion"] = 1
_profile["PayloadContent"] = [_payload]

# Complete Profile
Profile = _profile

#replacements = {"$UUID1$": uuid1, "$UUID2$": uuid2, "$PRINTERNAME$": args.printername, "$DISPLAYNAME$": displayName, "$LOCATION$":location, "$VERSION$":version, "$PPD$":driver,"$URI$":address, "$MODEL$": model}
#print model
#with open("Template_Profile.mobileconfig") as template, open("AddPrinter_" + args.printername + "_" + version + '.mobileconfig', 'w') as profile:
#tempprofile = template.read()
#newprofile = replace_words(tempprofile, replacements)


#profile = open("AddPrinter_" + args.printername + "_" + version + '.mobileconfig', 'w')
#profile.write(newprofile)
#profile.close()
#template.close()
#print len(replacements)
writePlist(Profile, "AddPrinter_{0}_{1}.mobileconfig".format(args.printername, version))
