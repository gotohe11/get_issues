import get_issues


project_name = input('input GitHub repo ID in format owner/repo (for example, "s0md3v/Photon"):')
my_issues_lst = get_issues.get_issue_list(project_name)
get_issues.print_issue_list(my_issues_lst)
