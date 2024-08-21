from dataclasses import dataclass, field
from collections import namedtuple


COLUMNS = ['N', 'title', 'created_at', 'updated_at', 'comments']

@dataclass
class Subscription:
    name: str
    issues_list: list = field(default_factory=list)    # весь список исусов проекта
    last_issue_num: int = field(default=0, compare=False)  # последний просмотренный исус у подписки


    @classmethod
    def from_dict(cls, dct):
        name = dct['name']
        issues_list = cls.make_named_tuples(dct['issues_list'])
        last_issue_num = dct['last_issue_num']
        return cls(name, issues_list, last_issue_num)


    @staticmethod
    def make_named_tuples(lst, project_name=None):
        turn_to_namedtuple = namedtuple('issue', ['project_name'] + COLUMNS)
        if not project_name:
            issues_list = [turn_to_namedtuple(*item) for item in lst]   # в считанных списках уже есть имя репо
        else:
            issues_list = [turn_to_namedtuple(project_name, *item) for item in lst]
        return issues_list

