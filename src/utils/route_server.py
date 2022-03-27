#!/usr/bin/env python3
import json
import os

import requests
from prettytable import PrettyTable

from utils.config import ProjectConfig


class RouteServerInteraction(object):

    def __init__(self):
        self.config = ProjectConfig().c
        self.route_servers = self.config["ROUTE_SERVERS"]
        self.data = {}
    
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
    
    def peers_by_location(self, location: str) -> list:
        """
            Return a list of peers for a given City

            Arguments:
                location (str): Location key
            
            Return:
                list: List of Descriptions from the Route Servers
                in the given Cities peering sessions
        """
        data = self.data

        response = [
            entry.get("description")
            for rs, rsd in data.items() if not rsd.get("error", False) for key, entry in rsd["data"]["protocols"].items()
        ]
        return list(set(response))
    
    # Moved to enums
    # def is_valid_location(self, location: str) -> bool:
    #     """
    #         Check if a Route Server location is valid

    #         Arguments:
    #             location (str): Location key to validate
            
    #         Return:
    #             bool: True if exists
    #     """
    #     return True if self.route_servers.get(location.upper()) is not None else False

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
