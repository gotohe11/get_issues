from typing import Dict
import sys
import requests
from tabulate import tabulate
from github import make_issues_list, GithubError, ProjectNotFoundError


ISSUES_LIST = []
LAST_ISSUE_NUM = 0


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
            ISSUES_LIST = make_issues_list(project_name)
        except ProjectNotFoundError:
            print(f'Project "{project_name}" not found, check your spelling.')
            ISSUES_LIST = []
            break
        except GithubError as err:
            print(f'Error communicating with Github: {err}')
            break
        success = True
        LAST_ISSUE_NUM = 0
        print(f'There are {len(ISSUES_LIST)} issues in the "{project_name}" repository.')


def exit_command():
    sys.exit()


def print_command(issue_number=None):
    global ISSUES_LIST
    global LAST_ISSUE_NUM

    if not ISSUES_LIST:
        print('Firstly, try the command "/get <owner>/<repo>".')
        return

    if issue_number is None:
        # prints first 10, if no args
        limit = 10
        skip = 0
    else:
        limit = 1
        try:
            skip = int(issue_number) - 1
        except ValueError:
            print('Enter a number with "/print" command, not a string.')
            return

    pretty_print_issues(skip, skip + limit)
    LAST_ISSUE_NUM = skip + limit


def next_command():
    global ISSUES_LIST
    global LAST_ISSUE_NUM

    if not ISSUES_LIST:
        print('Firstly, try the command "/get <owner>/<repo>".')
        return

    num_1 = LAST_ISSUE_NUM
    num_2 = num_1 + 10
    if num_1 < 1 or num_1 > len(ISSUES_LIST):
        print('You have seen the whole issues list.')
    else:
        pretty_print_issues(num_1, num_2)
        LAST_ISSUE_NUM = num_2


command_dict = {
    '/help': help_command,
    '/get': get_command,
    '/exit': exit_command,
    '/print': print_command,
    '/next': next_command
}


def run():
    """ Запускает пользовательский (консольный) интерфейс приложения.

    Чтобы "запуск" не был совсем тривиальным, реализуем перезапрос в случае
    ошибок.
    """
    while True:
        user_command = input('Enter the command '
                            '(for more information about commands input "/help"): ')
        parts = user_command.lower().split()
        cmd = parts[0]
        if len(parts) > 1:
            args = parts[1:]
        else:
            args = []

        if cmd not in command_dict.keys():
            print(f'The command "{cmd}" not found. Try again.')
            continue
        else:
            try:
                command_dict[cmd](*args)
            except TypeError:
                print('Wrong number of arguments provided. '
                      'Or arguments added when it was not necessary.')



if __name__ == "__main__":
    run()
