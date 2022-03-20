#!/usr/bin/env python3
import os
import asyncio

from config.dev import config as dev
from config.production import config as prod

class ProjectConfig(object):

    def __init__(self) -> None:
        """
        Initialise Config Items
        """
        try:
            self.env = os.environ["PYTHON_ENV"]
            self.env_config = prod
        except KeyError:
            self.env = "dev"
            self.env_config = dev
    
    @property
    def c(self) -> dict:
        return self.env_config