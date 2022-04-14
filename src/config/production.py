import os
config = {
    "RULES_CHANNEL_ID": os.getenv("RULES_CHANNEL_ID"),
    "RULES_ACCEPTED_ROLE": os.getenv("RULES_ACCEPTED_ROLE"),
    "WELCOME_CHANNEL_ID": os.getenv("WELCOME_CHANNEL_ID"),
    "ROLE_APPROVAL_CHANNEL_ID": os.getenv("ROLE_APPROVAL_CHANNEL_ID"),
    "ANNOUNCEMENT_CHANNEL_ID": os.getenv("ANNOUNCEMENT_CHANNEL_ID"),
    "TOKEN": os.getenv("TOKEN"),
    "IXPM_API_KEY": os.getenv("IXPM_API_KEY"),
    "IXPM_PEER_INFO": os.getenv("IXPM_PEER_INFO"),
    "PEER_ROLE": os.getenv("PEER_ROLE"),
    "GUILD_ID": os.getenv("GUILD_ID"),
    "ROUTE_SERVERS": {
        "SYD": {
            "rs1": {
                "url": os.getenv("SYD_RS1")
            },
            "rs2": {
                "url": os.getenv("SYD_RS2")
            }
        },
        "MEL": {
            "rs1": {
                "url": os.getenv("MEL_RS1")
            },
            "rs2": {
                "url": os.getenv("MEL_RS2")
            }
        },
        "ADL": {
            "rs1": {
                "url": os.getenv("ADL_RS1")
            },
            "rs2": {
                "url": os.getenv("ADL_RS2")
            }
        },
        "BNE": {
            "rs1": {
                "url": os.getenv("BNE_RS1")
            },
            "rs2": {
                "url": os.getenv("BNE_RS2")
            }
        },
        "PER": {
            "rs1": {
                "url": os.getenv("PER_RS1")
            },
            "rs2": {
                "url": os.getenv("PER_RS2")
            }
        },
        "DRW": {
            "rs1": {
                "url": os.getenv("DRW_RS1")
                }
            },
        "HBA": {
            "rs1": {
                "url": os.getenv("HBA_RS1")
                }
            }
    }
}