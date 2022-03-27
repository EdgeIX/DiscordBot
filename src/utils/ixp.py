#!/usr/bin/env python3
from utils.config import ProjectConfig


class IXPManager(object):

    def __init__(self):
        self.config = ProjectConfig().c
        self.data = {}
        self.asns = {}
        self.ixp_id = {}

    def make_ixp_dict(self):
        """
        Maintain mapping of IXP ID to user friendly name
        """
        for ixp in self.data["ixp_list"]:
            self.ixp_id.update({ixp["ixp_id"]: {
                "name": ixp["shortname"],
            }})
        
        return
    
    def get_asn_data(self, asn: int) -> dict:
        """
        Iterate all IXPM Peers for a given ASN

        Arguments:
            asn (int): AS Number
        
        Return:
            dict: JSON Blob from IXPM
        """
        for peer in self.data["member_list"]:
            if peer.get("asnum") == asn:
                return peer
        return None
    
