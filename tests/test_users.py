import pytest
import json
from .. import users, subscriptions


TEST_ISSUES = [
    (1, 'Title #1', '2021-05-06', '2021-05-06', 0),
    (2, 'Title #2', '2021-01-10', '2022-01-14', 5),
    (3, 'Title #3', '2020-12-01', '2021-01-03', 0),
    (4, 'Title #4', '2020-11-30', '2021-06-07', 11)
]

TEST_SUB_1 = subscriptions.Subscription('sub_name_1', TEST_ISSUES, 1)
TEST_SUB_2 = subscriptions.Subscription('sub_name_2', TEST_ISSUES[:2], 2)


class TestUser():
    def _dump_user(self, sub_obj):
        '''Записывает пользователя (экземпляр класса User)
        во временную БД в виде словаря'''
        data = {sub_obj.name: {"name": sub_obj.name, "subs": {}, "last_project": None}}
        data[sub_obj.name]['subs'] = {k: v.__dict__ for k, v in sub_obj.subs.items()}
        with open(self.db.path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2)

    def _read_db(self):
        '''Считывает данные БД.'''
        with open(self.db.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    @pytest.mark.usefixtures('tmp_db', 'clean_file')
    def test_from_dict(self):
        """Проверяем десереализацию пользователя"""
        test_user = users.User(name="test_user", subs={TEST_SUB_1.name: TEST_SUB_1})    # создаем юзера с 1 подпиской
        self._dump_user(test_user)    # записываем подписку в файл
        test_data = self._read_db()    # считываем данные из файла
        user_from_db = users.User.from_dict(test_data['test_user'])   # отправляем в тестируемую ф-ию
        assert user_from_db.name == 'test_user'   # сравниваем с ожидаемым результатом
        assert user_from_db.subs[TEST_SUB_1.name] == TEST_SUB_1
        assert user_from_db.last_project == None


    def test_add_subsc_one_sub(self):
        """Проверяем добавление 1й подписки новому пользователю"""
        test_user = users.User(name="test_user")    # создаем нового юзера
        test_user.add_subsc(TEST_SUB_1)    # добавляем одну подписку
        assert test_user.subs == {TEST_SUB_1.name: TEST_SUB_1}


    def test_add_subsc_one_plus_one_sub(self):
        """Проверяем добавление подписки пользователю с 1й подпиской"""
        test_user = users.User(name="test_user", subs={TEST_SUB_1.name: TEST_SUB_1})    # создаем юзера с 1 подпиской
        test_user.add_subsc(TEST_SUB_2)    # добавляем еще одну подписку
        assert test_user.subs == {TEST_SUB_1.name: TEST_SUB_1,
                                  TEST_SUB_2.name: TEST_SUB_2}  # сравниваем с ожидаемым результатом


    def test_add_subsc_name_error(self):
        """Проверяем добавление подписки, которая уже есть у пользователя"""
        with pytest.raises(NameError):
            test_user = users.User(name='test_user', subs={TEST_SUB_1.name: TEST_SUB_1})
            test_user.add_subsc(TEST_SUB_1)


    def test_remove_subsc_one_sub_user(self):
        """Проверяем удаление подписки у пользователя с 1й подпиской"""
        test_user = users.User(name='test_user', subs={TEST_SUB_1.name: TEST_SUB_1})
        test_user.remove_subsc(TEST_SUB_1.name)
        assert test_user.subs == {}


    def test_remove_subsc_two_subs_user(self):
        """Проверяем удаление подписки у пользователя с 2мя подписками"""
        test_user = users.User(name='test_user', subs={TEST_SUB_1.name: TEST_SUB_1,
                                                       TEST_SUB_2.name: TEST_SUB_2})
        test_user.remove_subsc(TEST_SUB_2.name)
        assert test_user.subs == {TEST_SUB_1.name: TEST_SUB_1}


    def test_remove_subsc_not_found(self):
        """Проверяем удаление подписки, которой нет у пользователя"""
        with pytest.raises(NameError):
            test_user = users.User(name='test_user', subs={TEST_SUB_1.name: TEST_SUB_1})
            test_user.remove_subsc(TEST_SUB_2.name)

