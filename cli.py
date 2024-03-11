from typing import Dict

import requests
from tabulate import tabulate
from github import make_issues_list, GithubError, ProjectNotFoundError


def pretty_print_issues(lst, num, project_name):
    """
    Prints a list of issues sorted by creation date (by default),
    in the form of a table.
    :param lst: list of
    :param project_name: repo ID
    :return: data table
    """
    print(f'List of {num} issues in the "{project_name}" repository:')
    columns = ['№', 'title', 'created at', 'updated at', 'comments']
    print(tabulate(lst[:num], headers=columns))


def run():
    """ Запускает пользовательский (консольный) интерфейс приложения.

    Чтобы "запуск" не был совсем тривиальным, реализуем перезапрос в случае
    ошибок.
    """

    success = False

    while not success:
        global project_name
        project_name = input('Enter project name in format owner/repo '
                             '(for example, "s0md3v/Photon"):')

        try:
            issues_list = make_issues_list(project_name)
        except ProjectNotFoundError:
            print(f'Project "{project_name}" not found, check your spelling.')
            continue
        except GithubError as err:
            print(f'Error communicating with Github: {err}')
            # Да, в `GithubError` мы не напихали ничего умного, когда его
            # выкидывали, поэтому тут будет напечатано просто GithubError,
            # но это чисто для иллюстрации.
            #
            # Допустим, при сетевых ошибках мы не хотим повторно стучаться,
            # а сразу выходим.
            break

        success = True

        global pretty_issues_list

        pretty_issues_list = []
        for i in range(len(issues_list)):
            pretty_issues_list.append((i + 1,
                               issues_list[i][0],
                               issues_list[i][1][0:10],
                               issues_list[i][2][0:10],
                               issues_list[i][3]))

        #pretty_print_issues(pretty_issues_list, project_name)


def help_command():
    print(
        'Available commands:\n'
        '/help - commands info;\n'
        '/exit - exit;\n'
        '/get_all - print whole list of issues\n'
        '/get(n) - get a list of {n} newest issues (but not more than 100 at once);\n'
        )


def get_all():
    pretty_print_issues(pretty_issues_list, len(pretty_issues_list), project_name)


def get(num):
    pretty_print_issues(pretty_issues_list, num, project_name)


command_dict = {
    '/help': help_command,
    '/get_all': get_all,
    '/get': get

}


def ask_user():
    """
    *Представим, что пока в мире не существует репозиториев типа
    microsoft/vscode или NixOS/nixpkgs (у которых 1к+ исусов),
    и поэтому мы все исусы к себе подгружаем и с этими данными
    работаем.
    Я потом переделаю с учетом больших репозиториев.

    Commands asker
    :return: commands doer func
    """
    print(f'There are {len(pretty_issues_list)} issues in the "{project_name}" repository.')
    while True:
        command = input('Enter the command '
                        '(for more information about commands input "/help"): ')

        if command.lower() == '/exit':
            break
        elif command.lower().startswith('/get'):
            issues_num = int(command[command.index('(') + 1: command.index(')')])
            print(issues_num)
            command_dict[command.lower()[:4]](issues_num)
        else:
            if command.lower() not in command_dict.keys():
                print(f'The command "{command}" not found. Try again.')
                continue
            else:
                command_dict[command.lower()]()



if __name__ == "__main__":
    run()
    ask_user()
