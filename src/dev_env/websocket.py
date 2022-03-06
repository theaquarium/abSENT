from datetime import datetime
import json
from ws4py.websocket import WebSocket
from .date_faker import DateFaker
from .sms_faker import SMSFaker
from .schoology_faker import SchoologyFaker
from .typedefs import SchoologyUpdate, SchoologyUser, Text


class DevWebsocket(WebSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sc_mock = SchoologyFaker()
        self.sms_mock = SMSFaker()
        self.date_faker = DateFaker()

        self.sms_mock.set_send_cb(self.send_text)

    def send_text(self):
        if not self.terminated and self.sock is not None:
            for text in self.sms_mock.send_queue:
                response = {
                    'messageType': 'sms-from-absent',
                    'number': text.number,
                    'body': text.content,
                }
                self.send(json.dumps(response), False)
            self.sms_mock.clear_send_queue()

    def opened(self):
        self.send_text()

    def received_message(self, message):
        message_data = json.loads(message.data)
        if message_data['messageType'] == 'sms-from-user':
            new_text = Text(message_data['body'], message_data['number'])
            self.sms_mock.add_text(new_text)

            # conversation = None
            # if 'number' not in self.sms_mock.conversations:
            #     conversation = Conversation(message_data['number'])
            #     self.sms_mock.conversations[message_data['number']
            #                                 ] = conversation
            # else:
            #     conversation = self.sms_mock.conversations['number']

            # conversation.add_text(new_text)

            # response = {
            #     'messageType': 'sms-from-absent',
            #     'number': message_data['number'],
            #     'body': message_data['body'],
            # }
            # self.send(json.dumps(response), False)

        elif message_data['messageType'] == 'south-update-posted' or message_data['messageType'] == 'north-update-posted':
            new_user = SchoologyUser(
                message_data['user']['id'], message_data['user']['name'])
            # schoology_users.append(new_user)

            new_update = SchoologyUpdate(
                message_data['id'], datetime.fromtimestamp(message_data['date']/1000), message_data['body'], new_user.id)

            if message_data['messageType'] == 'south-update-posted':
                # south_update_feed.append(new_update)
                self.sc_mock.get_south().add_update(new_update, new_user)
            else:
                # north_update_feed.append(new_update)
                self.sc_mock.get_north().add_update(new_update, new_user)

        elif message_data['messageType'] == 'delete-update':
            # south_update_feed = [item for item in south_update_feed if (
            #     item['id'] != message_data['updateId'])]
            # north_update_feed = [item for item in north_update_feed if (
            #     item['id'] != message_data['updateId'])]
            self.sc_mock.get_south().delete_update(message_data['updateId'])
            self.sc_mock.get_north().delete_update(message_data['updateId'])

        elif message_data['messageType'] == 'delete-conversation':
            # conversations.pop(message_data['number'], None)
            pass

        elif message_data['messageType'] == 'clear-updates':
            # north_update_feed = []
            # south_update_feed = []
            # schoology_users = []
            self.sc_mock.get_south().clear()
            self.sc_mock.get_north().clear()

        elif message_data['messageType'] == 'clear-conversations':
            # conversations = {}
            pass

        elif message_data['messageType'] == 'clear-all':
            # north_update_feed = []
            # south_update_feed = []
            # schoology_users = []
            # conversations = {}
            self.sc_mock.get_south().clear()
            self.sc_mock.get_north().clear()

        elif message_data['messageType'] == 'freeze-date':
            frozen_date = datetime.fromtimestamp(message_data['date']/1000)
            self.date_faker.freeze(frozen_date)

        elif message_data['messageType'] == 'unfreeze-date':
            # frozen_date = None
            self.date_faker.unfreeze()

        elif message_data['messageType'] == 'reset-state':
            print('Resetting state...')
