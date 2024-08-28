import pytest
import json
import os
from .. import database


PATH = '/tmp/test_data.json'


@pytest.fixture(scope='class')
def tmp_db(request):
    """ Заменяет директорию БД для класса TestDataBase,
    удаляет в конце (класса) файл БД.
    """
    request.cls.db = database.Database(PATH)
    yield
    os.remove(PATH)


@pytest.fixture(scope='function')
def clean_file():
    """Чистит временный файл БД при выполнении каждой ф-ии класса.
    """
    with open(PATH, 'w', encoding='utf-8') as file:
        data = {}
        json.dump(data, file, indent=2)



