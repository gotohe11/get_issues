import pytest
import json
from .. import subscriptions


TEST_ISSUES = [
    (1, 'Title #1', '2021-05-06', '2021-05-06', 0),
    (2, 'Title #2', '2021-01-10', '2022-01-14', 5),
    (3, 'Title #3', '2020-12-01', '2021-01-03', 0),
    (4, 'Title #4', '2020-11-30', '2021-06-07', 11)
]


class TestSubscription():
    def _dump_sub(self, sub_obj):
        '''Записывает подписку (экземпляр класса Subscription)
        во временную БД в виде словаря'''
        data = sub_obj.__dict__
        with open(self.db.path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2)

    def _read_db(self):
        '''Считывает данные БД.'''
        with open(self.db.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    @pytest.mark.usefixtures('tmp_db', 'clean_file')
    def test_from_dict(self):
        """Проверяем десереализацию подписки"""
        test_sub = subscriptions.Subscription(name='test/test', issues_list=TEST_ISSUES,
                                              last_issue_num=2)    # создаем подписку
        self._dump_sub(test_sub)    # записываем подписку в файл
        test_data = self._read_db()    # считываем данные из файла
        sub_from_db = subscriptions.Subscription.from_dict(test_data)   # отправляем в тестируемую ф-ию
        assert sub_from_db.name == 'test/test'   # сравниваем с ожидаемым результатом
        assert sub_from_db.issues_list == TEST_ISSUES
        assert sub_from_db.last_issue_num == 2


    def test_read_issues(self):
        ''' Проверяем изменение последнего просмотренного тикета у подписки
        на номер внутри разрешимого диапазона чисел'''
        test_sub = subscriptions.Subscription(name='test/test', issues_list=TEST_ISSUES,
                                              last_issue_num=2)  # создаем подписку
        test_sub.read_issues(3)    # меняем просмотренный исус в тестируемой ф-ии
        assert test_sub.issues_list == TEST_ISSUES
        assert test_sub.last_issue_num == 3



    def test_read_issues_big_num(self):
        ''' Проверяем изменение последнего просмотренного тикета у подписки
        на номер вне разрешимого диапазона чисел'''
        test_sub = subscriptions.Subscription(name='test/test', issues_list=TEST_ISSUES,
                                              last_issue_num=2)  # создаем подписку
        test_sub.read_issues(100)    # меняем просмотренный исус в тестируемой ф-ии
        assert test_sub.issues_list == TEST_ISSUES
        assert test_sub.last_issue_num == 4


