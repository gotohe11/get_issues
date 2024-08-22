import pytest
import os
from .. import users, subscriptions, database


DB = database.Database('/tmp/test_data.json')   # 'get_issues/tests/test_data.json'  '/tmp/test_data.json'

JUST_ISSUES = [
    (1, 'Title #1', '2021-05-06', '2021-05-06', 0),
    (2, 'Title #2', '2021-01-10', '2022-01-14', 5),
    (3, 'Title #3', '2020-12-01', '2021-01-03', 0),
    (4, 'Title #4', '2020-11-30', '2021-06-07', 11)
]

TEST_ISSUES = subscriptions.Subscription.make_named_tuples(JUST_ISSUES, 'test/test')
TEST_SUB_1 = subscriptions.Subscription('sub_name_1', TEST_ISSUES, 1)
TEST_SUB_2 = subscriptions.Subscription('sub_name_2', TEST_ISSUES[:3], 2)

TEST_USER_1 = users.User(name='test_user_1')    # юзер без подписок


def test_load_or_create():
    """Проверяем создание нового экз класса User"""
    result = DB.load_or_create_user("test_user_1")    # создаем файл и нового юзера
    assert result == TEST_USER_1   # сравниваем


def test_save_user():    # этот метод используется только для новых "пустых" юзеров
    """Проверяем запись данных нового пользователя в файл"""
    test_user = users.User("test_user_2")    # создаем юзера
    DB.save_user(test_user)    # записываем юзера
    result = DB.load_or_create_user("test_user_2")    # считываем только что записанного юзера
    assert result == test_user


def test_save_sub_one():    # этот метод используется только для зареганых юзеров
    """Проверяем запись данных о подписках пользователя
    после добавления 1й подписки"""
    TEST_USER_1.add_subsc(TEST_SUB_1)    # добавляем подписку
    DB.save_sub(TEST_USER_1)    # записываем подписки юзера
    result = DB.load_or_create_user("test_user_1")    # считываем записанного юзера
    assert result == TEST_USER_1


def test_save_sub_two():    # этот метод используется только для зареганых юзеров
    """Проверяем запись данных о подписках пользователя
    после добавления 2й подписки"""
    TEST_USER_1.add_subsc(TEST_SUB_2)    # добавляем еще одну подписку
    DB.save_sub(TEST_USER_1)    # записываем подписки юзера
    result = DB.load_or_create_user("test_user_1")    # считываем записанного юзера
    assert result == TEST_USER_1
    os.remove(DB.path)  # удаляем файл



