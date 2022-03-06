from singleton import SingletonMeta
from datetime import datetime


class DateFaker(metaclass=SingletonMeta):
    date: datetime
    is_frozen: bool

    def __init__(self):
        self.date = None
        self.is_frozen = False

    def get_date(self):
        if self.is_frozen:
            return self.date
        else:
            return datetime.now()

    def freeze(self, date: datetime):
        self.date = date
        self.is_frozen = True

    def unfreeze(self):
        self.date = None
        self.is_frozen = False
