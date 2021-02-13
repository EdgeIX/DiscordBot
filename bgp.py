import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
SYD_RS1 = os.getenv('SYD_RS1')
SYD_RS2 = os.getenv('SYD_RS2')

def bgp_s_peerstatus(asn):
    response_rs1_syd = requests.get(SYD_RS1).json()
    response_rs2_syd = requests.get(SYD_RS2).json()
    results_rs1_syd = "SYD - rs1 - no peer found"
    results_rs2_syd = "SYD - rs2 - no peer found"

    for k,v in response_rs1_syd['protocols'].items():
        if asn in k:
            neighbor_as = str(v["neighbor_as"])
            if asn == neighbor_as:
                results_rs1_syd = "SYD: rs1 - "+asn+": "+v["state"]

    for k,v in response_rs2_syd['protocols'].items():
        if asn in k:
            neighbor_as = str(v["neighbor_as"])
            if asn == neighbor_as:
                results_rs2_syd = "SYD: rs2 - "+asn+": "+v["state"]

    return "\n"+results_rs1_syd+"\n"+results_rs2_syd


