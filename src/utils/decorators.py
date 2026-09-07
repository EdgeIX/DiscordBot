#!/usr/bin/env python3
from discord import app_commands, Interaction

def user_has_permissions(user, required: list) -> bool:
    """Return whether a Discord user has one of the required role IDs."""
    return any(role.id in required for role in getattr(user, "roles", ()))


def has_permissions(required: list):
    async def actual_check(interaction: Interaction):
        return user_has_permissions(interaction.user, required)

    return app_commands.check(actual_check)

    
