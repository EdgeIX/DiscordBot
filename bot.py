# bot.py
import os
import random
import discord
import re
from bgp import bgp_s_peerstatus

from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
welcome_channel_id=os.getenv('WELCOME_CHANNEL')

bot = commands.Bot(command_prefix='!')
client = discord.Client()

@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)


@bot.command(name="addasn", help='Adds user to ASN role',pass_context=True)
async def add_asn(ctx,*,message):
             user_input = message
             user_input = re.sub(r'[a-z]+', '', user_input, re.I)
             user_input = re.sub(r'[A-Z]+', '', user_input, re.I)
             try:
                 check_input = int(user_input)
                 user_input = ''.join(('AS',user_input))
                 if get(ctx.guild.roles, name=user_input):
                     role = discord.utils.get(ctx.guild.roles, name=user_input)
                     user = ctx.message.author
                     await  user.add_roles(role)
                     await ctx.send("Role Added")

                 else:
                    role = await ctx.guild.create_role(name=user_input)
                    await ctx.message.author.add_roles(role)
                    await ctx.send("Role Added")
             except(TypeError, ValueError):
                 await ctx.send("Please Enter a Valid ASN")


@bot.command(name="removeasn", help='Removes user from ASN role',pass_context=True)
async def add_asn(ctx,*,message):
             user_input = message
             user_input = re.sub(r'[a-z]+', '', user_input, re.I)
             user_input = re.sub(r'[A-Z]+', '', user_input, re.I)
             try:
                 check_input = int(user_input)
                 user_input = ''.join(('AS',user_input))
                 if get(ctx.guild.roles, name=user_input):
                     role = discord.utils.get(ctx.guild.roles, name=user_input)
                     user = ctx.message.author
                     await  user.remove_roles(role)
                     await ctx.send("Role Removed")

                 else:
                    role = await ctx.guild.create_role(name=user_input)
                    await ctx.message.author.remove_roles(role)
                    await ctx.send("Role Removed")
             except(TypeError, ValueError):
                 await ctx.send("Please Enter a Valid ASN")




@bot.event
async def on_member_join(member):
        channel = bot.get_channel(welcome_channel_id)
        guild=member.guild
        message ='Hello {}, Welcome to {} Discord server, please add your peer ASN by typing !addasn yourASNhere'.format(member.mention, guild.name)
        await channel.send(message)

@bot.command(name="peer_status", help='Check Router Server peer status', pass_context=True)
async def peer_status(ctx,*,message):
     user_input = message
     user_input = re.sub(r'[a-z]+', '', user_input, re.I)
     user_input = re.sub(r'[a-z]+', '', user_input, re.I)
     if "NSW" or "nsw" in user_input:
         asn = re.search(r'\d+', user_input).group(0)
         reply = bgp_s_peerstatus(asn)
         await ctx.send("\n"+reply)


bot.run(token)

