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
    :param issues_list: list of issues
    :param num_start: required number of issues
    :param num_finish: required number of issues
    :return: data table
    """
    #print(f'List of issues in the "{project_name}" repository:')
    columns = ['№', 'title', 'created at', 'updated at', 'comments']
    print(tabulate(ISSUES_LIST[num_start-1:num_finish], headers=columns))


def help_command():
    print(
        'Available commands:\n'
        '/help - commands info;\n'
        '/exit - exit;\n'
        '/get <owner>/<repo> (for example, "/get s0md3v/Photon") - '
        'gets repo issues list and prints the amount of them;\n'
        '/print N - prints the N-th issue (if there is no N, prints 10 newest issues);\n'
        '/next - prints the next 10 issues or the remainder'
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


def print_command(*args):
    global ISSUES_LIST
    global LAST_ISSUE_NUM

    if not ISSUES_LIST:
        print('Firstly, try the command "/get <owner>/<repo>".')
    else:
        if args:
            if args[0].isdigit():
                issue_number = int(args[0])
                if issue_number < 1 or issue_number > len(ISSUES_LIST):
                    print('The number is out of range. Try again.')
                else:
                    pretty_print_issues(issue_number, issue_number)
                    LAST_ISSUE_NUM = issue_number
            else:
                print('ValueError. Check your spelling and try again.')    # или здесь сделать исключение?
        else:
            pretty_print_issues(1, 10)
            LAST_ISSUE_NUM = 10


def next_command():
    global ISSUES_LIST
    global LAST_ISSUE_NUM

    if not ISSUES_LIST:
        print('Firstly, try the command "/get <owner>/<repo>".')
    else:
        num_1 = LAST_ISSUE_NUM + 1
        num_2 = num_1 + 9
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
            command_dict[cmd](*args)



if __name__ == "__main__":
    run()
