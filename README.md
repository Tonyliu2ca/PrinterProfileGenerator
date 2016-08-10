PrinterGenerator
================

This script will generate profile (mobileconfig) for [Munki](https://github.com/munki/munki/wiki) to install a printer.

CSV usage is currently not implemented.

### Command-line options:

A full description of usage is available with:

```
./print_generator.py -h
usage: print_generator.py [-h] [--printername PRINTERNAME] [--driver DRIVER]
                          [--address ADDRESS] [--location LOCATION]
                          [--displayname DISPLAYNAME] [--desc DESC]
                          [--options [OPTIONS [OPTIONS ...]]]
                          [--version VERSION] [--csv CSV]

Generate a Munki nopkg-style pkginfo for printer installation.

optional arguments:
  -h, --help            show this help message and exit
  --printername PRINTERNAME
                        Name of printer queue. May not contain spaces, tabs, #
                        or /. Required.
  --driver DRIVER       Name of driver file in
                        /Library/Printers/PPDs/Contents/Resources/. Can be
                        relative or full path. Required.
  --address ADDRESS     IP or DNS address of printer. If no protocol is
                        specified, defaults to lpd://. Required.
  --location LOCATION   Location name for printer. Optional. Defaults to
                        printername.
  --displayname DISPLAYNAME
                        Display name for printer (and Munki pkginfo).
                        Optional. Defaults to printername.
  --desc DESC           Description for Munki pkginfo only. Optional.

  --version VERSION     Version number of Munki pkginfo. Optional. Defaults to
                        1.0.
```
