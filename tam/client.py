#!/usr/bin/env python
 

import asyncio 
import websockets 

async def chat_client():
    uri = "wss://irc-ws.chat.twitch.tv:443"

    # TODO: Authenticate 

    while True: 
        message = await websocket.recv()
        if "PRIVMSG" in message: 
            parts = message.split(":")
            # username 
            # message

            print(part[1], part[2])
