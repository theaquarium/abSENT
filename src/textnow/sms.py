import os
from database.logger import MessageLogger
import pytextnow
from dev_env.sms_faker import SMSFaker
import time
from dataStructs import *
from datetime import datetime, timedelta
from database.logger import MessageLogger


class SMS:

    # "Logs" into API. In reality, each API request is simply using auth header. There is no concept of a session.
    def __init__(self, creds: TextNowCreds):
        if os.environ['absent_environment'] == 'dev':
            self.client = SMSFaker()
        else:
            self.client = pytextnow.Client(
                creds.username, sid_cookie=creds.sid, csrf_cookie=creds.csrf)

        # Message logger
        self.messageLog = MessageLogger()
    # Sends a message.

    def send(self, number: str, message: str) -> bool:
        self.client.send_sms(number, message)
        self.messageLog.log("abSENT", number, message)  # Log message.
        return True

    # Gets all unreads and marks them as read.
    def receive(self) -> list:
        unreads = []
        for msg in self.client.get_unread_messages():
            msg.mark_as_read()
            entry = Message(Number(msg.number), msg.content)
            unreads.append(entry)
        return unreads

    # Gets all unreads.
    def listen(self):
        messages = []
        for msg in self.client.get_unread_messages():
            entry = msg
            messages.append(entry)
        return messages

    # Marks a message as read.
    def markAsRead(self, msg) -> bool:
        msg.mark_as_read()
        return True

    # Blocks and waits for a message from a specific number.
    def awaitResponse(self, number: Number) -> Message or None:
        start_time = time.time()
        while True:
            # Timeout functionality.
            # Timeout after 5 minutes.
            if start_time + 300 < time.time():
                return None

            unreads = []
            for msg in self.listen():
                if str(msg.number) == str(number):
                    self.markAsRead(msg)
                    unreads.append(Message(Number(number), msg.content))
                    # Log message.
                    self.messageLog.log(number, "abSENT", msg.content)

            if len(unreads) == 0:
                time.sleep(0.2)
                continue
            return unreads[0]
