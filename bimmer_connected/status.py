#!/usr/bin/python3
"""Show nicely formatted status, mileage charge percent etc """

import argparse
import logging
import json
import os
import time
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
        print
        print(vehicle.name)
        """print('VIN: {}'.format(vehicle.vin))"""
        miles = 1.609
        mileage = int (vehicle.state.mileage / miles)
        print('mileage: {:0}'.format(mileage))
        
        """
        print('vehicle properties:')
        print(json.dumps(vehicle.attributes, indent=4))
        print('vehicle status:')
        print(json.dumps(vehicle.state.attributes, indent=4))
        """
        print('E-Range: {} miles'.format(vehicle.state.remainingRangeElectricMls ))
        print('Battery: {}%'.format(vehicle.state.chargingLevelHv ))


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
