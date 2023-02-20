
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re


class Project1Pipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongo_base = client.job_openings

    def process_item(self, item, spider):
        item = self.process_salary(item)

        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

    def process_salary(self, item):
        item_1 = {'name': item['name'], 'url': item['url']}
        str_1 = (str(''.join(item['salary']))).replace('\xa0', '')
        if item['salary'][0][0] == 'о' and item['salary'][2] == ' до ':
            re_minimum_maximum = re.compile(r'\d+')
            minimum = re_minimum_maximum.findall(str_1)[0]
            maximum = re_minimum_maximum.findall(str_1)[1]
            currency = item['salary'][5]
            item_1['salary_min'] = int(minimum)
            item_1['salary_max'] = int(maximum)
            item_1['salary_cur'] = currency
        if item['salary'][0][0] == 'о' and item['salary'][2] == ' ':
            re_minimum_maximum = re.compile(r'\d+')
            minimum = re_minimum_maximum.findall(str_1)[0]
            currency = item['salary'][3]
            item_1['salary_min'] = int(minimum)
            item_1['salary_max'] = None
            item_1['salary_cur'] = currency
        if item['salary'][0][0] == 'д':
            re_minimum_maximum = re.compile(r'\d+')
            maximum = re_minimum_maximum.findall(str_1)[0]
            currency = item['salary'][3]
            item_1['salary_min'] = None
            item_1['salary_max'] = int(maximum)
            item_1['salary_cur'] = currency
        if str_1 == 'з/п не указана':
            item_1['salary_min'] = None
            item_1['salary_max'] = None
            item_1['salary_cur'] = None
        return item_1
