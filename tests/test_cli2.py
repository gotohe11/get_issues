import pytest

from .. import cli, errors, github


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


TEST_ISSUES = [
    (1, 'Title #1', '2021-05-06', '2021-05-06', 0),
    (2, 'Title #2', '2021-01-10', '2022-01-14', 5),
    (3, 'Title #3', '2020-12-01', '2021-01-03', 0),
    (4, 'Title #4', '2020-11-30', '2021-06-07', 11),
]


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
