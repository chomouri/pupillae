
import random
import re

import discord

from pupillae.conf import config
from pupillae.conf import connect
from pupillae.pales import pales
import pupillae.fons.generator.dice_roller as dr


client = discord.Client()
emotinav = {
    "trash": '🚮'#"\U0001F6AE"
    # , "arrow_back": "\U000023EE"
    # , "arrow_forward": "\U000023ED"
    }

@client.event
async def on_ready() -> None:
    print("DISCORD: We have logged in as {0.user}".format(client))
    conn = connect.connect(user="pales_pg", persist=False)

@client.event
async def on_message(message) -> None:
    if message.author == client.user and not message.content.startswith("Offical:"):
        for unicode in emotinav.values():
            await message.add_reaction(unicode)

    if message.content.startswith("$db "):
        db_query = message.content
        error = None
        try:
            conn = connect.connect(user="pales_pg", persist=True)
            cur = conn.cursor()
            response = pales.query_db(cur, db_query[4:])
        except Exception as error:
            error = error
        finally:
            if conn is not None:
                conn.close()
                print("Database connection closed.")
        if error:
            await message.channel.send(error)
        if response.startswith("Model ID:"):
            header, img_path = response.split("||")
            await message.channel.send(file=discord.File(img_path))
        else:
            await message.channel.send(response)

    if message.content.startswith("$roll "):
        dice = message.content
        response = f"Offical:\n {dr.parse_roll(dice)}"
        await message.channel.send(response)

@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """ Delete messges by the bot that a user has reacted to with trash-icon"""
    if payload.member.bot == True:
        return

    if payload.emoji.name == '🚮':
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author == client.user and not message.content.startswith("Offical:"):
            await message.delete()


client.run(config.config(section="discord_tokens")["test_bot_token"])
