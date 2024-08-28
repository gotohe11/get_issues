import pytest
import json
from .. import users, subscriptions, database


JUST_ISSUES = [
    (1, 'Title #1', '2021-05-06', '2021-05-06', 0),
    (2, 'Title #2', '2021-01-10', '2022-01-14', 5),
    (3, 'Title #3', '2020-12-01', '2021-01-03', 0),
    (4, 'Title #4', '2020-11-30', '2021-06-07', 11)
]

TEST_SUB_1 = subscriptions.Subscription('sub_name_1', JUST_ISSUES, 1)
TEST_SUB_2 = subscriptions.Subscription('sub_name_2', JUST_ISSUES[:3], 2)


@pytest.mark.usefixtures('tmp_db', 'clean_file')
class TestDataBase():
    def _read_db(self):
        '''Считывает данные БД.'''
        with open(self.db.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    def _dump_user(self, user_name):
        '''Записывает юзера с заданным именем в БД.'''
        data = {user_name: {"name": user_name, "subs": {}, "last_project": None}}
        with open(self.db.path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2)


    def test_load_or_create_create(self):
        """Проверяем создание нового экз класса User"""
        self.db.load_or_create_user("test_user_1")    # создает нового юзера и записывает его в файл
        test_data = self._read_db()    # считываем файл
        assert len(test_data) == 1    # убеждаемся что он такой один и неповторимый
        test_user = list(test_data.values())[0]
        assert test_user['name'] == "test_user_1"
        assert test_user['subs'] == {}
        assert test_user['last_project'] == None


    def test_load_or_create_load(self):
        """Проверяем считывание существующего юзера из БД"""
        self._dump_user("test_user_1")    # записываем в БД юзера
        self.db.load_or_create_user("test_user_1")    # считываем юзера
        test_data = self._read_db()    # считываем файл
        assert len(test_data) == 1    # убеждаемся что он такой один и неповторимый
        test_user = list(test_data.values())[0]
        assert test_user['name'] == "test_user_1"
        assert test_user['subs'] == {}
        assert test_user['last_project'] == None


    def test_save_user(self):    # этот метод используется только для новых "пустых" юзеров
        """Проверяем запись данных нового пользователя в файл"""
        test_user_1 = users.User("test_user_1")    # создаем юзера (экз класса)
        self.db.save_user(test_user_1)    # записываем юзера

        test_data = self._read_db()    # считываем файл
        assert len(test_data) == 1
        test_user = list(test_data.values())[0]
        assert test_user['name'] == "test_user_1"
        assert test_user['subs'] == {}
        assert test_user['last_project'] == None


    def test_save_sub_user_with_one_sub(self):    # этот метод используется только для зареганых юзеров
        """Проверяем запись данных о подписках пользователя
        после добавления 1й подписки"""
        test_user_1 = users.User("test_user_1")  # создаем нового юзера
        self.db.save_user(test_user_1)  # записываем юзера

        test_data = self._read_db()  # считываем файл и убеждаемся в том, что он один и без подписок
        assert len(test_data) == 1
        test_user = list(test_data.values())[0]
        assert test_user['name'] == "test_user_1"
        assert test_user['subs'] == {}

        test_user_1.add_subsc(TEST_SUB_1)    # добавляем подписку нашему юзеру
        self.db.save_sub(test_user_1)  # записываем юзера с новой подпиской

        # считываем файл и убеждаемся в том, что юзер тот же, он один и с ожидаемой подпиской
        test_data_new = self._read_db()
        assert len(test_data) == 1
        test_user_with_sub = list(test_data_new.values())[0]
        assert test_user_with_sub['name'] == "test_user_1"
        assert len(test_user_with_sub['subs']) == 1
        assert 'sub_name_1' in test_user_with_sub['subs']
        assert test_user_with_sub['subs']['sub_name_1']['issues_list'] == [list(item) for item in JUST_ISSUES]
        assert test_user_with_sub['subs']['sub_name_1']['last_issue_num'] == 1


    def test_save_sub_user_with_two_sub(self):  # этот метод используется только для зареганых юзеров
        """Проверяем запись данных о подписках пользователя
        после добавления 1й подписки"""
        test_user_1 = users.User("test_user_1")  # создаем нового юзера
        self.db.save_user(test_user_1)  # записываем юзера
        test_user_1.add_subsc(TEST_SUB_1)  # добавляем подписку нашему юзеру
        self.db.save_sub(test_user_1)  # записываем юзеру подписку

        test_data = self._read_db()  # считываем файл и убеждаемся в том, что он один и с 1й подпиской
        assert len(test_data) == 1
        test_user_with_sub = list(test_data.values())[0]
        assert test_user_with_sub['name'] == "test_user_1"
        assert len(test_user_with_sub['subs']) == 1
        assert 'sub_name_1' in test_user_with_sub['subs']
        assert test_user_with_sub['subs']['sub_name_1']['issues_list'] == [list(item) for item in JUST_ISSUES]
        assert test_user_with_sub['subs']['sub_name_1']['last_issue_num'] == 1

        test_user_1.add_subsc(TEST_SUB_2)  # добавляем подписку нашему юзеру
        self.db.save_sub(test_user_1)  # записываем юзера с новой подпиской

        # считываем файл и убеждаемся в том, что юзер тот же, он один и с ожидаемыми 2мя подписками
        test_data_new = self._read_db()
        assert len(test_data) == 1
        test_user_with_sub = list(test_data_new.values())[0]
        assert test_user_with_sub['name'] == "test_user_1"
        assert len(test_user_with_sub['subs']) == 2
        assert 'sub_name_1' in test_user_with_sub['subs'] and 'sub_name_2' in test_user_with_sub['subs']
        assert test_user_with_sub['subs']['sub_name_1']['issues_list'] == [list(item) for item in JUST_ISSUES]
        assert test_user_with_sub['subs']['sub_name_1']['last_issue_num'] == 1
        assert test_user_with_sub['subs']['sub_name_2']['issues_list'] == [list(item) for item in JUST_ISSUES[:3]]
        assert test_user_with_sub['subs']['sub_name_2']['last_issue_num'] == 2
