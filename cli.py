import sys
from tabulate import tabulate
from collections import namedtuple
from datetime import date

from . import errors
from . import github
from . import users
from . import subscriptions
from . import database

COLUMNS = ['N', 'title', 'created_at', 'updated_at', 'comments']
USER = None    # несет экземпляр класса юзер


def pretty_print_issues(res_list, num_start, num_finish=100):
    """
    Prints a list of issues sorted by creation date (by default),
    in the form of a table.
    :param num_start: required number of issues
    :param num_finish: required number of issues
    :return: data table
    """
    temp_lst = [(item[1:]) for item in res_list]
    print(tabulate(temp_lst[num_start:num_finish], headers=COLUMNS))


def help_command():
    print(
        'Available commands:\n'
        '/help - commands info;\n'
        '/exit - exit;\n'
        '/get <owner>/<repo> (for example, "/get s0md3v/Photon") - '
        'gets repo issues list and prints the amount of them;\n'
        '/print N - prints the N-th issue (if there is no N, prints 10 newest issues);\n'
        '/next - prints the next 10 issues or the remainder;\n'
        '/sub <owner>/<repo> - to subscribe to the project;\n'
        '/unsub <owner>/<repo> - to unsubscribe from the project;\n'
        '/update - prints issues in all projects you subscribe since the last visit;\n'
        '/update YYYY-MM-DD - prints issues in all projects you subscribe since the date (ISO-format)'
        )



def _get_issues_list_from_github(project_name):
    issues_list = namedtuple('issue', ['project_name'] + COLUMNS)

    success = False
    while not success:
        try:
            res_list = [issues_list(project_name, *item) for item in github.make_issues_list(project_name)]
        except github.ProjectNotFoundError:
            print(f'Project "{project_name}" not found, check your spelling.')
            res_list = []
            break
        except github.GithubError as err:
            print(f'Error communicating with Github: {err}')
            break
        success = True
        return res_list



def get_command(project_name):
    global USER

    if not USER:
        USER = users.User('_no_name')

    issues_list = _get_issues_list_from_github(project_name)
    if issues_list:
        print(f'There are {len(issues_list)} issues in the "{project_name}" repository.'
              ' Use /sub, /next or /print commands')

        USER.last_project = subscriptions.Subscription(project_name, issues_list, 0)


def exit_command():
    sys.exit()


def print_command(issue_number=None):
    global USER
    if not USER.last_project:
        raise errors.IncorrectOder('Firstly, try "/get <owner>/<repo>" command')

    issues_list = USER.last_project.issues_list

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
        if skip >= len(issues_list) or skip < 0:
            raise errors.CommandArgsError('Number out of issues list range.')


    pretty_print_issues(issues_list, skip, skip+limit)   # печатаем
    last_issue_num = skip + limit
    USER.last_project.last_issue_num = last_issue_num   # замена последнего просмотренного исуса текущего проекта

    # замена последнего просмотренного исуса проекта если он в подписках у пользователя
    project_name = issues_list[0].project_name
    res = [obj.name for obj in USER.subsc_list]
    if project_name in res:    # если юзер подписан на репо, то меняем последний просмотренный исус
        for i in range(len(USER.subsc_list)):
            if USER.subsc_list[i].name == project_name:
                USER.subsc_list[i].last_issue_num = last_issue_num
                database.Database.save_sub(USER)     # записываем в файлик

    return issues_list[skip:skip+limit]


def next_command():
    global USER
    if not USER.last_project:
        raise errors.IncorrectOder('Firstly, try "/get <owner>/<repo>" command')

    issues_list = USER.last_project.issues_list
    num_1 = USER.last_project.last_issue_num
    num_2 = num_1 + 10
    if num_1 < 0 or num_1 >= len(issues_list):
        raise errors.CommandArgsError('You have seen the whole issues list.')
    else:
        pretty_print_issues(issues_list, num_1, num_2)
        # замена последнего просмотренного исуса текущего проекта
        USER.last_project.last_issue_num = num_2 if num_2 <= len(issues_list) else len(issues_list)

        # замена последнего просмотренного исуса проекта если он в подписках у пользователя
        project_name = issues_list[0].project_name
        res = [obj.name for obj in USER.subsc_list]
        if project_name in res:  # если юзер подписан на репо, то меняем последний просмотренный исус
            for i in range(len(USER.subsc_list)):
                if USER.subsc_list[i].name == project_name:
                    USER.subsc_list[i].last_issue_num = num_2 if num_2 <= len(issues_list) \
                        else len(issues_list)
                    database.Database.save_sub(USER)  # записываем в файлик

        return issues_list[num_1:num_2]


def login_command(user_name=None):   # имя получилось нечувств к регистру
    if not user_name:
        raise errors.CommandArgsError('You should text your login-name first')
    global USER
    USER = database.Database.load_or_create_user(user_name)
    print(f'Hello, {USER.name}!')



def sub_command(project_name=None):
    global USER
    if USER.name == '_no_name':
        raise errors.IncorrectOder('To subscribe a project, you first need to log in. ' 
                                   'Try </login> command')
    if not project_name:
        raise errors.CommandArgsError('You forgot to text a project name')

    if USER.last_project and project_name in USER.last_project.name:
        project_obj = USER.last_project
    else:
        try:    # создаем подписку
            issues_list = _get_issues_list_from_github(project_name)    # заново грузим исусы
            if not issues_list:
                raise github.GithubError
            project_obj = subscriptions.Subscription(project_name, issues_list, 0)
        except github.GithubError:
            return
    try:
        USER.add_subsc(project_obj)
        database.Database.save_sub(USER)  # просто переписываем весь список подписок юзера заново
        print(f'{USER.name}, you subscribed to "{project_name}" repository.')
    except NameError as er:
        print(er)



def unsub_command(project_name=None):
    global USER
    if USER.name == '_no_name':
        raise errors.IncorrectOder('To unsubscribe from a project, you first need to log in. '
                                   'Try </login> command')
    if not project_name:
        raise errors.CommandArgsError('You forgot to text a project name')

    try:
        USER.remove_subsc(project_name)    # удаляем ненужную подписку из списка подписок юзера
        database.Database.save_sub(USER)   # просто переписываем весь список подписок Юзера заново
        print(f'{USER.name}, you unsubscribed from the "{project_name}" repository.')
    except NameError as er:
        print(er)



def update_command(since_date=None):
    """
    Prints new issues since {since_date} or since last time visit (last_issue_num)
    """
    global USER
    if USER.name == '_no_name':
        raise errors.IncorrectOder('To update your projects, you first need to log in. ' 
                                   'Try </login> command')
    if not USER.subsc_list:
        print('You do not have any subscriptions yet')

    elif USER.subsc_list and not since_date:    # догружаем у каждой подписки все исусы, которые еще не видел юзер
        for subscription in USER.subsc_list:
            temp_list_issues = _get_issues_list_from_github(subscription.name)  # заново грузим весь репозиторий
            if not temp_list_issues:
                return
            if subscription.last_issue_num < len(temp_list_issues):    # сравниваем с последним просмотренным исусом
                print(subscription.name + ':')
                pretty_print_issues(temp_list_issues, subscription.last_issue_num, len(temp_list_issues))
                subscription.issues_list = temp_list_issues
                subscription.last_issue_num = len(temp_list_issues)
            else:
                print(f'There is nothing to update in "{subscription.name}" repository')
        database.Database.save_sub(USER)  # перезаписываем все подписки у юзера разом

    elif USER.subsc_list and since_date:   # догружаем у каждой подписки все исусы позже указанной даты
        for subscription in USER.subsc_list:
            temp_list_issues = _get_issues_list_from_github(subscription.name)  # заново грузим весь репозиторий
            if not temp_list_issues:
                return
            numbers_new_issues_list = []    # собираем все номера непросмотренных исусов подписки для печати
            for issue in temp_list_issues:
                if date.fromisoformat(issue.created_at) >= date.fromisoformat(since_date):
                    numbers_new_issues_list.append(issue.N)
                    subscription.last_issue_num = issue.N
            if numbers_new_issues_list:
                print(subscription.name + ':')
                pretty_print_issues(temp_list_issues, numbers_new_issues_list[0] - 1, numbers_new_issues_list[-1])
            else:
                print(f'There is nothing to update in "{subscription.name}" repository')
        database.Database.save_sub(USER)  # перезаписываем все подписки у юзера разом


command_dict = {
    '/help': help_command,
    '/get': get_command,
    '/exit': exit_command,
    '/print': print_command,
    '/next': next_command,
    '/login': login_command,
    '/sub': sub_command,
    '/unsub': unsub_command,
    '/update': update_command
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
    except TypeError as er:
        #print(er)
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
