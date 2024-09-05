import pytest
import json
from datetime import date
from .. import cli, errors, github, database, users, subscriptions


TEST_ISSUES = [
    (1, 'Title #1', '2021-05-06', '2021-05-06', 0),
    (2, 'Title #2', '2021-01-10', '2022-01-14', 5),
    (3, 'Title #3', '2020-12-01', '2021-01-03', 0),
    (4, 'Title #4', '2020-11-30', '2021-06-07', 11)
]

TEST_SUB_1 = subscriptions.Subscription('sub_name_1', TEST_ISSUES, 1)
TEST_SUB_2 = subscriptions.Subscription('sub_name_2', TEST_ISSUES, 2)


@pytest.fixture()
def command_stub():
    """ Добавляет специальную команду, которую можно использовать в тестах
    для проверки парсера, не думая о том, чтобы внутри самой команды корректно
    работало.
    """
    def _stub(*args):
        """ Команда-заглушка возвращает свои аргументы. """
        return args

    cli.COMMANDS['/stub'] = _stub
    yield
    del cli.COMMANDS['/stub']


@pytest.fixture()
def mock_github():
    """ Вешаем заглушку на Github API.
    """
    def _github_mock(project_name: str):
        if project_name in ['test/test', 'sub_name_1', 'sub_name_2']:
            return TEST_ISSUES
        else:
            raise github.ProjectNotFoundError
    original_fn = github.make_issues_list
    github.make_issues_list = _github_mock
    yield
    github.make_issues_list = original_fn



class TestCliDecoratorCommand():
    def test_dec_command(self):
        """ Проверяем, что декоратор на тестируемой ф-ии добавляет
        информацию о ней в словарь COMMANDS и в список INFO.
        """
        # определяем функцию с декоратором
        @cli.dec_command('test_cmd', 'test_cmd info')
        def _test_commad():
            return '= ^ . ^ ='

        assert '/test_cmd' in cli.COMMANDS
        assert ('/test_cmd', 'test_cmd info') in cli.INFO


class TestCliMainLogicFunc():
    @pytest.mark.parametrize('cmd', ['/bad', 'next'])
    def test_missing_command(self, cmd):
        """ Проверяем, что корректно обрабатывается ввод не существующей команды.
        """
        with pytest.raises(errors.CommandNotFound):
            cli._run_one(cmd)


    def test_case_and_whitespace(self, command_stub):
        """ Проверяем, что парсер команд не чувствителен к регистру ввода и лишним
        пробелам.
        """
        result = cli._run_one('  /StUb a1   a2 a3  ')
        assert list(result) == ['a1', 'a2', 'a3']


    def test_get_ok(self, mock_github):
        """ Проверяем основной сценарий выполнения команды /get.
        """
        result = cli._run_one('/get test/test')
        assert cli.USER.last_project.issues_list == TEST_ISSUES


    @pytest.mark.parametrize('cmd', ['/help 1', '/next 2', '/print 3 4'])
    def test_wrong_number_of_arguments(self, cmd):
        """ Проверяем, что корректно обрабатывается ввод команд
        с неправильным количеством аргументов.
        """
        with pytest.raises(errors.CommandArgsError):
            cli._run_one(cmd)



class TestCliPrintCommand():
    @pytest.mark.parametrize('num', [1, 2, 3, 4])
    def test_print_command_right_num(self, num):
        """Проверка функции печати с передачей номера тикета
        внутри диапазона имеющихся данных.
        """
        cli.USER = users.User(name='test_user', last_project=TEST_SUB_1)
        result = cli.print_command(num)
        assert result[0] == TEST_ISSUES[num-1]
        assert cli.USER.last_project.last_issue_num == num
        # проверки сохраненного в бд нет


    @pytest.mark.parametrize('num', [-1, 0, 5])
    def test_print_command_wrong_num(self, num):
        """Проверка функции печати с передачей номера тикета
        вне диапазона имеющихся данных."""
        cli.USER = users.User(name='test_user', last_project=TEST_SUB_1)
        with pytest.raises(errors.CommandArgsError):
            cli.print_command(num)


    @pytest.mark.parametrize('arg', ['siniy', 'traktor'])
    def test_print_command_wrong_arg(self, arg):
        """Проверка функции печати с передачей строки вместо номера."""
        cli.USER = users.User(name='test_user', last_project=TEST_SUB_1)
        with pytest.raises(errors.CommandArgsError):
            cli.print_command(arg)


    def test_print_command_no_num(self):
        """Проверка функции печати без передачи номера тикета.
        По умолчанию функция должна возвращать первые 10 тикетов."""
        cli.USER = users.User(name='test_user', last_project=TEST_SUB_1)
        result = cli.print_command(None)
        assert result == TEST_ISSUES[0:10]
        assert cli.USER.last_project.last_issue_num == len(TEST_ISSUES)


    def test_print_command_wrong_order(self):
        """Проверка функции печати без предварительного
        вызова команды /get."""
        cli.USER = None
        with pytest.raises(errors.IncorrectOder):
            cli.print_command(1)




class TestCliNextCommand():
    def test_next_command_right(self):
        """Проверка функции печати последующих 10 тикетов."""
        test_last_num = 2
        test_sub = subscriptions.Subscription('test_subs_name', TEST_ISSUES, test_last_num)
        cli.USER = users.User(name='test_user', last_project=test_sub)
        result = cli.next_command()
        assert result == TEST_ISSUES[test_last_num:test_last_num+10]
        assert cli.USER.last_project.last_issue_num == len(TEST_ISSUES)
        # проверки сохраненного в бд нет


    def test_next_command_wrong_order(self):
        """Проверка функции печати последующих 10 тикетов
        без предварительного вызова команды /get."""
        cli.USER = None
        with pytest.raises(errors.IncorrectOder):
            cli.next_command()


    def test_next_command_whole_list(self):
        """Проверка функции печати последующих 10 тикетов,
        когда все тикеты уже были просмотрены пользователем."""
        test_sub = subscriptions.Subscription('test_subs_name', TEST_ISSUES, 4)
        cli.USER = users.User(name='test_user', last_project=test_sub)
        with pytest.raises(errors.CommandArgsError):
            cli.next_command()



class TestCliLoginCommand():
    def test_login_command_with_no_name(self):
        """Проверка функции регистрации пользователя
        без передачи имени пользователя"""
        with pytest.raises(errors.CommandArgsError):
            cli.login_command()

    @pytest.mark.usefixtures('tmp_db', 'clean_file')
    @pytest.mark.parametrize('arg', ['продам', 'гараж', '88009632581'])
    def test_login_command_right(self, arg):
        """Проверка функции login пользователя"""
        cli.DB = self.db
        result = cli.login_command(arg)
        assert result.name == arg
        # проверки сохраненного в бд нет



class TestCliSubCommand():
    def test_sub_command_with_no_user(self):
        """Проверка функции подписки пользователя на репозиторий
        без предварительной регистрации пользователя"""
        with pytest.raises(errors.IncorrectOder):
            cli.USER = None
            cli.sub_command()


    def test_sub_command_with_no_name(self):
        """Проверка функции подписки пользователя на репозиторий
        без передачи имени проекта"""
        with pytest.raises(errors.CommandArgsError):
            cli.USER = users.User(name='test_user')
            cli.sub_command()


    @pytest.mark.usefixtures('tmp_db', 'clean_file')
    def test_sub_command_one_sub(self, mock_github):
        """Проверка функции подписки на репозиторий у нового пользователя"""
        cli.DB = self.db
        cli.USER = users.User(name='test_user_1')
        cli.DB.save_user(cli.USER)   # записываем юзера в дб
        cli.sub_command(TEST_SUB_1.name)   # добавляем новому пользователю 1 подписку
        assert cli.USER.subs == {TEST_SUB_1.name: TEST_SUB_1}
        # проверки сохраненного в бд нет


    @pytest.mark.usefixtures('tmp_db', 'clean_file')
    def test_sub_command_two_subs(self, mock_github):
        """Проверка функции подписки на репозиторий у пользователя с 1й подпиской"""
        cli.DB = self.db
        cli.USER = users.User(name='test_user_1')
        cli.DB.save_user(cli.USER)  # записываем юзера в дб
        cli.sub_command(TEST_SUB_1.name)  # добавляем новому пользователю 1 подписку
        assert cli.USER.subs == {TEST_SUB_1.name: TEST_SUB_1}    # проверяем что подписка одна
        cli.sub_command(TEST_SUB_2.name)  # добавляем еще 1 подписку
        assert cli.USER.subs == {TEST_SUB_1.name: TEST_SUB_1,
                                  TEST_SUB_2.name: TEST_SUB_2}   # проверяем что подписки две
        # проверки сохраненного в бд нет



@pytest.mark.usefixtures('tmp_db', 'clean_file')
class TestCliUnsubCommand():
    def test_unsub_command_with_no_user(self):
        """Проверка функции отписки пользователя от репозитория
        без предварительной регистрации пользователя"""
        with pytest.raises(errors.IncorrectOder):
            cli.USER = None
            cli.unsub_command()


    def test_unsub_command_with_no_name(self):
        """Проверка функции отписки пользователя от репозитория
        без передачи имени проекта"""
        with pytest.raises(errors.CommandArgsError):
            cli.USER = users.User(name='test_user')
            cli.unsub_command()


    def test_unsub_command_one_sub(self, mock_github):
        """Проверка функции отписки от репозитория у пользователя с одной подпиской"""
        cli.DB = self.db
        cli.USER = users.User(name='test_user_1')
        cli.DB.save_user(cli.USER)  # записываем юзера в дб
        cli.sub_command(TEST_SUB_1.name)  # добавляем новому пользователю 1 подписку
        assert cli.USER.subs == {TEST_SUB_1.name: TEST_SUB_1}  # проверяем что подписка есть
        cli.unsub_command(TEST_SUB_1.name)   # удаляем пользователю эту подписку
        assert cli.USER.subs == {}
        # проверки сохраненного в бд нет


    def test_unsub_command_two_subs(self, mock_github):
        """Проверка функции отписки от репозитория у пользователя с 2мя подписками"""
        cli.DB = self.db
        cli.USER = users.User(name='test_user_1')
        cli.DB.save_user(cli.USER)  # записываем юзера в дб
        cli.sub_command(TEST_SUB_1.name)  # добавляем новому пользователю 1 подписку
        cli.sub_command(TEST_SUB_2.name)    # добавляем вторую
        assert cli.USER.subs == {TEST_SUB_1.name: TEST_SUB_1,
                                 TEST_SUB_2.name: TEST_SUB_2}    # проверяем что обе на месте
        cli.unsub_command(TEST_SUB_2.name)   # удаляем пользователю подписку
        assert cli.USER.subs == {TEST_SUB_1.name: TEST_SUB_1}
        # проверки сохраненного в бд нет



@pytest.mark.usefixtures('tmp_db', 'clean_file')
class TestCliUpdateCommand():
    def test_update_command_with_no_user(self):
        """Проверка функции обновления подписок пользователя
        без предварительной регистрации пользователя"""
        with pytest.raises(errors.IncorrectOder):
            cli.USER = None
            cli.update_command()


    def test_update_command_with_no_since_date_with_one_sub(self, mock_github):
        """Проверка функции обновления подписок пользователя
        без передачи даты начала обновления (по умолчанию функция
        должна обновить с последнего просмотренного юзером тикета)"""
        cli.DB = self.db
        cli.USER = users.User(name='test_user_1')
        cli.DB.save_user(cli.USER)  # записываем юзера в дб
        cli.sub_command(TEST_SUB_1.name)  # добавляем новому пользователю 1 подписку
        # подписка добавляется только что подгруженная, поэтому last_issue_num у нее = 0
        # проверяем ожидаемую подписку (при сравнении не учитывается последний просмотренный исус)
        assert cli.USER.subs == {TEST_SUB_1.name: TEST_SUB_1}
        assert cli.USER.subs[TEST_SUB_1.name].last_issue_num == 0
        cli.update_command(None)    # обновляем подписки и сравниваем с ожидаемым результатом
        assert cli.USER.subs[TEST_SUB_1.name].last_issue_num == 4
        # проверки сохраненного в бд нет


    def test_update_command_with_no_since_date_with_two_subs(self, mock_github):
        """Проверка функции обновления подписок пользователя
        без передачи даты начала обновления (по умолчанию функция
        должна обновить с последнего просмотренного юзером тикета)"""
        cli.DB = self.db
        cli.USER = users.User(name='test_user_1')
        cli.DB.save_user(cli.USER)  # записываем юзера в дб
        cli.sub_command(TEST_SUB_1.name)  # добавляем новому пользователю 1 подписку
        cli.sub_command(TEST_SUB_2.name)  # добавляем вторую
        assert cli.USER.subs == {TEST_SUB_1.name: TEST_SUB_1,
                                 TEST_SUB_2.name: TEST_SUB_2}  # проверяем что обе на месте

        assert cli.USER.subs[TEST_SUB_1.name].last_issue_num == 0
        assert cli.USER.subs[TEST_SUB_2.name].last_issue_num == 0
        cli.update_command(None)    # обновляем подписки и сравниваем с ожидаемым результатом
        assert cli.USER.subs[TEST_SUB_1.name].last_issue_num == 4
        assert cli.USER.subs[TEST_SUB_2.name].last_issue_num == 4
        # проверки сохраненного в бд нет


    @pytest.mark.parametrize('since_date', ['2021-01-01', '2021-02-02', '2020-01-01'])
    def test_update_command_with_since_date_with_one_sub(self, mock_github, since_date):
        """Проверка функции обновления подписок пользователя с 1й
        подпиской c определенной даты"""
        cli.DB = self.db
        cli.USER = users.User(name='test_user_1')
        cli.DB.save_user(cli.USER)  # записываем юзера в дб
        cli.sub_command(TEST_SUB_1.name)  # добавляем новому пользователю 1 подписку
        assert cli.USER.subs == {TEST_SUB_1.name: TEST_SUB_1}  # проверяем ожидаемую подписку
        assert cli.USER.subs[TEST_SUB_1.name].last_issue_num == 0
        cli.update_command(since_date)    # обновляем подписки и сравниваем с ожидаемым результатом
        test_list = [i for i in TEST_ISSUES if date.fromisoformat(i[2]) >= date.fromisoformat(since_date)]
        assert cli.USER.subs[TEST_SUB_1.name].last_issue_num == len(test_list)
        # проверки сохраненного в бд нет


    @pytest.mark.parametrize('since_date', ['2021-01-01', '2021-02-02', '2020-01-01'])
    def test_update_command_with_since_date_with_two_subs(self, mock_github, since_date):
        """Проверка функции обновления подписок пользователя с 2мя
        подписками c определенной даты"""
        cli.DB = self.db
        cli.USER = users.User(name='test_user_1')
        cli.DB.save_user(cli.USER)  # записываем юзера в дб
        cli.sub_command(TEST_SUB_1.name)  # добавляем новому пользователю 1 подписку
        cli.sub_command(TEST_SUB_2.name)  # добавляем вторую
        assert cli.USER.subs == {TEST_SUB_1.name: TEST_SUB_1,
                                 TEST_SUB_2.name: TEST_SUB_2}  # проверяем что обе на месте
        assert cli.USER.subs[TEST_SUB_1.name].last_issue_num == 0
        assert cli.USER.subs[TEST_SUB_2.name].last_issue_num == 0
        cli.update_command(since_date)    # обновляем подписки и сравниваем с ожидаемым результатом
        test_list = [i for i in TEST_ISSUES if date.fromisoformat(i[2]) >= date.fromisoformat(since_date)]
        assert cli.USER.subs[TEST_SUB_1.name].last_issue_num == len(test_list)
        assert cli.USER.subs[TEST_SUB_2.name].last_issue_num == len(test_list)
        # проверки сохраненного в бд нет
