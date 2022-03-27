import enum

class PeeringLocations(enum.Enum):
    Sydney = "SYD"
    Melbourne = "MEL"
    Brisbane = "BNE"
    Perth = "PER"
    Adelaide = "ADL"
    Darwin = "DRW"
    Hobart = "HBA"

class WhoisTypes(enum.Enum):
    ASN = "ASN"
    IP = "IP"