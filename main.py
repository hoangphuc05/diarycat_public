import discord
from discord.flags import Intents
from dotenv import load_dotenv
from discord.ext import tasks
import asyncio
import os
import yaml
import importlib
import traceback

# for slash command
from discord_slash import SlashCommand 
from discord_slash.utils.manage_commands import create_choice, create_option

# for code reuse
from mock_object.mock_object import Manual_message

import dailyBot

from connection import Connection

#load the api_key
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
baseEntry = os.getenv('BASEURL')

#discord client start
client = discord.Client()

responses = yaml.full_load(open('./response.yaml'))

dailyClient = dailyBot.DailyBot(client)

class LocalDailyBot(discord.Client):
    @tasks.loop(seconds=40)
    async def checkDaily(self):
        await dailyClient.loopUpdate()

    @client.event
    async def on_ready(self):
        #self
        await self.change_presence(activity=discord.Game(name=responses["presence"]))

    # @client.event
    # async def on_error(event, *args, **kawrgs):
    #     print(args)

    # @client.event
    # async def on_error(self, event_method, *args, **kwargs):
    #     print(*args)
    #     await dailyClient._LogRaw(event_method)
    #     for i in traceback.format_stack():
    #         print(i)
    #         await dailyClient._LogRaw(i)
    #     #return super().on_error(event_method, *args, **kwargs)

    @client.event
    async def on_message(self, message):
        global dailyClient, dailyBot, responses, clients
        if message.author.bot:
            return


        if message.content == "dl!reload":
            if str(message.author.id) != "363694976665780226":
                return
            #reload file
            responses = yaml.full_load(open('./response.yaml'))
            print(type(dailyBot))
            importlib.reload(dailyBot)
            dailyClient = dailyBot.DailyBot(clients)
            await clients.change_presence(activity=discord.Game(name=responses["presence"]))
        else:
            await asyncio.wait_for(dailyClient.messageHandler(message), timeout= 1600.0)
            #await dailyClient.messageHandler(message)

    #@client.event
    # async def on_raw_reaction_add(self,payload):
    #     print(payload)
    #     print(type(payload))

    # @client.event
    # async def on_reaction_add(self,reaction,user):
    #     print("On reaction")
    #     print(reaction)
    #     print(user)
    

clients = LocalDailyBot()
clients.checkDaily.start()

#hot fix?
responses = yaml.full_load(open('./response.yaml'))
importlib.reload(dailyBot)
dailyClient = dailyBot.DailyBot(clients)

# slash command here?
slash = SlashCommand(clients, sync_commands=True) # Declares slash commands through the client.
guilds_id = [653133437087121419]

@slash.slash(guild_ids=guilds_id, name="addText", description= "Add a text entry to your diary",
                options=[
                    create_option(
                        name = "content",
                        description= "The content of the diary entry you want to add",
                        option_type=3,
                        required=True
                    )
                ])
async def add_text(ctx, content: str): # Defines a new "context" (ctx) command called "ping."
    await ctx.send(f"Received: {content}")

    tradition_content = "dl!addtext "+content
    # build a message object
    user_message = Manual_message(ctx.author, clients.get_channel(int(ctx.channel_id)), tradition_content)
    await dailyClient.messageHandler(user_message)

    #print(ctx.message)


@slash.slash(guild_ids=guilds_id, name= "help", description="Display help windows",
                options=[
                    create_option(
                        name = "command",
                        description="The command that you want to learn more about",
                        option_type=3,
                        required=False
                    )
                ])
async def help(ctx, command = ""):
    tradition_content = "dl!help " + command
    user_message = Manual_message(ctx.author, clients.get_channel(int(ctx.channel_id)), tradition_content)
    await ctx.send("Help content:")
    await dailyClient.messageHandler(user_message)


@slash.slash(guild_ids=guilds_id, name= "read", description="Read your diary")
async def read(ctx):
    tradition_content = "dl!read"
    user_message = Manual_message(ctx.author, clients.get_channel(int(ctx.channel_id)), tradition_content)
    await ctx.send("Your diary:")
    await dailyClient.messageHandler(user_message)

@slash.slash(guild_ids=guilds_id, name= "delete", description="Delete an entry from your diary",
                options=[
                    create_option(
                        name="id",
                        description="Id of the entry that you want to delete, use /read and react the entry with ❌ to get the id",
                        option_type=4,
                        required=False
                    )
                ])
async def delete(ctx, id=""):
    tradition_content = "dl!delete " + str(id)
    user_message = Manual_message(ctx.author, clients.get_channel(int(ctx.channel_id)), tradition_content)
    await ctx.send(".")
    await dailyClient.messageHandler(user_message)


@slash.slash(guild_ids=guilds_id, name= "remind", description="Turn daily reminder on or off",
                options=[
                    create_option(
                        name="switch",
                        description="Choose the reminder to be on or off",
                        option_type=3,
                        required=True,
                        choices=[
                            create_choice(
                                name = "on",
                                value="on"
                            ),
                            create_choice(
                                name= "off",
                                value= "off"
                            )
                        ]
                    )
                ])
async def remind_switch(ctx, switch="on"):
    tradition_content = "dl!remind"+ switch
    user_message = Manual_message(ctx.author, clients.get_channel(int(ctx.channel_id)), tradition_content)
    await ctx.send(".")
    await dailyClient.messageHandler(user_message)


@slash.slash(guild_ids=guilds_id, name= "invite", description="Get invite link of the bot")
async def read(ctx):
    tradition_content = "dl!invite"
    user_message = Manual_message(ctx.author, clients.get_channel(int(ctx.channel_id)), tradition_content)
    await ctx.send("Invite link:")
    await dailyClient.messageHandler(user_message)


clients.run(token)


