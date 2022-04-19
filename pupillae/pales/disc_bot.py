import copy
import random
import re

import discord

from pupillae.conf import config
from pupillae.conf import connect
from pupillae.pales import pales
import pupillae.fons.generator.dice_roller as dr


client = discord.Client()
message_max = config.config(section="discord")["message_max"]
search_max = config.config(section="discord")["search_max"]

emotinav = {
    "trash": '🚮'#"\U0001F6AE"
    }
searchnav = {
    "arrow_forward": '⏭'#"\U000023ED"
    }
imgage_shortcuts = {
    "result_1": '1️⃣',
    "result_2": '2️⃣',
    "result_3": '3️⃣',
    "result_4": '4️⃣',
    "result_5": '5️⃣',
    "result_6": '6️⃣',
    "result_7": '7️⃣',
    "result_8": '8️⃣',
    "result_9": '9️⃣',
    "result_10": '🔟'
    }
offset_dict = {
    "limit_current": int(search_max),
    "offset_current": 0
    }
saved_query = None
saved_offset = None

@client.event
async def on_ready() -> None:
    print("DISCORD: We have logged in as {0.user}".format(client))
    conn = connect.connect(user="pales_pg", persist=False)

@client.event
async def on_message(message) -> None:

    global saved_query
    global saved_offset

    if message.author == client.user and not message.content.startswith("Offical:"):
        for unicode in emotinav.values():
            await message.add_reaction(unicode)

    if message.author == client.user and message.content.startswith("__Search"):
        for unicode in searchnav.values():
            await message.add_reaction(unicode)

    if message.content.startswith("$db "):
        db_query = message.content
        error = None

        try:
            conn = connect.connect(user="pales_pg", persist=True)
            cur = conn.cursor()
            response = pales.query_db(cur, db_query[4:], offset=offset_dict)
        except Exception as error:
# TODO: Catch AttributeError: 'SyntaxError' object
            error = error
        finally:
            if conn is not None:
                conn.close()
                print("Database connection closed.")
        if error:
            await message.channel.send(error)
        print(response)
        if response.startswith("Model ID:"):
            header, img_path = response.split("||")
            await message.channel.send(file=discord.File(img_path))
        else:
# Save query and offset_dict in "cache".
            saved_query = copy.deepcopy(db_query)
            saved_offset = copy.deepcopy(offset_dict)

            response = "__Search Results:__" + "\n" + response
            await message.channel.send(response)

    if message.content.startswith("$roll "):
        if message.content.startswith("$roll char"):
            response = f"Offical:\n {dr.roll_char_stats()}"
        else:
            dice = message.content
            response = f"Offical:\n {dr.parse_roll(dice)}"
        await message.channel.send(response)

@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """ Respond to reactions to bot messages in the following manner:

    - trash-icon (🚮): Delete bot message, clear the "cache" if message was search.
    - next-track (⏭): Show the next page of search results.
    - '1' to n (1️⃣...): Display image for associated result.
    """

    global saved_query
    global saved_offset
    error = None

    if payload.member.bot == True:
        return

    if payload.emoji.name == '🚮':
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author == client.user and not message.content.startswith("Offical:"):
            await message.delete()

        if message.author == client.user and message.content.startswith("__Search"):
        # Trash the saved search
            saved_query = None
            saved_offset = None

    if payload.emoji.name == '⏭':
        if saved_query and saved_offset:
            channel = client.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            saved_offset["offset_current"] = saved_offset["offset_current"] + saved_offset["limit_current"]

            try:
                conn = connect.connect(user="pales_pg", persist=True)
                cur = conn.cursor()
                response = pales.db_find(cur, saved_query[8:], saved_offset)
                print(response)
            except Exception as e:
    # TODO: Catch AttributeError: 'SyntaxError' object
                error = e
            finally:
                if conn is not None:
                    conn.close()
                    print("Database connection closed.")
            print("ERR -->", error)
            if error:
                await message.channel.send(error)
            print(response)
            response = "__Search Results:__" + "\n" + response
            await message.channel.send(response)

client.run(config.config(section="discord")["test_bot_token"])
