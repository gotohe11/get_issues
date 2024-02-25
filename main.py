import get_issues


project_name = input('input owner/repo (for example, "s0md3v/Photon"):')
my_issues_lst = get_issues.print_issues(project_name)
