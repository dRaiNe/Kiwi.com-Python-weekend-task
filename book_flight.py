#!/usr/bin/python3
# by Leos Navratil
# Python 3 version 3.5.2

import sys
import argparse
import enum
import time
import requests
import json

# debug -> pprint(vars(args))
from pprint import pprint

class err_code(enum.IntEnum):
	OK					= 0
	ERR_PARAMS			= 1
	ERR_GENERAL			= 2
	ERR_BAD_RESPONSE	= 3

# International airport codes LUT (IATA codes)
# search flights | book

# ./book_flight.py --date 2017-10-13 --from BCN --to DUB --one-way
# ./book_flight.py --date 2017-10-13 --from LHR --to DXB --return 5
# ./book_flight.py --date 2017-10-13 --from NRT --to SYD --cheapest
# ./book_flight.py --date 2017-10-13 --from CPH --to MIA --shortest

# output <- PNR num

try:
	parser = argparse.ArgumentParser(add_help=False)

	parser.add_argument('--date', required=True, action='store', metavar='DATE')
	parser.add_argument('--from', required=True, action='store', metavar='DESTINATION', dest='fromDest')
	parser.add_argument('--to', required=True, action='store', metavar='DESTINATION', dest='toDest')

	wayGroup = parser.add_mutually_exclusive_group()
	wayGroup.add_argument('--one-way', required=False, action='store_true')
	wayGroup.add_argument('--return', required=False, action='store', type=int, dest='returnNum')

	cheapestOrShortestGroup = parser.add_mutually_exclusive_group()
	cheapestOrShortestGroup.add_argument('--cheapest', required=False, action='store_true')
	cheapestOrShortestGroup.add_argument('--shortest', required=False, action='store_true')

	try:
		args = parser.parse_args()
	except SystemExit:
		# incorrect arguments, exit with error code 1
		sys.exit(int(err_code.ERR_PARAMS))


	if args.fromDest == args.toDest:
		print('[ERROR] From and To destinations cannot be the same.')
		sys.exit()

	try:
		validDate = time.strptime(args.date, '%Y-%m-%d')
	except ValueError:
		print('Submitted date is invalid!')

	# TODO: verify dest args against look-up-table or web API
	# prepare IATA codes LUT
	#airportCodes = requests.get('https://api.skypicker.com/places?id=dub&v=3')
	#airportCodes = airportCodes.json()

	#lut = {}
	#for item in airportCodes:
	#	lut[item['id']] = item

	# process
	if args.shortest == True:
		# search for the shortest route
		# convert to string
		sort = 'duration'

	else:
		# fallback (default = cheapest route)
		sort = 'price'

	# fire search request
	convertedDate = time.strftime('%d/%m/%Y', validDate)

	url = 'https://api.skypicker.com/flights?flyFrom=' + args.fromDest + '&dateFrom=' + convertedDate + '&dateTo=' + convertedDate + '&to=' + args.toDest + '&sort=' + sort
	if args.returnNum is not None:
		# e.g. return 5 -> append params for return (two-way) flight
		url = url + '&daysInDestinationTo=' + (str)(args.returnNum) + '&daysInDestinationFrom=' + (str)(args.returnNum)

	r = requests.get(url)
	# book through API, use passenger placeholder
	passengers = list()
	passengers.append(dict({
			"firstName": "FirstName",
			"lastName": "LastName",
			"title": "Mr",
			"birthday": "1990-1-1",
			"documentID": "",
			"email": "mail1@gmail.com"}))

	template = {
		"booking_token" : r.json()['data'][0]['booking_token'],
		"currency" : "USD",
		"passengers" : passengers
	}

	req = requests.post('http://37.139.6.125:8080/booking', json=template)
	res = json.loads(req.text)

	# output PNR
	print(res['pnr'])

except KeyboardInterrupt:
	# catch SIGINT properly and shut down
	print('\n')
	sys.exit()