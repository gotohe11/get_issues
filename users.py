from dataclasses import dataclass, field

from . import cli
from . import subscriptions


@dataclass
class User:
    name: str
    subsc_list: list = field(default_factory=list)


    def add_subsc(self, project_name):
        res = (obj.name for obj in self.subsc_list)
        if project_name in res:
            raise NameError(f'You have already subscribed to the "{project_name}" repository.')
        check_project = cli.get_command(project_name)  # проверяем все ли так с введенным проектом, есть ненужный принт
        subs_obj = subscriptions.Subscription(project_name)
        self.subsc_list.append(subs_obj)
        #print('добавилась подписка')


    def remove_subsc(self, project_name):
        res = (obj.name for obj in self.subsc_list)
        if project_name not in res:
            raise NameError(f'You are not subscribed to the "{project_name}" repository.')
        self.subsc_list = [item for item in self.subsc_list if item.name != project_name]
        #print('удалилась подписка')


    @classmethod
    def from_dict(cls, dct):
        name = dct['name']
        subsc_list = dct['subsc_list']
        return cls(name, subsc_list)



