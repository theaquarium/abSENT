from dataclasses import dataclass
from datetime import datetime


@dataclass
class SchoologyUser:
    id: str
    name_display: str


@dataclass
class SchoologyUpdate:
    id: str
    date: datetime
    body: str
    uid: str


@dataclass
class Text:
    content: str
    number: str
    is_unread: bool = True
    # is_user: bool

    def mark_as_read(self):
        self.is_unread = False


# class Conversation:
#     number: str
#     texts: 'list[Text]'

#     def __init__(self, number, texts=[]):
#         self.number = number
#         self.texts = texts

#     def add_text(self, text):
#         self.texts.append(text)
