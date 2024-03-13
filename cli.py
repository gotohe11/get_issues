from typing import Dict
import sys
import requests
from tabulate import tabulate
from github import make_issues_list, GithubError, ProjectNotFoundError


def pretty_print_issues(lst, num_start, num_finish=len(lst)):
    """
    Prints a list of issues sorted by creation date (by default),
    in the form of a table.
    :param lst: list of issues
    :param num_start: required number of issues
    :param num_finish: required number of issues
    :return: data table
    """

    #print(f'List of issues in the "{project_name}" repository:')
    columns = ['№', 'title', 'created at', 'updated at', 'comments']
    print(tabulate(lst[num_start-1:num_finish], headers=columns))


def help_command(*args):
    print(
        'Available commands:\n'
        '/help - commands info;\n'
        '/exit - exit;\n'
        '/print N - prints the N-th issue (if there is no N, prints 10 newest issues);\n'
        '/next - print the next 10 issues'
        )


def exit_command(*args):
    sys.exit()


def print_command(issues_list, issue_number):
    if issue_number:
        pretty_print_issues(issues_list, issue_number, issue_number)
    else:
        pretty_print_issues(issues_list, 1, 10)


def next_command(issues_list, num_1):
    # как следить за последним номером?
    num_2 = num_1 + 10
    pretty_print_issues(issues_list, num_1, num_2)


command_dict = {
    '/help': help_command,
    '/print': print_command,
    '/exit': exit_command,
    '/next': next_command

}


def run():
    """ Запускает пользовательский (консольный) интерфейс приложения.

    Чтобы "запуск" не был совсем тривиальным, реализуем перезапрос в случае
    ошибок.
    """

    success = False

    while not success:
        project_name = input('Enter project name in format owner/repo '
                             '(for example, "s0md3v/Photon"):')

        try:
            issues_list = make_issues_list(project_name)
        except ProjectNotFoundError:
            print(f'Project "{project_name}" not found, check your spelling.')
            continue
        except GithubError as err:
            print(f'Error communicating with Github: {err}')
            break

        success = True

    print(f'There are {len(issues_list)} issues in the "{project_name}" repository.')
    while True:
        user_command = input('Enter the command '
                            '(for more information about commands input "/help"): ')
        if len(user_command.lower().split()) > 1:
            user_command = user_command.lower().split()
            command = user_command[0]
            issue_number = int(user_command[1])
            #надо бы сделать исключение на номер не из диапазона и ValueError:
        else:
            command = user_command.lower()
            issue_number = None

        if command not in command_dict.keys():
            print(f'The command "{command}" not found. Try again.')
            continue
        else:
            command_dict[command](issues_list, issue_number)




if __name__ == "__main__":
    run()

