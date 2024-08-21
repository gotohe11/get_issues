import pytest
from collections import namedtuple
from .. import subscriptions


JUST_ISSUES = [
    (1, 'Title #1', '2021-05-06', '2021-05-06', 0),
    (2, 'Title #2', '2021-01-10', '2022-01-14', 5)
]


TEST_DATA = {
    "name": "sub_name_1",
    "issues_list": [
        [
            "test/test",
            1,
            "Title #1",
            "2021-05-06",
            "2021-05-06",
            0
        ],
        [
            "test/test",
            2,
            "Title #2",
            "2021-01-10",
            "2022-01-14",
            5
        ]
    ],
    "last_issue_num": 0
}



def test_from_dict():
    """Проверяем десереализацию подписки"""
    sub_from_data = subscriptions.Subscription.from_dict(TEST_DATA)
    test_issues = subscriptions.Subscription.make_named_tuples(JUST_ISSUES, 'test/test')
    test_sub = subscriptions.Subscription('sub_name_1', test_issues)
    assert sub_from_data == test_sub


def test_make_named_tuples():
    """Проверяем создание named tuple из списков"""
    turn_to_namedtuple = namedtuple('issue', ['project_name'] + subscriptions.COLUMNS)
    list_for_compare = [turn_to_namedtuple('test/test', *item) for item in JUST_ISSUES]
    test_issues = subscriptions.Subscription.make_named_tuples(JUST_ISSUES, 'test/test')
    assert test_issues == list_for_compare




