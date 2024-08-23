import pytest
from .. import cli, errors, github, database, users, subscriptions


JUST_ISSUES = [
    (1, 'Title #1', '2021-05-06', '2021-05-06', 0),
    (2, 'Title #2', '2021-01-10', '2022-01-14', 5),
    (3, 'Title #3', '2020-12-01', '2021-01-03', 0),
    (4, 'Title #4', '2020-11-30', '2021-06-07', 11)
]

TEST_ISSUES = subscriptions.Subscription.make_named_tuples(JUST_ISSUES, 'test/test')
TEST_SUB = subscriptions.Subscription('test_subs_name', TEST_ISSUES, 0)
TEST_USER = users.User(name='test_user', last_project=TEST_SUB)    # юзер, листающий проект

test_issues_1 = subscriptions.Subscription.make_named_tuples(JUST_ISSUES, 'test_1/test_1')
TEST_SUB_1 = subscriptions.Subscription('test_1/test_1', test_issues_1, 0)    # ожидаемая подписка 1
test_issues_2 = subscriptions.Subscription.make_named_tuples(JUST_ISSUES, 'test_2/test_2')
TEST_SUB_2 = subscriptions.Subscription('test_2/test_2', test_issues_2, 0)  # ожидаемая подписка 2

TEST_USER_1 = users.User(name='test_user_1', subs={TEST_SUB_1.name: TEST_SUB_1})    # юзер с одной подпиской
TEST_USER_2 = users.User(name='test_user_1', subs={TEST_SUB_1.name: TEST_SUB_1, TEST_SUB_2.name: TEST_SUB_2})   # юзер с 2мя подписками

TEST_DB = DB = database.Database('/tmp/test_data_cli.json')


@pytest.fixture()
def command_stub():
    """ Добавляет специальную команду, которую можно использовать в тестах
    для проверки парсера, не думая о том, чтобы внутри самой команды корректно
    работало.
    """

    def _stub(*args):
        """ Команда-заглушка возвращает свои аргументы. """
        return args

    cli.command_dict['/stub'] = _stub
    yield
    del cli.command_dict['/stub']


@pytest.fixture()
def mock_github():
    """ Вешаем заглушку на Github API.
    """
    def _github_mock(project_name: str):
        if project_name in ['test/test', 'test_1/test_1', 'test_2/test_2']:
            return JUST_ISSUES
        else:
            raise github.ProjectNotFoundError

    original_fn = github.make_issues_list
    github.make_issues_list = _github_mock
    yield
    github.make_issues_list = original_fn


@pytest.mark.parametrize('cmd', ['/bad', 'next'])    # +
def test_missing_command(cmd):
    """ Проверяем, что корректно обрабатывается ввод не существующей команды.
    """
    with pytest.raises(errors.CommandNotFound):
        cli._run_one(cmd)


def test_case_and_whitespace(command_stub):    # +
    """ Проверяем, что парсер команд не чувствителен к регистру ввода и лишним
    пробелам.
    """
    result = cli._run_one('  /StUb a1   a2 a3  ')
    assert list(result) == ['a1', 'a2', 'a3']


def test_get_ok(mock_github):    # + fixed
    """ Проверяем основной сценарий выполнения команды /get.
    """
    result = cli._run_one('/get test/test')
    assert cli.USER.last_project.issues_list == TEST_ISSUES


#  #  #
@pytest.mark.parametrize('cmd', ['/help 1', '/next 2', '/print 3 4'])    # +
def test_wrong_number_of_arguments(cmd):
    """ Проверяем, что корректно обрабатывается ввод команд
    с неправильным количеством аргументов.
    """
    with pytest.raises(errors.CommandArgsError):
        cli._run_one(cmd)


# print_command_tests
@pytest.mark.parametrize('num', [1, 2, 3, 4])    # + fixed
def test_print_command_right_num(num):
    """Проверка функции печати с передачей номера тикета
    внутри диапазона имеющихся данных.
    """
    cli.USER = TEST_USER
    result = cli.print_command(num)
    assert result[0] == TEST_ISSUES[num-1]


@pytest.mark.parametrize('num', [-1, 0, 5])    # + fixed
def test_print_command_wrong_num(num):
    """Проверка функции печати с передачей номера тикета
    вне диапазона имеющихся данных."""
    cli.USER = TEST_USER
    with pytest.raises(errors.CommandArgsError):
        cli.print_command(num)


@pytest.mark.parametrize('arg', ['siniy', 'traktor'])    # + fixed
def test_print_command_wrong_arg(arg):
    """Проверка функции печати с передачей строки вместо номера."""
    cli.USER = TEST_USER
    with pytest.raises(errors.CommandArgsError):
        cli.print_command(arg)


def test_print_command_no_num():    # + fixed
    """Проверка функции печати без передачи номера тикета.
    По умолчанию функция должна возвращать первые 10 тикетов."""
    cli.USER = TEST_USER
    result = cli.print_command(None)
    assert result == TEST_ISSUES[0:10]


def test_print_command_wrong_order():    # + fixed
    """Проверка функции печати без предварительного
    вызова команды /get."""
    cli.USER = None
    with pytest.raises(errors.IncorrectOder):
        cli.print_command(1)


# next_command_tests
def test_next_command_right():    # + fixed
    """Проверка функции печати последующих 10 тикетов."""
    TEST_SUB_2 = subscriptions.Subscription('test_subs_name', TEST_ISSUES, 2)
    cli.USER = users.User(name='test_user', last_project=TEST_SUB_2)
    test_last_num = 2
    result = cli.next_command()
    assert result == TEST_ISSUES[test_last_num:test_last_num+10]


def test_next_command_wrong_order():    # + fixed
    """Проверка функции печати последующих 10 тикетов
    без предварительного вызова команды /get."""
    cli.USER = None
    with pytest.raises(errors.IncorrectOder):
        cli.next_command()


def test_next_command_whole_list():    # + fixed
    """Проверка функции печати последующих 10 тикетов,
    когда все тикеты уже были просмотрены пользователем."""
    TEST_SUB_4 = subscriptions.Subscription('test_subs_name', TEST_ISSUES, 4)
    cli.USER = users.User(name='test_user', last_project=TEST_SUB_4)
    with pytest.raises(errors.CommandArgsError):
        cli.next_command()



### login_command_tests
def test_login_command_with_no_name():
    """Проверка функции регистрации пользователя
    без передачи имени пользователя"""
    with pytest.raises(errors.CommandArgsError):
        cli.login_command()


@pytest.mark.parametrize('arg', ['test_user_1', 'test_user_2', 'test_user_3'])
def test_login_command_right(arg):
    """Проверка функции login пользователя"""
    test_user = users.User(arg)
    cli.DB = TEST_DB
    res = cli.login_command(arg)
    assert res == test_user


# sub_command_tests работают только с зарегаными юзерами (поэтому сначала надо прогнать тесты login)
def test_sub_command_with_no_user():
    """Проверка функции подписки пользователя на репозиторий
    без предварительной регистрации пользователя"""
    with pytest.raises(errors.IncorrectOder):
        cli.USER = None
        cli.sub_command()


def test_sub_command_with_no_name():
    """Проверка функции подписки пользователя на репозиторий
    без передачи имени проекта"""
    with pytest.raises(errors.CommandArgsError):
        cli.USER = TEST_USER
        cli.sub_command()


def test_sub_command_right_one(mock_github):
    """Проверка функции подписки на репозиторий у нового пользователя"""
    cli.USER = users.User(name='test_user_1')
    cli.DB = TEST_DB
    cli.sub_command('test_1/test_1')   # добавляем новому пользователю 1 подписку
    assert TEST_USER_1 == cli.USER    # сравниваем результат с пользователем с 1й ожидаемой подпиской


def test_sub_command_right_two(mock_github):
    """Проверка функции подписки на репозиторий у пользователя с подпиской"""
    cli.USER = TEST_USER_1
    cli.DB = TEST_DB
    cli.sub_command('test_2/test_2')   # добавляем пользователю еще 1 подписку
    assert TEST_USER_2 == cli.USER    # сравниваем результат с пользователем с ожидаемыми подписками

# проверка наличия проекта в подписках совершается в модуле User


# unsub_command_tests работают только с зарегаными юзерами (поэтому сначала надо прогнать тесты login)
def test_unsub_command_with_no_user():
    """Проверка функции отписки пользователя от репозитория
    без предварительной регистрации пользователя"""
    with pytest.raises(errors.IncorrectOder):
        cli.USER = None
        cli.unsub_command()


def test_unsub_command_with_no_name():
    """Проверка функции отписки пользователя от репозитория
    без передачи имени проекта"""
    with pytest.raises(errors.CommandArgsError):
        cli.USER = TEST_USER
        cli.unsub_command()


def test_unsub_command_right_two(mock_github):
    """Проверка функции отписки от репозитория у пользователя с 2мя подписками"""
    cli.USER = TEST_USER_1    # у него в файле уже 2 подписки после предыдущих тестов
    cli.DB = TEST_DB
    cli.unsub_command('test_2/test_2')   # удаляем пользователю 1 подписку
    assert TEST_USER_1 == cli.USER    # сравниваем результат с пользователем с 1й ожидаемой подпиской


def test_unsub_command_right_one(mock_github):    # !!!!
    """Проверка функции отписки от репозитория у пользователя с 2мя подписками"""
    cli.USER = TEST_USER_1    # у него в файле уже 1 подписки после предыдущих тестов
    cli.DB = TEST_DB
    cli.unsub_command('test_1/test_1')   # удаляем пользователю 2ю подписку
    test_user_0 = users.User(name='test_user_1')
    assert test_user_0 == cli.USER    # сравниваем результат с пользователем без подписок


# update_command_tests работают только с зарегаными юзерами (поэтому сначала надо прогнать тесты login)
def test_update_command_with_no_user():
    """Проверка функции отписки пользователя от репозитория
    без предварительной регистрации пользователя"""
    with pytest.raises(errors.IncorrectOder):
        cli.USER = None
        cli.update_command()


# в конце надо не забыть удалить файл