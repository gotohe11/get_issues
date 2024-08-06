from dataclasses import dataclass, field


@dataclass
class Subscription:
    name: str
    last_issue_num: int = field(default=0)


    @classmethod
    def from_dict(cls, dct):
        name = dct['name']
        last_issue_num = dct['last_issue_num']
        return cls(name, last_issue_num)


