#!/usr/bin/env python3
import re

ASN_REGEX = re.compile(r'^[0-9]+$')
IP_REGEX = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')