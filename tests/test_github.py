import responses
import pytest

from ..github import *


@responses.activate
def test_make_issues_list_404Error():
    valid_json_answer = [{
  "message": "Not Found",
  "documentation_url": "https://docs.github.com/rest/issues/issues#list-repository-issues"
}]

    responses.add(method=responses.GET, url='https://api.github.com/repos/shobrook/rebound1/issues?page=1',
                  json=valid_json_answer, status=404)
    with pytest.raises(ProjectNotFoundError):
        assert make_issues_list('shobrook/rebound1')


@responses.activate
def test_make_issues_list_GithubError():
    valid_json_answer = [{
      "message": "Not Found",
      "documentation_url": "https://docs.github.com/rest/issues/issues#list-repository-issues"
    }]

    responses.add(method=responses.GET, url='https://api.github.com/repos/shobrook/rebound1/issues?page=1',
                  json=valid_json_answer, status=500)
    with pytest.raises(GithubError):
        assert make_issues_list('shobrook/rebound')



# @responses.activate
# def test_make_issues_list():
#     valid_json_answer = [{
#     "url": "https://api.github.com/repos/shobrook/rebound/issues/90",
#     "repository_url": "https://api.github.com/repos/shobrook/rebound",
#     "html_url": "https://github.com/shobrook/rebound/issues/90",
#     "id": 877780283,
#     "node_id": "MDU6SXNzdWU4Nzc3ODAyODM=",
#     "number": 90,
#     "title": "LICENSE file missing from root directory",
#     "state": "open",
#     "locked": 'false',
#     "assignee": 'null',
#     "milestone": 'null',
#     "comments": 0,
#     "created_at": "2021-05-06T17:36:46Z",
#     "updated_at": "2021-05-06T17:36:46Z",
#     "closed_at": 'null',
#     "author_association": "NONE",
#     "active_lock_reason": 'null',
#     "body": "I see this is MIT licensed. Adding a LICENSE file to the root directory would make this very obvious for people new to the project and show up in the `About` header on the first page view of the project.\r\n\r\nWould you like me to make a PR to move the file?\r\n\r\n`mv docs/LICENSE LICENSE`",
#     "performed_via_github_app": 'null',
#     "state_reason": 'null'
#     }]
#
#     responses.add(method=responses.GET, url='https://api.github.com/repos/shobrook/rebound/issues?page=1',
#                   json=valid_json_answer, status=200)
#     issues_list = make_issues_list('shobrook/rebound')
#     assert issues_list == [(1, valid_json_answer['title'], valid_json_answer['created_at'][0:10],
#                                   valid_json_answer['updated_at'][0:10], valid_json_answer['comments'])]
#    c=1
#[(1, 'LICENSE file missing from root directory', '2021-05-06', '2021-05-06', 0)]
