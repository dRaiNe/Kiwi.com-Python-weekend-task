#!/usr/bin/python3
# by Leos Navratil
# Python 3 version 3.5.2

import os
import sys
import http.client
import signal
import argparse
import string
import re
import zlib
import enum
import urllib.request
import xml.etree.ElementTree as ET
import http.client
import bencodepy
import ipaddress
import struct
import hashlib

class err_code(enum.IntEnum):
	OK					= 0
	ERR_PARAMS			= 1
	ERR_GENERAL			= 2
	ERR_BAD_RESPONSE	= 3

# International airport codes LUT
# ./book_flight.py --date 2017-10-13 --from BCN --to DUB --one-way
# ./book_flight.py --date 2017-10-13 --from LHR --to DXB --return 5
# ./book_flight.py --date 2017-10-13 --from NRT --to SYD --cheapest
# ./book_flight.py --date 2017-10-13 --from CPH --to MIA --shortest

try:
	parser = argparse.ArgumentParser(add_help=False)

	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-r', '--rss', help='', action='store', metavar='rssUrl')
	group.add_argument('-i', '--input-announcement', help='', action='store', metavar='inputAnnouncementFile')
	# expansion
	group.add_argument('-t', '--torrent-file', help='', action='store', metavar='torrentFile')
	# also take care of misspelled param, as in assignment
	parser.add_argument('-a', '--tracker-announce-url', '--tracker-annonce-url', help='', action='store', metavar='trackerAnnounceUrl')

	try:
		args = parser.parse_args()
	except SystemExit:
		# incorrect arguments, exit with error code 1
		sys.exit(int(err_code.ERR_PARAMS))

