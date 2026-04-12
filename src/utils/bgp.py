#!/usr/bin/env python3
import aiohttp

from rich.console import Console

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
            async with self.session.get(url=url) as resp:
                if resp.status != 200:
                    self.console.print(f"[red]HTTP GET to {url} returned {resp.status}[/]")
                    return "UNKNOWN"
                data = await resp.json()
        except aiohttp.ClientError as exc:
            self.console.print(f"[red]HTTP GET to {url} failed: {exc}[/]")
            return "UNKNOWN"
        except aiohttp.ContentTypeError:
            self.console.print(f"[red]HTTP GET to {url} returned invalid JSON[/]")
            return "UNKNOWN"

        return data.get("data", {}).get("name", "UNKNOWN")
    
