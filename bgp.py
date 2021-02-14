#!/usr/bin/env python3
import json
import os

import requests
from prettytable import PrettyTable
from dotenv import load_dotenv

load_dotenv()


class RouteServerInteraction(object):

    def __init__(self):
        self.route_servers = {
            'SYD': {
                'rs1': {
                    'url': os.getenv('SYD_RS1')
                },
                'rs2': {
                    'url': os.getenv('SYD_RS2')
                }
            },
            'MEL': {
                'rs1': {
                    'url': os.getenv('MEL_RS1')
                },
                'rs2': {
                    'url': os.getenv('MEL_RS2')
                }
            },
            'ADL': {
                'rs1': {
                    'url': os.getenv('ADL_RS1')
                },
                'rs2': {
                    'url': os.getenv('ADL_RS2')
                }
            },
            'BNE': {
                'rs1': {
                    'url': os.getenv('BNE_RS1')
                },
                'rs2': {
                    'url': os.getenv('BNE_RS2')
                }
            },
            'PER': {
                'rs1': {
                    'url': os.getenv('PER_RS1')
                },
                'rs2': {
                    'url': os.getenv('PER_RS2')
                }
            }
        }

        # Load data on init
        self.get_responses()
    
    def on_message(self, asn: int) -> PrettyTable:
        """
            Function called from Discord Bot message

            Arguments:
                asn (int): AS Number
            
            Return:
                PrettyTable: Formatted table containing
                location, route server, ASN & BGP state
        """
        if isinstance(asn, str):
            asn = self._int_convert(asn)
            if not asn:
                return 'Please enter a valid ASN!'

        data = self.check_asn(asn)
        return self.parse(data)
        
    
    def get_responses(self) -> None:
        """
            Load latest data from Inner Function
        """
        return self._load_bird_data()
    
    def check_asn(self, checked_asn: int) -> dict:
        """
            Remove ASN role from User, if present

            Arguments:
                checked_asn (int): AS Number
            
            Return:
                dict: Nested dict containing state & ASN information
        """
        # load latest data
        data = self.get_responses()
        response = {}

        # Get state per route server in each location for the specific ASN
        for location, location_data in data.items():
            for route_server, route_server_data in location_data.items():
                # Check if route server is currently down/in an errored state
                if route_server_data.get('error') is not None:
                    continue
                for asn, asn_data in route_server_data['data']['protocols'].items():
                    if asn_data.get('neighbor_as') == checked_asn:
                        if location not in response:
                            response[location] = {
                                route_server: {
                                    'asn': checked_asn,
                                    'name': asn_data.get('description'),
                                    'state': asn_data.get('state')
                                }
                            }
                        
                        if route_server not in response[location]:
                            response[location][route_server] = {
                                'asn': checked_asn,
                                'name': asn_data.get('description'),
                                'state': asn_data.get('state')
                            }
        return response
    
    def parse(self, data: dict) -> PrettyTable:
        """
            Parse into a table format

            Arguments:
                data (dict): Nested dict containing state & ASN information
            
            Return:
                PrettyTable: Formatted table containing
                location, route server, ASN & BGP state
        """
        table = PrettyTable()
        table.field_names = ['City', 'RS', 'Description', 'State']
        for location, location_data in data.items():
            for route_server, route_server_data in location_data.items():
                table.add_row(
                    [
                        location, 
                        route_server, 
                        route_server_data['name'],
                        route_server_data['state']
                    ]
                )
        return table
    
    def _load_bird_data(self) -> dict:
        """
            Inner function to obtain data from IXPM, adds
            data into self.route_servers
            
            Return:
                dict: Latest version of the
                route server data
        """
        for loc, loc_data in self.route_servers.items():
            for rs, rsd in loc_data.items():
                try:
                    rsd['data'] = requests.get(rsd.get('url')).json()
                except requests.exceptions.ConnectionError:
                    rsd['data'] = 'Route Server Unavailable'
                    rsd['error'] = True
        return self.route_servers
    
    def _int_convert(self, item: str) -> int:
        """
            Attempt to convert str to int

            Arguments:
                item (str): String to convert
            
            Return:
                int/bool: Int if success, False if failure
        """
        try:
            return int(item)
        except ValueError:
            return False
