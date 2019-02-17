#!/usr/bin/python3
"""Show nicely formatted status, mileage charge percent etc """

import argparse
import logging
import json
import os
import time

from datetime import datetime
from math import radians, sin, cos, acos

from bimmer_connected.account import ConnectedDriveAccount
from bimmer_connected.country_selector import get_region_from_name, valid_regions
from bimmer_connected.vehicle import VehicleViewDirection

def main() -> None:
    """Main function."""
    logging.basicConfig(level=logging.CRITICAL) 

    parser = argparse.ArgumentParser(description='script to show nicely foramted status mileage etc ')
    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.required = True

    status_parser = subparsers.add_parser('status', description='get current status of the vehicle')
    _add_default_arguments(status_parser)
    _add_position_arguments(status_parser)

    args = parser.parse_args()
    args.func(args)


def get_status(args) -> None:
    """Get the vehicle status."""
    account = ConnectedDriveAccount(args.username, args.password, get_region_from_name(args.region))
    if args.lat and args.lng:
        for vehicle in account.vehicles:
            vehicle.set_observer_position(args.lat, args.lng)
    account.update_vehicle_states()

    for vehicle in account.vehicles:
        print ()
        print(vehicle.name)
        """print('VIN: {}'.format(vehicle.vin))"""
        miles = 1.609344
        mileage = int (vehicle.state.mileage / miles)
        print('mileage: {:0}'.format(mileage))
        
        maxRange = vehicle.state.maxRangeElectric / miles
        range = vehicle.state.remainingRangeElectricMls

        print('E-Range: {} miles'.format(range))
        print('Battery: {}%'.format(vehicle.state.chargingLevelHv ))

        position = vehicle.state.position

        """ home location """ 
        hlat = radians (53.429768)
        hlon = radians (-2.757043)

        lat = radians (position["lat"])
        lon = radians (position["lon"])

        dist = 6378 * acos(sin(hlat)*sin(lat) + cos(hlat)*cos(lat)*cos(hlon - lon))
        dist = dist / miles
        if dist > 0 :
           print("Location: %.1f miles from home" % dist )
        else :
           print("Location: home")

        sinceCharge = round( maxRange - range,1)
        print ("Distance since last charge: {} miles" .format(sinceCharge))

        BASE_URL = 'https://{server}/webapi/v1'
        VEHICLES_URL = BASE_URL + '/user/vehicles'
        VEHICLE_VIN_URL = VEHICLES_URL + '/{vin}'
        VEHICLE_TRIP_URL = VEHICLE_VIN_URL + '/statistics/lastTrip'
        response = account.send_request(
            VEHICLE_TRIP_URL.format(server=account.server_url, vin=vehicle.vin), logfilename='status',
            params="")
        lastTrip = response.json()['lastTrip']
        print ()
        print ("Last Trip:")

        date = datetime.strptime(lastTrip['date'],'%Y-%m-%dT%H:%M:%S+0100')
        print (date)
        duration = lastTrip["duration"]
        distance = lastTrip["totalDistance"]
        distance = round (distance / miles ,1)
        print ("{} miles in {} minutes" .format(distance,duration))

	# convert kWh/100km to miles / kWh
        mpk = round (100 / (lastTrip['avgElectricConsumption'] * miles ),2)
        print ("{} mi/kWh" .format(mpk))

        print ("Efficiency: {} /5.0" .format(lastTrip['efficiencyValue'] * 5.0))

def _add_default_arguments(parser: argparse.ArgumentParser):
    """Add the default arguments username, password, region to the parser."""
    parser.add_argument('username', help='Connected Drive user name')
    parser.add_argument('password', help='Connected Drive password')
    parser.add_argument('region', choices=valid_regions(), help='Region of the Connected Drive account')


def _add_position_arguments(parser: argparse.ArgumentParser):
    """Add the lat and lng attributes to the parser."""
    parser.add_argument('lat', type=float, nargs='?', const=0.0,
                        help='optional: your gps latitide (as float)')
    parser.add_argument('lng', type=float, nargs='?', const=0.0,
                        help='optional: your gps longitude (as float)')
    parser.set_defaults(func=get_status)


if __name__ == '__main__':
    main()
