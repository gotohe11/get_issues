import requests


def get_issues_list(project_name):
    """Returns a list of open issues (not pull-request)
    of the required GitHub repository.

    Args:
        project_name: a string with repository ID
          (for example, "s0md3v/Photon")

    Returns:
        A list of all open repository issues.
        For example:
          ['Endho32', "Ain't getting any output", 'Errno 30']
    """

    def make_issues_list(url):
        issue_list = []
        response = requests.get(url)
        if response.status_code == 200:
            for item in response.json():
                if 'pull_request' not in item.keys():
                    issue_list.append(item['title'])
        return issue_list


    base_url = f'https://api.github.com/repos/{project_name}/issues'
    total_list = []
    counter = 1
    temp_list = True
    while temp_list:
        add_url = f'{base_url}?page={counter}'
        temp_list = make_issues_list(add_url)
        total_list.extend(temp_list)
        counter += 1
    return total_list


def print_issues_list(data):
    if data:
        for i in range(len(data)):
            print(f'{i+1}. {data[i]}', sep='\n')
    else:
        print("OOPS! Something went wrong. "
              "Let's try this again")


if __name__ == "__main__":
    project_name = input('input owner/repo (for example, "s0md3v/Photon"):')
    total_list = get_issues_list(project_name)
    print_issues_list(total_list)
