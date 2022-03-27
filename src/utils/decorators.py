#!/usr/bin/env python3
import asyncio
from discord import app_commands, Interaction

def has_permissions(required: list):
    async def actual_check(interaction: Interaction):
        for role in interaction.user.roles:
            if role.id in required:
                return True
        return False
        #return await interaction.client.is_owner(interaction.user)
    return app_commands.check(actual_check)

    
