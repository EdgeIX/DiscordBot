import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
SYD_RS1 = os.getenv('SYD_RS1')
SYD_RS2 = os.getenv('SYD_RS2')
MEL_RS1 = os.getenv('MEL_RS1')
MEL_RS2 = os.getenv('MEL_RS2')
ADL_RS1 = os.getenv('ADL_RS1')
ADL_RS2 = os.getenv('ADL_RS2')
BNE_RS1 = os.getenv('BNE_RS1')
BNE_RS2 = os.getenv('BNE_RS2')
PER_RS1 = os.getenv('PER_RS1')
PER_RS2 = os.getenv('PER_RS2')



def bgp_s_peerstatus(asn):
    response_rs1_syd = requests.get(SYD_RS1).json()
    response_rs2_syd = requests.get(SYD_RS2).json()
    response_rs1_mel = requests.get(MEL_RS1).json()
    response_rs2_mel = requests.get(MEL_RS2).json()
    response_rs1_adl = requests.get(ADL_RS1).json()
    response_rs2_adl = requests.get(ADL_RS2).json()
    response_rs1_bne = requests.get(BNE_RS1).json()
    response_rs2_bne = requests.get(BNE_RS2).json()
    response_rs1_per = requests.get(PER_RS1).json()
    response_rs2_per = requests.get(PER_RS2).json()
    results_rs1_syd = "SYD - rs1 - no peer found"
    results_rs2_syd = "SYD - rs2 - no peer found"
    results_rs1_mel = "MEL - rs1 - no peer found"
    results_rs2_mel = "MEL - rs2 - no peer found"
    results_rs1_adl = "ADL - rs1 - no peer found"
    results_rs2_adl = "ADL - rs2 - no peer found"
    results_rs1_bne = "BNE - rs1 - no peer found"
    results_rs2_bne = "BNE - rs2 - no peer found"
    results_rs1_per = "PER - rs1 - no peer found"
    results_rs2_per = "PER - rs2 - no peer found"

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

    for k,v in response_rs1_mel['protocols'].items():
        if asn in k:
            neighbor_as = str(v["neighbor_as"])
            if asn == neighbor_as:
                results_rs1_mel = "MEL: rs1 - "+asn+": "+v["state"]

    for k,v in response_rs2_mel['protocols'].items():
        if asn in k:
            neighbor_as = str(v["neighbor_as"])
            if asn == neighbor_as:
                results_rs2_mel = "MEL: rs2 - "+asn+": "+v["state"]

    for k,v in response_rs1_adl['protocols'].items():
        if asn in k:
            neighbor_as = str(v["neighbor_as"])
            if asn == neighbor_as:
                results_rs1_adl = "ADL: rs1 - "+asn+": "+v["state"]

    for k,v in response_rs2_adl['protocols'].items():
        if asn in k:
            neighbor_as = str(v["neighbor_as"])
            if asn == neighbor_as:
                results_rs2_adl = "ADL: rs2 - "+asn+": "+v["state"]

    for k,v in response_rs1_bne['protocols'].items():
        if asn in k:
            neighbor_as = str(v["neighbor_as"])
            if asn == neighbor_as:
                results_rs1_bne = "BNE: rs1 - "+asn+": "+v["state"]

    for k,v in response_rs2_bne['protocols'].items():
        if asn in k:
            neighbor_as = str(v["neighbor_as"])
            if asn == neighbor_as:
                results_rs2_bne = "BNE: rs2 - "+asn+": "+v["state"]

    for k,v in response_rs1_per['protocols'].items():
        if asn in k:
            neighbor_as = str(v["neighbor_as"])
            if asn == neighbor_as:
                results_rs1_per = "PER: rs1 - "+asn+": "+v["state"]

    for k,v in response_rs2_per['protocols'].items():
        if asn in k:
            neighbor_as = str(v["neighbor_as"])
            if asn == neighbor_as:
                results_rs2_per = "PER: rs2 - "+asn+": "+v["state"]


    return "\n"+results_rs1_syd+"\n"+results_rs2_syd+"\n"+results_rs1_mel+"\n"+results_rs2_mel+"\n"+results_rs1_adl+"\n"+results_rs2_adl+"\n"+results_rs1_bne+"\n"+results_rs2_bne+"\n"+results_rs1_per+"\n"+results_rs2_per


