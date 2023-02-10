"""
Читаем данные из базы данных
"""
from pprint import pprint

import settings


def main(target_salary: int):
    # target_salary = 120000

    # вакансии с заработной платой больше введённой суммы (необходимо анализировать оба поля зарплаты):
    for job in settings.jobs.find(
            {'$or': [{'min_salary': {'$gt': target_salary}, 'max_salary': {'$gt': target_salary}},
                     {'min_salary': {'$gt': target_salary}, 'max_salary': None},
                     {'min_salary': None, 'max_salary': {'$gt': target_salary}}
                     ]}).sort('min_salary'):
        pprint(job)

    # попадает в зарплатную вилку
    # min_salary <= target_salary <= max_salary
    for job in settings.jobs.find(
            {'$or': [{'min_salary': {'$lte': target_salary}, 'max_salary': {'$gte': target_salary}},
                     {'min_salary': {'$lte': target_salary}, 'max_salary': None},
                     {'min_salary': None, 'max_salary': {'$gte': target_salary}}
                     ]}):
        pprint(job)


if __name__ == '__main__':
    input_target_salary = 120000
    main(input_target_salary)
