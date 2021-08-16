#!/usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=4
#
# RaceDB QLLabels Python Script
#
# Usage
# In the RaceDB System Info Edit screen:
#
#   Cmd used to print Bib Tag (parameter is PDF file)
#
#       [  /home/RaceDB/scripts/QLLABELS.py $1 ]
# 
# This script will convert the PDF file to Brother Raster file(s) and 
# send the Raster file(s) to a Brother QL style label printer or to 
# the qlmuxd printer spooler.
# 
# Sending the files directly to the printers on port 9100 works, but 
# only when # there is only a single person using RaceDB. Multiple prints 
# to a QL printer will result in over lapping labels.
#
# The qlmuxd program manages pools of QL printers and will spool
# the data allowing multiple people to print to them, with support
# for different printers for the different antennas and fall-over
# support if (when) the printers are not available (typically when
# they run out of labels. The qlmuxd program takes the same raster
# file data that would be sent to the printers on port 9100, but
# uses ports 910N to allow us to specify which pool of printers
# to use.
#
# This script will get labels printed (either directly or via qlmuxd) 
# far faster than CUPS using the standard Brother QL support files.
#
# This script will:
#
#   1. Convert $1 to $1-$PAGENO.png for each page in the PDF file
#   2. Convert each page to $1-$PAGENO.rast
#   3. Equivalent of cat $1-*.rast | netcat $PRINTER_HOST $PRINTER_PORT
#
#
# The argument provided is the file name which contains information about what is to 
# be printed. E.g.:
#
#       230489203498023809_bib-356_port-8000_antenna-2_type-Frame.pdf
#
# "type" is one of Frame, Body, Shoulder or Emergency.
# "port" is the RaceDB server port.
# "antenna" is the antenna of the user.
#
# The combination of server port and antenna allows different printers to 
# be used for different registration stations. The server port refers to
# the TCP port that the server responds to, e.g. 8000 or 8001 etc.
#

import sys
import os
import socket
import subprocess

import pdf2image
from pdf2image import convert_from_path

fname = sys.argv[1]

# Split file name apart to get information about the label.
# Numeric fields are converted to numbers to allow comparisons like params['antenna'] == 1

print('fname: %s' % (fname))
# 230489203498023809_bib-719_port-8000_antenna-0_type-Frame.pdf

params = { k:(int(v) if v.isdigit() else v) for k, v in (p.split('-') for p in os.path.splitext(fname)[0].split('_')[1:] ) }
print('params: %s' % (params))

# debug
# print '\n'.join( '{}={}'.format(k,v if isinstance(v,int) else "'{}'".format(v)) for k, v in params.items() )

# determine printer destination by label type.  Can also use 'type', 'port' and 'antenna'.

# XXX need to generalize this to support direct to printers
#
# If qlmuxd is used we send the data to host qlmuxd with a port that specifies which printer pool:
#
#   pool    port
#   small1  9101
#   small2  9102
#   large1  9103
#   large1  9104
#
# For direct to printers, we just need a hostname and the port will be 9100
#

#host = 'qlmuxd'
host = '127.0.0.1'

# get pool, model and labelsize using the label type
#
if params['type'] in ('Frame', 'Shoulder', 'Emergency'):
    pool = 'small'
    model = 'QL-710W'
    labelsize='62x100'
    width = 696
    height = 1109
    resolution = 300
else:
    pool = 'large'
    model = 'QL-1060N'
    labelsize='102x152'
    width = 1164
    height = 1660
    resolution = 300

# use antenna to change the pool, e.g. small becomes small1 or small2
#
if params['antenna'] in ('1', '2'):
    pool += '1'
elif params['antenna'] in ('3', '4'):
    pool += '2'
else:
    pool += '1'

# based on pool, get the tcp port to send the raster data to
#
if pool == 'small1':
    port = 9101
elif pool == 'small2':
    port = 9102
elif pool == 'large1':
    port = 9103
elif pool == 'large2':
    port = 9104


# convert PDF to PNG images using pdf2image (poppler)
#images = convert_from_path(fname, size=(696,1109), dpi=280, grayscale=True)
#images = convert_from_path(fname, size=(1109, 696), dpi=280, grayscale=True)
images = convert_from_path('/dev/stdin', size=(1109, 696), dpi=280, grayscale=True)
last = 0
for index, image in enumerate(images):
    image.save(f'/tmp/{fname}-{index}.png')
    last = index
print('last: %d' % last)

# convert PNG images to Brother Raster file, --no-cut for 0..N-1, the last file will
# have a cut so that multiple labels will be kept together.
#
if last >= 1:
    for index in range(0, last):
        print('image: %d NO-CUT' % index)
        subprocess.check_call(['brother_ql_create', '--rotate', '90', '--model', model, '--label-size', labelsize, '--no-cut', f'/tmp/{fname}-{index}.png', f'/tmp/{fname}-{index}.rast' ]) ;
print('image: %d CUT' % last)
subprocess.check_call(['brother_ql_create', '--rotate', '90', '--model', model, '--label-size', labelsize, f'/tmp/{fname}-{last}.png', f'/tmp/{fname}-{last}.rast' ]) ;

# Send *.rast to qlmuxd or direct to printer
#
print('host: %s port: %d' % (host, port))
s = socket.socket()
s.connect((host, port))
for index in range(0, last+1):
    with open(f'/tmp/{fname}-{index}.rast', "rb") as f:
        while True:
            bytes_read = f.read(4096)
            if not bytes_read:
                break
            s.sendall(bytes_read)
s.close()

# remove the intermediate files
#
#for index in range(0, last):
#    os.remove('/tmp/{fname}-{index}.png')
#    os.remove('/tmp/{fname}-{index}.rast')

