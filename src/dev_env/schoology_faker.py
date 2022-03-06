from singleton import SingletonMeta
from .typedefs import SchoologyUpdate, SchoologyUser


class SchoologyFakerInstance():
    update_feed: 'list[SchoologyUpdate]'
    users: 'dict[str, SchoologyUser]'
    limit: int = 20

    def get_feed(self):
        return self.update_feed[:self.limit]

    def get_user(self, uid):
        return self.users[uid]

    # not api method
    def add_update(self, update, user):
        self.update_feed.insert(0, update)
        self.users[user.uid] = user

    # not api method
    def delete_update(self, id):
        for index, val in enumerate(self.update_feed):
            if val.id == id:
                self.users.pop(val.uid, None)
                self.update_list.remove(index)

        # self.update_list = [item for item in self.update_list if (
        #     item['id'] != id)]

    # not api method
    def clear(self):
        self.update_feed = []
        self.users = {}


class SchoologyFaker(metaclass=SingletonMeta):
    schoology_instances = {}

    def get_schoology_instance(self, school) -> SchoologyFakerInstance:
        if school not in self.schoology_instances:
            self.schoology_instances[school] = SchoologyFakerInstance()

        return self.schoology_instances[school]

    def get_south(self) -> SchoologyFakerInstance:
        return self.get_schoology_instance('south')

    def get_north(self) -> SchoologyFakerInstance:
        return self.get_schoology_instance('north')
