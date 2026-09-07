#!/usr/bin/env python3
from rich.console import Console
from utils.functions import HTTPRequestError, fetch_json

class BGPToolkitAPI:
    """
        Python Wrapper for bgptoolkit.net
    """
    def __init__(self, session=None):
        self.console = Console()
        self.session = session

    async def get_asn_name(self, asn):
        """ 
        Get ASN name from BGP Toolkit API

        Arguments:
            asn (int): ASN to obtain

        Return:
            dict: JSON blop from bgptoolkit.net
        """
        url = f"https://bgptoolkit.net/api/asn/{asn}"
        if self.session is None:
            self.console.print("[red]BGP Toolkit session is not ready[/]")
            return "UNKNOWN"

        try:
            data = await fetch_json(self.session, url)
        except HTTPRequestError as exc:
            self.console.print(f"[red]{exc}[/]")
            return "UNKNOWN"

        details = data.get("data")
        if not isinstance(details, dict):
            self.console.print(f"[red]HTTP GET to {url} returned an invalid schema[/]")
            return "UNKNOWN"
        return details.get("name", "UNKNOWN")
    
