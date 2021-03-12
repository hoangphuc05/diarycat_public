import discord
from discord.flags import Intents
from dotenv import load_dotenv
from discord.ext import tasks
import asyncio
import os
import yaml
import importlib
import traceback

import dailyBot

from connection import Connection

#load the api_key
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
baseEntry = os.getenv('BASEURL')

#discord client start
client = discord.Client()

responses = yaml.full_load(open('./response.yaml'))

#dailyBot = __import__('dailyBot').DailyBot()
#client
dailyClient = dailyBot.DailyBot(client)

class LocalDailyBot(discord.Client):
    @tasks.loop(seconds=10)
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


clients.run(token)


