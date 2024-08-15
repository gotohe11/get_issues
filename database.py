import json
from dataclasses import dataclass, field
import os.path

from . import users
from . import subscriptions


class Database:
    @staticmethod
    def load_or_create_user(user_name):
        try:
            with open(os.path.expanduser('~/users_data.json'), 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            with open(os.path.expanduser('~/users_data.json'), 'w', encoding='utf-8') as file:
                data = {"vasya": {"name": "vasya", "subsc_list": [], "last_project": None}}  # без предварительной записи каких-либо данных ничего не работало
                json.dump(data, file, indent=2)
        if user_name in data:
            user = users.User.from_dict(data[user_name])
        else:
            user = users.User(user_name)
            Database.save_user(user)
        return user


    @staticmethod
    def save_user(user):
        with open(os.path.expanduser('~/users_data.json'), 'r+', encoding='utf-8') as file:
            data = json.load(file)
            data[user.name] = user.__dict__
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()


    @staticmethod
    def save_sub(user):     # перезаписываем все подписки юзера
        with open(os.path.expanduser('~/users_data.json'), 'r+', encoding='utf-8') as file:
            data = json.load(file)
            data[user.name]['subsc_list'] = [item.__dict__ for item in user.subsc_list]
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()
