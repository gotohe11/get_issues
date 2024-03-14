from typing import Dict
import sys
import requests
from tabulate import tabulate
from github import make_issues_list, GithubError, ProjectNotFoundError


ISSUES_LIST = []
LAST_ISSUE_NUM = 0


def pretty_print_issues(issues_list, num_start, num_finish=100):
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
    print(tabulate(issues_list[num_start-1:num_finish], headers=columns))


def help_command(*args):
    print(
        'Available commands:\n'
        '/help - commands info;\n'
        '/exit - exit;\n'
        '/get <owner>/<repo> (for example, "/get s0md3v/Photon") - '
        'gets repo issues list and prints the amount of them;\n'
        '/print N - prints the N-th issue (if there is no N, prints 10 newest issues);\n'
        '/next - prints the next 10 issues or the remainder'
        )


def get_command(*args):
    project_name = args[0]
    success = False
    while not success:
        try:
            global ISSUES_LIST
            ISSUES_LIST = make_issues_list(project_name)
        except ProjectNotFoundError:
            print(f'Project "{project_name}" not found, check your spelling.')
            ISSUES_LIST = []
            break
        except GithubError as err:
            print(f'Error communicating with Github: {err}')
            break

        success = True
        global LAST_ISSUE_NUM
        LAST_ISSUE_NUM = 0
        print(f'There are {len(ISSUES_LIST)} issues in the "{project_name}" repository.')


def exit_command(*args):
    sys.exit()


def print_command(issues_list, *args):
    if args:
        if args[0].isdigit():
            issue_number = int(args[0])
            if issue_number < 1 or issue_number > len(issues_list):
                print('The number is out of range. Try again.')
            else:
                pretty_print_issues(issues_list, issue_number, issue_number)
                global LAST_ISSUE_NUM
                LAST_ISSUE_NUM = issue_number
        else:
            print('ValueError. Check your spelling and try again.')    # или здесь сделать исключение?

    else:
        pretty_print_issues(issues_list, 1, 10)
        LAST_ISSUE_NUM = 10


def next_command(issues_list, *args):
    global LAST_ISSUE_NUM
    num_1 = LAST_ISSUE_NUM + 1
    num_2 = num_1 + 9
    if num_1 < 1 or num_1 > len(issues_list):
        print('You have seen the whole issues list.')
    else:
        pretty_print_issues(issues_list, num_1, num_2)
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
            if cmd == '/get' or cmd == '/exit' or cmd == '/help':
                command_dict[cmd](*args)
            elif not ISSUES_LIST:
                print('Firstly, try the command "/get <owner>/<repo>".')
                continue
            else:
                command_dict[cmd](ISSUES_LIST, *args)



if __name__ == "__main__":
    run()
