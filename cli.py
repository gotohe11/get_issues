import sys
from tabulate import tabulate
import json

from . import errors
from . import github
from . import users
from . import subscriptions
from . import database


ISSUES_LIST = []
LAST_ISSUE_NUM = 0
USER = None    # несет экземпляр класса юзер


def pretty_print_issues(num_start, num_finish=100):
    """
    Prints a list of issues sorted by creation date (by default),
    in the form of a table.
    :param num_start: required number of issues
    :param num_finish: required number of issues
    :return: data table
    """
    columns = ['№', 'title', 'created at', 'updated at', 'comments']
    print(tabulate(ISSUES_LIST[num_start:num_finish], headers=columns))


def help_command():
    print(
        'Available commands:\n'
        '/help - commands info;\n'
        '/exit - exit;\n'
        '/get <owner>/<repo> (for example, "/get s0md3v/Photon") - '
        'gets repo issues list and prints the amount of them;\n'
        '/print N - prints the N-th issue (if there is no N, prints 10 newest issues);\n'
        '/next - prints the next 10 issues or the remainder.'
        )


def get_command(project_name):
    global ISSUES_LIST
    global LAST_ISSUE_NUM

    success = False
    while not success:
        try:
            ISSUES_LIST = github.make_issues_list(project_name)
        except github.ProjectNotFoundError:
            print(f'Project "{project_name}" not found, check your spelling.')
            ISSUES_LIST = []
            break
        except github.GithubError as err:
            print(f'Error communicating with Github: {err}')
            break
        success = True
        LAST_ISSUE_NUM = 0
        print(f'There are {len(ISSUES_LIST)} issues in the "{project_name}" repository.')
        return ISSUES_LIST


def exit_command():
    sys.exit()


def print_command(issue_number=None):
    global ISSUES_LIST
    global LAST_ISSUE_NUM

    if not ISSUES_LIST:
        raise errors.IncorrectOder('Firstly, try the command '
                                   '"/get <owner>/<repo>".')
    if issue_number is None:
        # prints first 10, if no args
        limit = 10
        skip = 0
    else:
        limit = 1
        try:
            skip = int(issue_number) - 1
        except ValueError:
            raise errors.CommandArgsError('Enter a number with "/print" '
                                          'command, not a string.')
        if skip >= len(ISSUES_LIST) or skip < 0:
            raise errors.CommandArgsError('Number out of issues list range.')

    pretty_print_issues(skip, skip+limit)
    LAST_ISSUE_NUM = skip + limit
    return ISSUES_LIST[skip:skip+limit]


def next_command():
    global ISSUES_LIST
    global LAST_ISSUE_NUM

    if not ISSUES_LIST:
        raise errors.IncorrectOder('Firstly, try the command '
                                   '"/get <owner>/<repo>".')
    num_1 = LAST_ISSUE_NUM
    num_2 = num_1 + 10
    if num_1 < 0 or num_1 >= len(ISSUES_LIST):
        raise errors.CommandArgsError('You have seen the whole issues list.')
    else:
        pretty_print_issues(num_1, num_2)
        LAST_ISSUE_NUM = num_2
        return ISSUES_LIST[num_1:num_2]


def login_command(user_name='no_name'):   # имя получилось нечувств к регистру
    if user_name == 'no_name':
        raise errors.CommandArgsError('You should text your login-name first')
    global USER
    USER = database.Database.load_user(user_name)



def sub_command(project_name=None):
    if not project_name:
        raise errors.CommandArgsError('You forgot to text a project name')
    global USER
    if not USER:
        raise errors.IncorrectOder('To subscribe a project, you first need to log in. '
                                   'Try </login> command')
    try:
        USER.add_subsc(project_name)
        database.Database.save_sub(USER)  # просто переписываем весь список подписок юзера заново
        print(f'{USER.name}, you subscribed to "{project_name}" repository.')
    except NameError as er:
        print(er)



def unsub_command(project_name=None):
    if not project_name:
        raise errors.CommandArgsError('You forgot to text a project name')
    global USER
    if not USER:
        raise errors.IncorrectOder('To unsubscribe from a project, you first need to log in. '
                                   'Try </login> command')
    try:
        USER.remove_subsc(project_name)   # удаляем ненужную из списка подписок экз.класса Юзер
        database.Database.save_sub(USER)  # просто переписываем весь список подписок Юзера заново
        print(f'{USER.name}, you unsubscribed from the "{project_name}" repository.')

    except NameError as er:
        print(er)



command_dict = {
    '/help': help_command,
    '/get': get_command,
    '/exit': exit_command,
    '/print': print_command,
    '/next': next_command,
    '/login': login_command,
    '/sub': sub_command,
    '/unsub': unsub_command

}


def ask_user():
    return input('Enter the command '
                 '(for more information about commands input "/help"): ')


def _run_one(command: str):
    parts = command.lower().split()
    cmd = parts[0]
    if len(parts) > 1:
        args = parts[1:]
    else:
        args = []

    if cmd not in command_dict:
        raise errors.CommandNotFound('Command not found')

    try:
        return command_dict[cmd](*args)
    except TypeError:
        raise errors.CommandArgsError('Wrong number of arguments provided.')


def run():
    """ Запускает пользовательский (консольный) интерфейс приложения.
    Чтобы "запуск" не был совсем тривиальным, реализуем перезапрос в случае
    ошибок.
    """
    while True:
        user_command = ask_user()
        try:
            _run_one(user_command)
        except errors.CommandError as exc:
            print(exc)


if __name__ == "__main__":
    run()
