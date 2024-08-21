from dataclasses import dataclass, field
from . import subscriptions


@dataclass
class User:
    name: str
    subs: dict = field(default_factory=dict)
    last_project: subscriptions.Subscription = field(default=None)    # последний просмотренный проект без подписки


    def add_subsc(self, project_obj):
        if project_obj.name in self.subs:
            raise NameError(f'You have already subscribed to the "{project_obj.name}" repository.')
        dct = {project_obj.name: project_obj}
        self.subs.update(dct)


    def remove_subsc(self, project_name):
        if project_name not in self.subs:
            raise NameError(f'You are not subscribed to the "{project_name}" repository.')
        del self.subs[project_name]


    @classmethod
    def from_dict(cls, dct):
        name = dct['name']
        subs = {
            k: subscriptions.Subscription(v['name'],
                                          subscriptions.Subscription.make_named_tuples(v['issues_list']),
                                          v['last_issue_num'])
            for k, v in dct['subs'].items()
        }
        return cls(name, subs)    # без посл просм проекта

