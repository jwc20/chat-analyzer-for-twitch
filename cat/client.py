import os
import re
import sys
import asyncio
import json
import aiohttp
import websockets
from datetime import datetime
from collections import deque, namedtuple

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor, QTextCharFormat, QFont


from chat_classifier import ChatClassifier

sys.path.append(os.getcwd())
from config import CLIENT_ID, CLIENT_SECRET, CHANNEL_NAME

MAX_MESSAGES = 100
messages_queue = deque(maxlen=MAX_MESSAGES)


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
            # print(data)
            return data["data"][0]["id"]


class ChatReceiver(QThread):
    message_received = pyqtSignal(str)

    async def receive_chat_messages(self, channel_name):
        token = await get_oauth_token(CLIENT_ID, CLIENT_SECRET)
        channel_id = await get_channel_id(channel_name, token)
        websocket_url = f"wss://irc-ws.chat.twitch.tv:443"

        # Keep reconnecting and receiving messages
        while True:
            try:
                async with websockets.connect(websocket_url) as websocket:
                    await websocket.send(f"PASS oauth:{token}")
                    await websocket.send(f"NICK justinfan123")  # for read-only
                    await websocket.send(f"JOIN #{channel_name}")

                    counter = 0
                    after_end_of_names = False

                    while True:
                        message = await websocket.recv()
                        message = message.strip().replace("\n", "")

                        if not after_end_of_names:
                            match = re.search(r":End of /NAMES list", message)
                            if match:
                                after_end_of_names = True
                            continue

                        counter += 1  # Use to get total message count.

                        messages_queue.append(message)
                        self.message_received.emit(message)

            # except websockets.ConnectionClosed:
            #     continue

            except Exception as e:
                print(f"WebSocket Error: {e}")
                print("Reconnecting...")
                await asyncio.sleep(5)

    def run(self):
        asyncio.run(self.receive_chat_messages(CHANNEL_NAME))


# Chat = namedtuple(
#     "Chat",
#     [
#         "username",
#         "message",
#         "is_toxic",
#         "is_profanity",
#         "is_hate_speech",
#         "is_highlighted",
#     ],
# )


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.classifier = ChatClassifier()

    def init_ui(self):
        self.setWindowTitle("Chat")
        self.setGeometry(300, 300, 600, 600)

        self.layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)

        self.setLayout(self.layout)

    @pyqtSlot(str)
    def update_chat(self, message):
        match_nick = re.search(r"@(\w+)\.tmi\.twitch\.tv", message)
        match_chat = re.search(r"PRIVMSG #\w+ :(.*)", message)

        current_time = datetime.now().strftime("%H:%M:%S")
        username = match_nick.group(1) if match_nick else ""
        chat_message = match_chat.group(1) if match_chat else ""

        # TODO: classify the chat message
        # self.text_edit.append(f"[{current_time}] <{username}> {chat_message}")

         # Classify the chat message
        classification = self.classifier.get_result(chat_message)

        # Set the default format
        text_format = QTextCharFormat()
        # text_format.setFont(QFont("Arial", 10))

        # Highlight toxic messages
        if classification == "toxic":
            text_format.setForeground(QColor("red"))

        # Add the formatted message to the QTextEdit
        self.text_edit.setCurrentCharFormat(text_format)
        self.text_edit.append(f"[{current_time}] <{username}> {chat_message}")


def main():
    app = QApplication(sys.argv)

    chat_window = ChatWindow()
    chat_window.show()

    chat_receiver = ChatReceiver()
    chat_receiver.message_received.connect(chat_window.update_chat)
    chat_receiver.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
