import asyncio
import json
import aiohttp
import websockets

# Set your credentials
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
CHANNEL_NAME = "target_channel_name"

async def get_oauth_token(client_id, client_secret):
    url = f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials"
    async with aiohttp.ClientSession() as session:
        async with session.post(url) as response:
            data = await response.json()
            return data["access_token"]


async def get_channel_id(channel_name, token):
    url = f"https://api.twitch.tv/helix/users?login={channel_name}"
    headers = {"Client-ID": CLIENT_ID, "Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data["data"][0]["id"]


async def receive_chat_messages(channel_name):
    token = await get_oauth_token(CLIENT_ID, CLIENT_SECRET)
    channel_id = await get_channel_id(channel_name, token)

    websocket_url = f"wss://irc-ws.chat.twitch.tv:443"
    async with websockets.connect(websocket_url) as websocket:
        # Send authentication and join channel
        await websocket.send(f"PASS oauth:{token}")
        await websocket.send(f"NICK justinfan123")
        await websocket.send(f"JOIN #{channel_name}")

        # Receive messages
        while True:
            message = await websocket.recv()
            print(f"Message: {message}")


if __name__ == "__main__":
    asyncio.run(receive_chat_messages(CHANNEL_NAME))
