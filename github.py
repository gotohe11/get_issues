import requests


class GithubError(Exception):
    """Base class for API-related exceptions."""
    pass


class ProjectNotFoundError(GithubError):
    """Raised when the requested resource is not found."""
    pass


def make_issues_list(project_name):
    base_url = f'https://api.github.com/repos/{project_name}/issues'
    total_list = []
    counter = 1
    while True:
        temp_list = []
        add_url = f'{base_url}?page={counter}'
        try:
            response = requests.get(add_url)
            status_code = response.status_code
            if status_code == 404:
                raise ProjectNotFoundError
            # if status_code != 404 and status_code != 200:
            #     raise GithubError
        except ProjectNotFoundError:
            raise ProjectNotFoundError
        except Exception:
            raise GithubError('Something went wrong. Try again.')

        for item in response.json():
            if 'pull_request' not in item.keys():
                temp_list.append((item['title'], item['created_at'],
                                  item['updated_at'], item['comments']))
        if temp_list:
            total_list.extend(temp_list)
            counter += 1
        else:
            break

    return total_list


if __name__ == "__main__":
    project_name = "s0md3v/Photon1"
    l = make_issues_list(project_name)
    for i in range(len(l)):
        print(f'{i + 1}. {l[i]}', sep='\n')
