import discord
from discord import ui

from utils.functions import format_message

ANNOUNCEMENT_TYPES = ["outage", "general"]

class EdgeIXAnnouncementModal(ui.Modal, title="EdgeIX Announcement"):
    header = ui.TextInput(label="Header", required=True)
    #outage_type = ui.Select(options = [
    #        discord.SelectOption(label="Test",emoji="✅",description="Test1"),
    #        discord.SelectOption(label="Test2",emoji="❌",description="Test2"),
    #    ]
    #)
    announcement_type = ui.TextInput(label="Announcement Type", placeholder="outage/general", required=True)
    body = ui.TextInput(label="Body", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        if self.announcement_type.value.lower() not in ANNOUNCEMENT_TYPES:
            await interaction.response.send_message(f"{self.announcement_type.value} is not a valid announcement type", ephemeral=True)
        else:
            channel = interaction.client.get_channel(interaction.client.config["ANNOUNCEMENT_CHANNEL_ID"])
            message = await format_message(self.header.value, self.body.value, None, "Announcement")
            await channel.send(embed=message)
            await interaction.response.send_message("Announcement has been sent", ephemeral=True)