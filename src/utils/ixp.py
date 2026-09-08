#!/usr/bin/env python3
class IXPManager(object):

    def __init__(self, config=None):
        self.config = config or {}
        self.data = {}
        self.asns = {}
        self.ixp_id = {}

    def make_ixp_dict(self):
        """
        Maintain mapping of IXP ID to user friendly name
        """
        self.ixp_id = {}
        for ixp in self.data.get("ixp_list", []):
            if not isinstance(ixp, dict) or "ixp_id" not in ixp:
                continue
            self.ixp_id.update({ixp["ixp_id"]: {
                "name": ixp.get("shortname", str(ixp["ixp_id"])),
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
        for peer in self.data.get("member_list", []):
            try:
                peer_asn = int(peer.get("asnum"))
            except (AttributeError, TypeError, ValueError):
                continue
            try:
                requested_asn = int(asn)
            except (TypeError, ValueError):
                return None
            if peer_asn == requested_asn:
                return peer
        return None
    
