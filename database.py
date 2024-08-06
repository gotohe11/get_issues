import json
from dataclasses import dataclass, field

from . import users
from . import subscriptions


class Database:
    @staticmethod
    def load_user(user_name):
        with open('users_data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        if user_name in data:
            user = users.User.from_dict(data[user_name])
            print(f'Hello, {user_name}! Glad to see you again!')
        else:
            user = users.User(user_name)
            Database.save_user(user)

        return user


    @staticmethod
    def save_user(user):
        with open('users_data.json', 'r+', encoding='utf-8') as file:
            data = json.load(file)
            data[user.name] = user.__dict__
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()
        print(f'Hello, {user.name}!')


    @staticmethod
    def save_sub(USER):    # перезаписываем
        with open('users_data.json', 'r+', encoding='utf-8') as file:
            data = json.load(file)
            data[USER.name]['subsc_list'] = [item.__dict__ for item in USER.subsc_list]
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()







