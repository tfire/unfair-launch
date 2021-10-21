from private import discord_keys, infura_api
import utils

import traceback
import websockets
import asyncio
import json

import discord
from discord.ext import commands
from discord.ext.commands import bot

class UnfairLaunchBot(bot.BotBase, discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        asyncio.run_coroutine_threadsafe(self.sushi_monitor(), self.loop)

    async def on_ready(self):
        print(self.user)

    async def sushi_monitor(self):
        await self.wait_until_ready()
        async with websockets.connect(infura_api.INFURA_WS) as ws:
            await ws.send(json.dumps(
                {
                    "id": 1, "method": "eth_subscribe", "params": ["logs", {
                        "address": [utils.SUSHI_FACTORY_V2],
                        "topics": [utils.w3.keccak(text="PairCreated(address,address,address,uint256)").hex()]
                    }]
                }
            ))
            
            subscription_response = await ws.recv()
            print(subscription_response)

            while not self.is_closed():
                try:
                    event = await ws.recv()
                    await self.handle(event)
                except Exception:
                    traceback.print_exc() 

    async def handle(self, event):
        print(event)



b = UnfairLaunchBot(command_prefix="!")
b.run(discord_keys.DISCORD_BOT_KEY)

