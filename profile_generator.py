#!/usr/bin/python
'''
Generates Printer Profile
'''
# Libraries
import os
import argparse
import gzip
import subprocess
from plistlib import writePlist
from uuid import uuid4

path = os.path.dirname(os.path.abspath(__file__))
postinstall_script = os.path.join(path, "postinstall.py")
def main():
    '''
        Main Function
    '''
    # Variables
    profileuuid = str(uuid4())
    payloaduuid = str(uuid4())
    _options = {}

    # Parser Options
    parser = argparse.ArgumentParser(
        description='Generate a Configuration Profile for printer installation.')
    parser.add_argument(
        '--printername',
        help='Name of printer queue. May not contain spaces, tabs,'
        '# or /. Required.',
        required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--driver',
        help='Name of driver file in'
        '/Library/Printers/PPDs/Contents/Resources/.'
        'Can be relative or full path. Required OR use --generic.')
    group.add_argument('--generic', help='Use the Generic'
                                         'Postscript Printer driver. Required OR' \
                                         'use --driver /PATH/TO/Driver .',
                       action='store_true')
    parser.add_argument(
        '--address',
        help='IP or DNS address of printer.'
        'If no protocol is specified, defaults to socket://.'
        'Required.',
        required=True)
    parser.add_argument(
        '--location',
        help='Location name for printer.'
        'Optional. Defaults to printername.')
    parser.add_argument(
        '--displayname',
        help='Display name for printer (and Munki pkginfo).'
        'Optional. Defaults to printername.')
    parser.add_argument(
        '--version',
        help='Version number of Munki pkginfo.'
        'Optional. Defaults to 1.0.',
        default='1.0')
    parser.add_argument(
        '--organization',
        help='Change Organization of Profile.'
        'Defaults to GitHub',
        default="GitHub")
    parser.add_argument(
        '--identifier',
        help='Change Profile + Payload Identifier before uuid.'
        'Payload UUID is appended to ensure it is unique.'
        'Defaults to com.github.wardsparadox',
        default="com.github.wardsparadox")
    parser.add_argument(
        '--option',
        help='Add an option in addition to the "printer is shared" option.'
        'Bool values must be in True or False form.',
        action='append')
    parser.add_argument(
        '--munkiimport',
        help='Use munkiimport tools to import profile to munki_repo',
        action='store_true')

#    parser.add_argument('--csv', help='Path to CSV file containing printer info.'
#                                      'If CSV is provided, all other options are ignored.')

    # Main
    args = parser.parse_args()
    printername = str(args.printername).replace('-', '_')
    if args.displayname:
        displayName = args.displayname
    else:
        displayName = str(printername)

    if args.location:
        location = args.location
    else:
        location = printername

    if args.version:
        version = str(args.version)
    else:
        version = "1.0"

    if args.generic:
        driver = "/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/PrintCore.framework/Versions/A/Resources/Generic.ppd"
        with open(driver, 'rb') as ppd:
            for line in ppd:
                if "*NickName:" in line:
                    model = line.split('"')[1]
            ppd.close()
    if args.driver:
        if args.driver.startswith('/Library'):
            # Assume the user passed in a full path rather than a relative filename
            driver = args.driver
            with gzip.open(driver, 'rb') as ppd:
                for line in ppd:
                    if "*NickName:" in line:
                        model = line.split('"')[1]
                ppd.close()
        else:
            # Assume only a relative filename
            driver = os.path.join('/Library/Printers/PPDs/Contents/Resources',
                                  args.driver)
            with gzip.open(driver, 'rb') as ppd:
                for line in ppd:
                    if "*NickName:" in line:
                        model = line.split('"')[1]
                ppd.close()

    if '://' in args.address:
        # Assume the user passed in a full address and protocol
        address = args.address
    else:
        # Assume the user wants to use the default, socket://
        address = 'socket://' + args.address

    if "wardsparadox" in args.identifier:
        profileidentifier = "com.github.wardsparadox.{0}".format(profileuuid)
        payloadidentifier = "com.github.wardsparadox.{0}".format(payloaduuid)
    else:
        profileidentifier = args.identifier
        payloadidentifier = "{0}.{1}".format(args.identifier, payloaduuid)

    if args.option:
        for option in args.option:
            item = option.split('=')
            _options[item[0]] = item[1]

    _options["printer-is-shared"] = False

    # Actual Printer Info
    Printer = {}
    _printer = {}
    _printer["DeviceURI"] = address
    _printer["DisplayName"] = displayName
    _printer["Location"] = location
    _printer["Model"] = model
    _printer["PPDURL"] = driver
    _printer["PrinterLocked"] = False
    _printer["Option"] = _options
    Printer[printername] = _printer

    # Payload Content
    _payload = {}
    _payload["PayloadDisplayName"] = "Printing"
    _payload["PayloadEnabled"] = True
    _payload["PayloadIdentifier"] = payloadidentifier
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
    filename = "AddPrinter_{0}.mobileconfig".format(printername)

    writePlist(Profile, filename)
    if args.munkiimport:
        munkiimport = "/usr/local/munki/munkiimport"
        try:
            if os.path.isfile(munkiimport):
                pass
        except Exception as e:
            raise "Munki Admin Tools Not Installed!"
        script = """#!/usr/bin/python
from subprocess import call, check_output
import os
printertoremove = '{0}'
for line in check_output(['/usr/bin/lpstat', '-a']).split(os.linesep)[:-1]:
    queuename = line.split()[0]
    printer = check_output(['/usr/bin/lpoptions', '-p', queuename])
    if printertoremove in printer:
        print queuename, 'is printer needed to remove'
    print call(['/usr/sbin/lpadmin', '-x', queuename])
""".format(displayName)
        scriptfilename = printername+"_uninstallscript.py"
        with open(scriptfilename, "w") as scriptfile:
            scriptfile.write(script)
        mi_cmd = [munkiimport, "--postuninstall_script={}".format(scriptfilename), \
        "--postinstall_script={}".format(postinstall_script), filename]
        mi = subprocess.Popen(mi_cmd)
        mi.wait()
        scriptfile.close()
        os.remove(scriptfile)

if __name__ == "__main__":
    main()
