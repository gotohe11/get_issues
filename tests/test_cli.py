import pytest
import cli
import github

def _fake_issues():
    ISSUES_LIST = [
        (1, 'LICENSE file missing from root directory', '2021-05-06', '2021-05-06', 0),
        (2, 'Stackoverflow refused connection try again', '2021-01-10', '2022-01-14', 5),
        (3, 'Windows 10 -Cygwin Error "UnicodeDecodeError: \'utf-8\' codec can\'t decode byte 0xf3 in position "',
           '2020-12-01', '2021-01-03', 0),
        (4, 'Sorry, Stack Overflow blocked our request. Try again in a minute.', '2020-11-30', '2021-06-07', 11),
        (5, 'New Features for Rebound', '2020-10-17', '2021-01-03', 1),
        (6, 'Code should be distributed across files', '2020-02-09', '2020-02-09', 0),
        (7, 'can we make this to run on windows without using Cygwin?', '2019-11-20', '2021-01-03', 1),
        (8, "Doesn't work on Cygwin either", '2019-05-31', '2021-01-03', 1),
        (9, 'Fix formatting for questions with duplicates', '2018-04-17', '2019-09-03', 3),
        (10, 'Make the scrollbar smaller, change its color, and move it away from the text', '2018-04-17',
            '2018-04-17', 0),
        (11, 'Add formatting for Q/As with blockquotes and markdown', '2018-04-17', '2019-06-09', 1),
        (12, 'Make links clickable in each Q/A', '2018-04-04', '2018-04-30', 1),
        (13, 'Extract search criteria / keywords from the stack trace', '2018-04-02', '2019-05-15', 1),
        (14, 'Create a test suite for each supported language', '2018-03-14', '2020-06-21', 5)
    ]
    return ISSUES_LIST


def _fake_ask_user(value='/help'):
    return value


LAST_ISSUE_NUM = 2
ISSUES_LIST = _fake_issues()
#github.make_issues_list = _fake_issues()
cli.ask_user = _fake_ask_user('/help')


def test_run():
    cli.ask_user = _fake_ask_user('/help')
    with pytest.raises(TypeError):
        assert cli.run()



#PASSED потому что обращается по API и собирает настоящие списки))
@pytest.mark.parametrize('input_data, res',
                         [('shobrook/rebound', 'success'),
                          ('s0md3v/Photon', 'success'),
                          ('karpathy/neuraltalk2', 'success')])
def test_get_command(input_data, res):
    assert cli.get_command(input_data) == res

#FAILED
@pytest.mark.parametrize('input_data, res',
                          [(5, 'success')
                                       ])
def test_print_command(input_data, res):
    #temp_list = _fake_issues()
    #monkeypatch.setattr(cli, ISSUES_LIST, temp_list)
    assert cli.print_command(input_data) == res

#FAILED
def test_next_command():
    c1 = LAST_ISSUE_NUM
    c2 = ISSUES_LIST
    assert cli.next_command() == 'success'





#@pytest.fixture()
# def get_dict_value(arg):
#     command_dict = {
#         '/help': help_command,
#         '/get': get_command,
#         '/exit': exit_command,
#         '/print': print_command,
#        '/next': next_command
#     }
#     return command_dict[arg]
#
#
# @pytest.mark.parametrize('input_data, res',
#                          [('/help', get_dict_value)
#                          ])
# def test_run(input_data, res):
#     assert run() == res

