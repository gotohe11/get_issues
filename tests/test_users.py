import pytest
from collections import namedtuple
from .. import cli, users, subscriptions


JUST_ISSUES = [
    (1, 'Title #1', '2021-05-06', '2021-05-06', 0),
    (2, 'Title #2', '2021-01-10', '2022-01-14', 5),
    (3, 'Title #3', '2020-12-01', '2021-01-03', 0),
    (4, 'Title #4', '2020-11-30', '2021-06-07', 11)
]
turn_to_namedtuple = namedtuple('issue', ['project_name'] + cli.COLUMNS)
TEST_ISSUES = [turn_to_namedtuple('test/test', *item) for item in JUST_ISSUES]   # или можно какую нить другую фигню туда засунуть?
TEST_SUB_1 = subscriptions.Subscription('sub_name_1', TEST_ISSUES[:2], 0)
TEST_SUB_2 = subscriptions.Subscription('sub_name_2', TEST_ISSUES[:3], 1)
TEST_SUB_3 = subscriptions.Subscription('sub_name_3', TEST_ISSUES, 2)

TEST_USER_1 = users.User(name='test_user', subs={TEST_SUB_1.name: TEST_SUB_1})    # юзер с тест-подпиской №1
TEST_USER_2 = users.User(name='test_user', subs={TEST_SUB_2.name: TEST_SUB_2})    # юзер с тест-подпиской №2
TEST_USER_3 = users.User(name='test_user', subs={TEST_SUB_1.name: TEST_SUB_1, TEST_SUB_2.name: TEST_SUB_2})    # юзер с 2мя тест-подписками

TEST_DATA = {"test_user": {"name": "test_user", "subs": {}, "last_project": None}}


@pytest.mark.parametrize('sub, comparison', [(TEST_SUB_1, TEST_USER_1),
                                             (TEST_SUB_2, TEST_USER_2)])
def test_add_subsc_one(sub, comparison):
    """Проверяем добавление 1й подписки новому пользователю"""
    new_user = users.User(name='test_user')
    new_user.add_subsc(sub)
    assert new_user == comparison


def test_add_subsc_one_to_one():
    """Проверяем добавление 1й подписки пользователю с 1й подпиской"""
    user_with_sub = users.User(name='test_user', subs={TEST_SUB_1.name: TEST_SUB_1})
    user_with_sub.add_subsc(TEST_SUB_2)
    assert user_with_sub == TEST_USER_3


def test_add_subsc_two():
    """Проверяем добавление 2х подписок новому пользователю"""
    new_user = users.User(name='test_user')
    new_user.add_subsc(TEST_SUB_1)
    new_user.add_subsc(TEST_SUB_2)
    assert new_user == TEST_USER_3


def test_add_subsc_name_error():
    """Проверяем добавление подписки, которая уже есть у пользователя"""
    with pytest.raises(NameError):
        user_with_sub = users.User(name='test_user', subs={TEST_SUB_1.name: TEST_SUB_1})
        user_with_sub.add_subsc(TEST_SUB_1)


def test_remove_subsc_one_sub_user():
    """Проверяем удаляется ли подписка у пользователя с 1й подпиской"""
    user_with_sub = users.User(name='test_user', subs={TEST_SUB_1.name: TEST_SUB_1})
    new_user = users.User(name='test_user')
    user_with_sub.remove_subsc(TEST_SUB_1.name)
    assert user_with_sub == new_user


def test_remove_subsc_two_subs_user():
    """Проверяем удаляется ли подписка у пользователя с 2мя подписками"""
    user_with_subs = users.User(name='test_user', subs={TEST_SUB_1.name: TEST_SUB_1, TEST_SUB_2.name: TEST_SUB_2})
    user_with_subs.remove_subsc(TEST_SUB_1.name)
    assert user_with_subs == TEST_USER_2


def test_remove_subsc_not_found():
    """Проверяем удаление подписки, которой нет у пользователя"""
    with pytest.raises(NameError):
        new_user = users.User(name='test_user')
        new_user.remove_subsc(TEST_SUB_1.name)


def test_from_dict_no_sub():
    """Проверяем десереализацию пользователя без подписок"""
    user_from_data = users.User.from_dict(TEST_DATA['test_user'])
    new_user = users.User(name='test_user')
    assert user_from_data == new_user


def test_from_dict_with_subs():
    """Проверяем десереализацию пользователя с подпиской"""
    test_data = {"test_user": {"name": "test_user", "subs": {}, "last_project": None}}
    test_data["test_user"]["subs"][TEST_SUB_1.name] = TEST_SUB_1.__dict__
    user_from_data = users.User.from_dict(test_data['test_user'])
    assert user_from_data == TEST_USER_1

