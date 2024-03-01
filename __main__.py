import get_issues


def main():
    project_name = input('input GitHub repo ID in format owner/repo (for example, "s0md3v/Photon"):')
    my_issues_lst = get_issues.get_issues_list(project_name)
    get_issues.print_issues_list(my_issues_lst)


if __name__ == "__main__":
    main()
