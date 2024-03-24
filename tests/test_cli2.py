import pytest
from .. import cli, errors, github


TEST_LAST_ISSUE_NUM = 0
TEST_ISSUES = [
    (1, 'Title #1', '2021-05-06', '2021-05-06', 0),
    (2, 'Title #2', '2021-01-10', '2022-01-14', 5),
    (3, 'Title #3', '2020-12-01', '2021-01-03', 0),
    (4, 'Title #4', '2020-11-30', '2021-06-07', 11),
]


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
        if project_name == 'test/test':
            return TEST_ISSUES
        else:
            raise github.ProjectNotFoundError

    original_fn = github.make_issues_list
    github.make_issues_list = _github_mock
    yield
    github.make_issues_list = original_fn


@pytest.mark.parametrize('cmd', ['/bad', 'next'])
def test_missing_command(cmd):
    """ Проверяем, что корректно обрабатывается ввод не существующей команды.
    """
    with pytest.raises(errors.CommandNotFound):
        cli._run_one(cmd)


def test_case_and_whitespace(command_stub):
    """ Проверяем, что парсер команд не чувствителен к регистру ввода и лишним
    пробелам.
    """
    result = cli._run_one('  /StUb a1   a2 a3  ')
    assert list(result) == ['a1', 'a2', 'a3']


def test_get_ok(mock_github):
    """ Проверяем основной сценарий выполнения команды /get.
    """
    result = cli._run_one('/get test/test')
    assert cli.ISSUES_LIST == TEST_ISSUES


#  #  #
@pytest.mark.parametrize('cmd', ['/help 1', '/next 2', '/print 3 4'])
def test_wrong_number_of_arguments(cmd):
    """ Проверяем, что корректно обрабатывается ввод команд
    с неправильным количеством аргументов.
    """
    with pytest.raises(errors.CommandArgsError):
        cli._run_one(cmd)


# print_command_tests
@pytest.mark.parametrize('num', [1, 2, 3, 4])
def test_print_command_right_num(num):
    """Проверка функции печати с передачей номера тикета
    внутри диапазона имеющихся данных.
    """
    cli.ISSUES_LIST = TEST_ISSUES
    result = cli.print_command(num)
    assert result[0] == TEST_ISSUES[num-1]    # надо это как-то покрасивше сделать


@pytest.mark.parametrize('num', [-1, 0, 5])
def test_print_command_wrong_num(num):
    """Проверка функции печати с передачей номера тикета
    вне диапазона имеющихся данных."""
    cli.ISSUES_LIST = TEST_ISSUES
    with pytest.raises(errors.CommandArgsError):
        cli.print_command(num)


@pytest.mark.parametrize('arg', ['suka', 'blyat'])
def test_print_command_wrong_arg(arg):
    """Проверка функции печати с передачей строки вместо номера."""
    cli.ISSUES_LIST = TEST_ISSUES
    with pytest.raises(errors.CommandArgsError):
        cli.print_command(arg)


def test_print_command_no_num():
    """Проверка функции печати без передачи номера тикета.
    По умолчанию функция должна возвращать первые 10 тикетов."""
    cli.ISSUES_LIST = TEST_ISSUES
    result = cli.print_command(None)
    assert result == TEST_ISSUES[0:10]


def test_print_command_wrong_order():
    """Проверка функции печати без предварительного
    вызова команды /get."""
    cli.ISSUES_LIST = []
    with pytest.raises(errors.IncorrectOder):
        cli.print_command(1)


# next_command_tests
def test_next_command_right():
    """Проверка функции печати последующих 10 тикетов."""
    cli.ISSUES_LIST = TEST_ISSUES
    cli.LAST_ISSUE_NUM = TEST_LAST_ISSUE_NUM
    result = cli.next_command()
    assert result == TEST_ISSUES[0:10]


def test_next_command_wrong_order():
    """Проверка функции печати последующих 10 тикетов
    без предварительного вызова команды /get."""
    cli.ISSUES_LIST = []
    with pytest.raises(errors.IncorrectOder):
        cli.next_command()


def test_next_command_whole_list():
    """Проверка функции печати последующих 10 тикетов,
    когда все тикеты уже были просмотрены пользователем."""
    cli.ISSUES_LIST = TEST_ISSUES
    cli.LAST_ISSUE_NUM = TEST_LAST_ISSUE_NUM + len(TEST_ISSUES)
    with pytest.raises(errors.CommandArgsError):
        cli.next_command()
