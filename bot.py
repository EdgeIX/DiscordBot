#!/usr/bin/env python3
import os
import random
import re

import discord
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv

from bgp import RouteServerInteraction

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
welcome_channel_id = os.getenv('WELCOME_CHANNEL')

bot = commands.Bot(command_prefix='!')
client = discord.Client()

ASN_REGEX = re.compile(r'^[0-9]+$')
IP_REGEX = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')

RouteServers = RouteServerInteraction()

@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
        'Title of your sex tape.',
        'Nine Nine!',
        'Noice',
        'Jake, piece of advice: just give up. It’s the Boyle way. It’s why our family crest is a white flag.',
        'Great, I’d like your $8-est bottle of wine, please.',
        'Aw, man. All the orange soda spilled out of my cereal.',
        'Rules are made to be broken.',
        'If I die, turn my tweets into a book.',
        'Love, it sustains you. It’s like oatmeal.,
        'Is it a crime to steal bread to feed your family?',
        'Be myself, what kind of garbage advice is that?',
    ]

    embed = await format_message('Brooklyn Nine Nine', random.choice(brooklyn_99_quotes))
    await ctx.send(embed=embed)


@bot.command(name="addasn", help='Adds ASN role to User', pass_context=True)
async def add_asn(ctx, *, message):
    """
        Add ASN role to User, create & add if role
        doesn't currently exist

        Arguments:
            message (str): Message containing ASN
        
        Example:
            !addasn 9268
    """
    match = ASN_REGEX.match(message.strip())
    if match:
        asn = f'AS{message}'
        user = ctx.message.author
        if get(ctx.guild.roles, name=asn):
            await user.add_roles(discord.utils.get(ctx.guild.roles, name=asn))
            embed = await format_message('Role Addition', f'Successfully added {asn} to {user.display_name}')
            await ctx.send(embed=embed)
        else:
            role = await ctx.guild.create_role(name=asn)
            await user.add_roles(role)
            embed = await format_message('Role Addition', f'Successfully created and added {asn} to {user.display_name}')
            await ctx.send(embed=embed)
    else:
        embed = format_message('Role Addition', f'Please enter a valid ASN. You provided: {message}')
        await ctx.send(embed=embed)  


@bot.command(name="removeasn",
             help='Removes user from ASN role',
             pass_context=True
             )
async def remove_asn(ctx, *, message):
    """
        Remove ASN role from User, if present

        Arguments:
            message (str): Message containing ASN
        
        Example:
            !removeasn 9268
    """
    match = ASN_REGEX.match(message.strip())
    if match:
        asn = f'AS{message}'
        if get(ctx.guild.roles, name=asn):
            # TODO, check if user actually has the role
            user = ctx.message.author
            await user.remove_roles(discord.utils.get(ctx.guild.roles, name=asn))
            embed = await format_message('Role Removal', f'Successfully removed {asn} from {user.display_name}')
            await ctx.send(embed=embed)
    else:
        embed = await format_message('Role Removal', f'Please enter a valid ASN. You provided: {message}')
        await ctx.send(embed=embed)  


@bot.command(name="peer_status", help='Check Route Server peer status', pass_context=True)
async def peer_status(ctx, *, message):
    """
        Remove ASN role from User, if present

        Arguments:
            message (str): Message containing ASN
        
        Example:
            !removeasn 9268
    """
    match = ASN_REGEX.match(message.strip())
    if match:
        response, header = RouteServers.on_message(message)
        embed = await format_message(
            f'Peer Status for AS{message.strip()}',
            response,
            header
        )
    else:
        embed = await format_message(
            'Error',
            'Please enter a valid ASN!',
            'Response'
        )
    await ctx.send(embed=embed)


@bot.command(name="whois", help='Check what Company an ASN/IP belongs to', pass_context=True)
async def whois(ctx, *, message):
    """
        Check who an ASN or IP belongs to on the EdgeIX Fabric

        Arguments:
            message (str): Message containing ASN or IP
        
        Example:
            !whois 9268
    """
    as_match = ASN_REGEX.match(message.strip())
    if as_match:
        x = RouteServers.asns.get(int(message))
        if x is None:
            title = f'AS{message} is unknown to EdgeIX'
            header ='Quick Links:'
            message = f'https://bgptoolkit.net/api/asn/{message}\nhttps://bgp.he.net/AS{message}'
        else:
            title = x.get('descr')
            header = 'Peering in the follow locations:'
            message = '\n'.join(i for i in x.get('locs'))

    ip_match = IP_REGEX.match(message.strip())
    if ip_match:
        x = RouteServers.ips.get(message)
        if x is None:
            title = f'{message} is unknown to EdgeIX'
            header ='Quick Links:'
            message = f'https://bgptoolkit.net/api/ca/{message}\nhttps://bgp.he.net/ip/{message}'
        else:
            title = x.get('descr')
            header = 'Allocation:'
            message = f'{message} is allocated to {x.get("descr")} on the {x.get("loc")} EdgeIX Fabric'

    embed = await format_message(
        title, message, header
    )
    await ctx.send(embed=embed)


@bot.command(name="rs_stats", help='Check number of sessions for a given City', pass_context=True)
async def rs_stats(ctx, *, message):
    # TODO!
    pass


@bot.command(name="whois_peering", help='Check who is peering for a given City', pass_context=True)
async def whois_peering(ctx, *, message):
    # TODO
    pass


@bot.event
async def on_member_join(member):
    """
        Message User a custom message on join

        Arguments:
            member (obj): Discord.py User Object

    """
    channel = bot.get_channel(welcome_channel_id)
    guild = member.guild
    message = f'Hello {member.mention}, Welcome to {guild.name} Discord server, please add your peer ASN by typing !addasn <asn>'
    embed = await format_message('Welcome!', message)
    await channel.send(embed=embed)


async def format_message(title: str, value: str, header: str = 'Response') -> discord.embeds.Embed:
    """
        Format message with Edge IX Embeds

        Arguments:
            title (str): Title displayed at top of Message
            value (str): Body of the message

    """
    embed = discord.Embed(
        title = title,
        url = 'https://edgeix.net',
        color = discord.Color.orange()
    )
    embed.set_author(name='EdgeIX Bot', url='https://edgeix.net', icon_url='https://i.imgur.com/63RePV2.png')
    embed.add_field(name=header, value=value, inline=True)
    return embed

bot.run(token)
