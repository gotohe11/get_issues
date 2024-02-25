import requests

def print_issues(project_name):
    """A function that prints a list of open issues (not pull-request)
    of the required GitHub repository.

    Args:
        project_name: a string with repository ID
          (for example, "s0md3v/Photon")

    Returns:
        A numbered list of all open repository issues.
        For example:
          1. Endho32
          2. Ain't getting any output
          3. Errno 30
    """
    base_url=f'https://api.github.com/repos/{project_name}/issues'
    response = requests.get(base_url)
    #print(response.status_code)

    def make_issues_list(url):
        response = requests.get(url)
        issue_list = []
        for item in response.json():
            if not 'pull_request' in item.keys():
                issue_list.append(item['title'])
        return issue_list

    #print('List issues in a repository '
          #'(only open issues will be listed):')

    total_list = []
    if response.status_code != 200:
        print("ooops! let's try one more time")
    if response.status_code == 200 and not 'link' in response.headers:
        lst = make_issues_list(base_url)
        total_list.extend(lst)
    if response.status_code == 200 and 'link' in response.headers:
        counter = 1
        temp_list = True
        while temp_list:
            add_url = f'{base_url}?page={counter}'
            temp_list = make_issues_list(add_url)
            total_list.extend(temp_list)
            counter += 1

    for i in range(len(total_list)):
        print(f'{i+1}. {total_list[i]}', sep='\n')
    #return (total_list)

if __name__ == "__main__":
    project_name = input('input owner/repo (for example, "s0md3v/Photon"):')
    print_issues(project_name)