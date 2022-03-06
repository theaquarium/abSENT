from typing import Callable
from singleton import SingletonMeta
from .typedefs import Text


class SMSFaker(metaclass=SingletonMeta):
    # conversations: 'dict[str, Conversation]'
    new_messages: 'list[Text]' = []
    send_cb: Callable = None
    # not part of api
    send_queue: 'list[Text]' = []

    def get_unread_messages(self):
        unread_messages = [msg for msg in self.new_messages if msg.is_unread]
        self.new_messages = unread_messages
        return unread_messages

    def send_sms(self, number, message):
        self.send_queue.append(Text(message, number, is_unread=False))
        if self.send_cb is not None:
            self.send_cb()
        return True

    # not an api method
    def add_text(self, text):
        self.new_messages.append(text)

    # not an api method
    def set_send_cb(self, send_cb):
        self.send_cb = send_cb

    # not an api method
    def clear_send_queue(self):
        self.send_queue = []
