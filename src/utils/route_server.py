#!/usr/bin/env python3
import json
import os

import requests
from prettytable import PrettyTable
#from dotenv import load_dotenv

from utils.config import ProjectConfig

#load_dotenv()


class RouteServerInteraction(object):

    def __init__(self):
        self.config = ProjectConfig().c
        self.route_servers = {
            "SYD": {
                "rs1": {
                    "url": self.config.get("SYD_RS1")
                },
                "rs2": {
                    "url": self.config.get("SYD_RS2")
                }
            },
            "MEL": {
                "rs1": {
                    "url": self.config.get("MEL_RS1")
                },
                "rs2": {
                    "url": self.config.get("MEL_RS2")
                }
            },
            "ADL": {
                "rs1": {
                    "url": self.config.get("ADL_RS1")
                },
                "rs2": {
                    "url": self.config.get("ADL_RS2")
                }
            },
            "BNE": {
                "rs1": {
                    "url": self.config.get("BNE_RS1")
                },
                "rs2": {
                    "url": self.config.get("BNE_RS2")
                }
            },
            "PER": {
                "rs1": {
                    "url": self.config.get("PER_RS1")
                },
                "rs2": {
                    "url": self.config.get("PER_RS2")
                }
            },
            "DRW": {
                "rs1": {
                    "url": self.config.get("DRW_RS1")
                    }
                },
            "HBA": {
                "rs1": {
                    "url": self.config.get("HBA_RS1")
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
        # Check if ASN is Valid
        if isinstance(asn, str):
            asn = self._int_convert(asn)
            if not asn:
                return "Please enter a valid ASN!", "Response"
        
        # Cheeky
        if asn == 1221:
            return "The day Telstra peer on EdgeIX Route Servers is the day Joe shaves his beard..", "No Chance"

        data = self.check_asn(asn)

        # ASN isnt present on any Route Servers
        if len(data) == 0:
            response = f"AS{asn} is not present on any Route Servers.. perhaps they should email peering@edgeix.net?"
            return response, "Response"

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
                if route_server_data.get("error") is not None:
                    continue
                for asn, asn_data in route_server_data["data"]["protocols"].items():
                    if asn_data.get("neighbor_as") == checked_asn:
                        if location not in response:
                            response[location] = {
                                route_server: {
                                    "asn": checked_asn,
                                    "name": asn_data.get("description"),
                                    "state": asn_data.get("state")
                                }
                            }
                        
                        if route_server not in response[location]:
                            response[location][route_server] = {
                                "asn": checked_asn,
                                "name": asn_data.get("description"),
                                "state": asn_data.get("state")
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
                str: Header containing ASN & readable name
        """
        table = PrettyTable()
        table.field_names = ["City", "Route Server", "BGP State"]
        for location, location_data in data.items():
            for route_server, route_server_data in location_data.items():
                table.add_row(
                    [
                        location, 
                        route_server, 
                        route_server_data["state"]
                    ]
                )
        return f"```{table}```", route_server_data["name"]

    def is_peer(self, asn: int) -> bool:
        """
            Check if a given ASN is a Configured Peer
            of any Route Server

            Arguments:
                asn (int): ASN to check
            
            Returns:
                bool: True if ASN exists
        """
        if isinstance(asn, str):
            asn = self._int_convert(asn)
            if not asn:
                return False

        return True if asn in self.asns.keys() else False
    
    def peers_by_location(self, location: str) -> list:
        """
            Return a list of peers for a given City

            Arguments:
                location (str): Location key
            
            Return:
                list: List of Descriptions from the Route Servers
                in the given Cities peering sessions
        """
        data = self.route_servers.get(location.upper())

        response = [
            entry.get("description")
            for rs, rsd in data.items() if not rsd.get("error", False) for key, entry in rsd["data"]["protocols"].items()
        ]
        return list(set(response))
    
    def is_valid_location(self, location: str) -> bool:
        """
            Check if a Route Server location is valid

            Arguments:
                location (str): Location key to validate
            
            Return:
                bool: True if exists
        """
        return True if self.route_servers.get(location.upper()) is not None else False

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
                    rsd["data"] = requests.get(rsd.get("url")).json()
                except (requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, json.decoder.JSONDecodeError):
                    rsd["error"] = True

        return self.route_servers

    @property
    def asns(self) -> dict:
        """
            Property object to return nested dict
            containing locations an ASN is present
            on the Route Servers
            
            Return:
                dict: Keyed by ASN, containing
                description & locations present
        """
        asns = {}

        for loc, data in self.route_servers.items():
            for rs, rsd in data.items():
                if rsd.get("data") is not None:
                    for _, asn_data in rsd["data"]["protocols"].items():
                        asn = asn_data.get("neighbor_as")
                        if asn is not None:
                            locs = asns[asn].get("locs", []) if asns.get(asn) is not None else []
                            locs.append(f"{loc} - {rs}")
                            asns.update(
                                {
                                    asn: {
                                        "descr": asn_data.get("description"),
                                        "locs": locs
                                    } 
                                }
                            )
        return asns
    
    @property
    def ips(self) -> dict:
        """
            Property object to return nested dict
            containing allocated IP to ASN & Location
            mapping
            
            Return:
                dict: Keyed by IP, containing
                description & location
        """
        ips = {}

        for loc, data in self.route_servers.items():
            for rs, rsd in data.items():
                if rsd.get("data") is not None:
                    for _, asn_data in rsd["data"]["protocols"].items():
                        ip = asn_data.get("neighbor_address")
                        if ip is not None:
                            ips.update(
                                {
                                    ip: {
                                        "descr": asn_data.get("description"),
                                        "loc": loc
                                    } 
                                }
                            )
        return ips

    @property
    def locations(self) -> list:
        """
            Property object to return all available locations

            Return:
                list: List of keys from self.route_servers
        """
        return set(list(self.route_servers.keys()))
    
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
