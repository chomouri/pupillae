
import random
import re

import discord

import pupillae.fons.generator.dice_roller as dr
import pupil

from pupillae.conf import config
from pupillae.conf import connect

client = discord.Client()

@client.event
async def on_ready():
    print("DISCORD: We have logged in as {0.user}".format(client))
    conn = connect.connect(user="pales_pg", persist=False)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$db "):
        db_query = message.content
        response = pupil.parse_db(db_query)
        await message.channel.send(response)

    if message.content.startswith("$roll "):
        dice = message.content
        response = dr.parse_roll(dice)
        await message.channel.send(response)


client.run(config.config(section="discord_tokens")["test_bot_token"])
