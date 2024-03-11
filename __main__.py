from cli import *
from github import make_issues_list, GithubError, ProjectNotFoundError


def main():
    run()
    ask_user()


if __name__ == "__main__":
    main()
