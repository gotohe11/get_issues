from dataclasses import dataclass, field


@dataclass
class Subscription:
    name: str
    issues_list: list = field(default_factory=list)    # весь список исусов проекта
    last_issue_num: int = field(default=0, compare=False)  # последний просмотренный исус у подписки


    @classmethod
    def from_dict(cls, dct):
        name = dct['name']
        issues_list = dct['issues_list']
        last_issue_num = dct['last_issue_num']
        return cls(name, issues_list, last_issue_num)


