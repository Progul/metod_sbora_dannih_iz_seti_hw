"""
Урок 2. Парсинг данных. HTML, DOM, XPath
Необходимо собрать информацию о вакансиях на вводимую должность
(используем input или через аргументы получаем должность) с сайтов HH(обязательно) и/или Superjob(по желанию).
Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
Получившийся список должен содержать в себе минимум:
1. Наименование вакансии.
2. Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
3. Ссылку на саму вакансию.
4. Сайт, откуда собрана вакансия. (можно прописать статично hh.ru или superjob.ru)

"""
from time import sleep
import json
# from pprint import pprint
import re

import requests
from bs4 import BeautifulSoup
import pandas as pd
from pymongo import errors

import settings


def insert_data_to_mongodb(input_dict: dict):
    
    try:
        settings.jobs.insert_one(input_dict)
    except errors.DuplicateKeyError:
        settings.duplicates.insert_one({'dup_id': input_dict['_id']})


def save_data_to_json(input_data: list, file_name: str = 'output_data'):
    
    file_name += '.json'
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(input_data, file, indent=2, ensure_ascii=False)


def hh_get_head(soup):
    
    h_header = soup.find('h1', {'data-qa': 'bloko-header-3'})
    # убираем неразрывный пробел между цифрами:
    h_header_encode = h_header.text.replace(u'\xa0', '')
    # 9025 вакансий «python»
    h_header_list = h_header_encode.split(' ')
    if h_header_list[0].isdigit():
        h_header_list[0] = int(h_header_list[0])
    # удаляем кавычки «»:
    h_header_list[-1] = h_header_list[-1].lstrip('«')
    h_header_list[-1] = h_header_list[-1].rstrip('»')
    return h_header_list


def hh_is_last_page(soup):    
    div_pager_find = soup.find('div', {'class': 'pager'})
    last_content_div_pager = div_pager_find.contents[-1]
    if last_content_div_pager.text != 'дальше':
        return True


def sj_is_last_page(soup):    
    a_pager_find = soup.find('a', {
        'class': ['f-test-button-dalshe', 'f-test-link-Dalshe'],
        'rel': 'next'
    })
    if not a_pager_find:
        return True


def get_request(url, referer_url, params, get_redirect_url=False):    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 '
                      'Safari/537.36',
        'Referer': referer_url,
        'Connection': 'keep-alive',
        'Vary': 'User-Agent'
    }
    sleep(3)
    session = requests.session()
    try:
        response = session.get(url, headers=headers, params=params, timeout=5)
        if get_redirect_url:
            return response.history[-1].url
        response_text = response.text
        # soup = BeautifulSoup(response_text, 'lxml')
        return BeautifulSoup(response_text, 'lxml')
    except requests.exceptions.ReadTimeout:
        print('The server did not send any data in the allotted amount of time.')
    # requests.exceptions.ReadTimeout
    # if get_redirect_url:
    #     return response.history[-1].url
    # response_text = response.text
    # # soup = BeautifulSoup(input_text, 'lxml')
    # return BeautifulSoup(response_text, 'lxml')


def hh_get_vacancy(soup):
    # div data-qa="vacancy-serp__results" id="a11y-main-content"
    div_container_vacancies = soup.find('div', {'id': 'a11y-main-content'})
    div_vacancies = div_container_vacancies.find_all('div', {'class': 'vacancy-serp-item__layout'})

    list_vacancies = []
    url_prefix = 'https://hh.ru'
    for vacancy in div_vacancies:
        vacancy_dict = {
            'vacancy_name': None,
            'vacancy_link': None,
            'min_salary': None,
            'max_salary': None,
            'currency': None,
            'employer': None,
            'employer_link': None,
            'vacancy_id': None
        }
        vacancy_a = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
        vacancy_dict['vacancy_name'] = vacancy_a.text
        pattern_hh = r'hh\.ru\/vacancy\/(\d+)'
        if not re.search(pattern_hh, vacancy_a.get('href')):
            url = vacancy_a.get('href')
            vacancy_dict['vacancy_link'] = get_request(url, url, {}, get_redirect_url=True).split('?')[0]
        else:
            vacancy_dict['vacancy_link'] = vacancy_a.get('href').split('?')[0]
        vacancy_dict['_id'] = re.findall(pattern_hh, vacancy_dict['vacancy_link'])[0]
        span_salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        vacancy_employer = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})
        if vacancy_employer:
            vacancy_dict['employer'] = vacancy_employer.text.replace(u'\xa0', ' ')
            vacancy_dict['employer_link'] = url_prefix + vacancy_employer.get('href').split('?')[0]
            vacancy_dict['source'] = url_prefix
            if span_salary:
                salary_text = span_salary.text
                salary_list = salary_text.split(' ')
                if salary_list[0] == 'от':
                    salary_list[1] = salary_list[1].replace('\u202f', '')  
                    vacancy_dict['min_salary'] = int(salary_list[1])
                    vacancy_dict['max_salary'] = None
                    vacancy_dict['currency'] = salary_list[2]
                elif salary_list[0] == 'до':
                    salary_list[1] = salary_list[1].replace('\u202f', '')  
                    vacancy_dict['min_salary'] = None
                    vacancy_dict['max_salary'] = int(salary_list[1])
                    vacancy_dict['currency'] = salary_list[2]
                elif salary_list[1] == '–':
                    salary_list[0] = salary_list[0].replace('\u202f', '')  
                    salary_list[2] = salary_list[2].replace('\u202f', '')  
                    vacancy_dict['min_salary'] = int(salary_list[0])
                    vacancy_dict['max_salary'] = int(salary_list[2])
                    vacancy_dict['currency'] = salary_list[3]
        insert_data_to_mongodb(vacancy_dict)
        list_vacancies.append(vacancy_dict)
    return list_vacancies


def sj_get_vacancy(soup):
    div_vacancies = soup.find('div', {'class': ['_19nio']})
    div_vacancies = div_vacancies.find_all('div', {'class': '_2J3hU ZsUty GSXRd MgbFi'})
    list_vacancies = []
    url_prefix = 'https://russia.superjob.ru'
    for vacancy in div_vacancies:
        vacancy = vacancy.parent
        vacancy_dict = {
            'vacancy_name': None,
            'vacancy_link': None,
            'min_salary': None,
            'max_salary': None,
            'currency': None,
            'employer': None,
            'employer_link': None
        }
        vacancy_a = vacancy.find_all('a', {'class': ['_1IHWd', '_2b9za', '_-6lxq', 'HyxLN']})
        vacancy_dict['vacancy_name'] = vacancy_a[0].text
        vacancy_dict['vacancy_link'] = url_prefix + vacancy_a[0].get('href')
        pattern_hh = r'superjob\.ru\/vakansii\/(.+)\.html$'
        vacancy_dict['_id'] = re.findall(pattern_hh, vacancy_dict['vacancy_link'])[0]
        span_salary = vacancy.find('span', {'class': ['f-test-text-company-item-salary']}).text
        vacancy_dict['employer'] = vacancy_a[-1].text
        vacancy_dict['employer_link'] = url_prefix + vacancy_a[-1].get('href')
        vacancy_dict['source'] = url_prefix
        pattern1 = r'^(\D{2})\s(\d+.\d+)\s(\w*..\w*$)'
        pattern2 = r'^(\d+.\d+)\s.\s(\d+.\d+)\s(\w*..\w*$)'
        pattern3 = r'^(\d+.\d+)\s(\w*..\w*$)'

        min_or_max_salary = re.search(pattern1, span_salary)
        from_min_to_max_salary = re.search(pattern2, span_salary)
        salary = re.search(pattern3, span_salary)

        if min_or_max_salary:
            num_find1 = re.findall(pattern1, span_salary)
            if num_find1[0][0] == 'от':
                vacancy_dict['min_salary'] = int(num_find1[0][1].replace('\xa0', ''))
                vacancy_dict['currency'] = num_find1[0][2].split('/')[0]
            elif num_find1[0][0] == 'до':
                vacancy_dict['max_salary'] = int(num_find1[0][1].replace('\xa0', ''))
                vacancy_dict['currency'] = num_find1[0][2].split('/')[0]
        if from_min_to_max_salary:
            num_find2 = re.findall(pattern2, span_salary)
            vacancy_dict['min_salary'] = int(num_find2[0][0].replace('\xa0', ''))
            vacancy_dict['max_salary'] = int(num_find2[0][1].replace('\xa0', ''))
            vacancy_dict['currency'] = num_find2[0][2].split('/')[0]
            # print('-' * 20)
        if salary:
            num_find3 = re.findall(pattern3, span_salary)
            vacancy_dict['min_salary'] = vacancy_dict['max_salary'] = int(num_find3[0][0].replace('\xa0', ''))
            vacancy_dict['currency'] = num_find3[0][1].split('/')[0]
        insert_data_to_mongodb(vacancy_dict)
        list_vacancies.append(vacancy_dict)
    return list_vacancies


def get_hh_ru(text):
    url = 'https://hh.ru/search/vacancy'
    referer_url = 'https://hh.ru/'
    search_field = ['name', 'description']
    last_page = False
    page = 0  
    all_hh_vacancies = []
    while not last_page:
        params = {
            'from': 'suggest_post',
            'items_on_page': 20,
            'text': text,
            'search_field': search_field,
            'page': page
        }
        soup = get_request(url, referer_url, params)
        if page == 0:
            print(hh_get_head(soup))
        last_page = hh_is_last_page(soup)

        progress(last_page, 'hh.ru') 
        page += 1
        all_hh_vacancies.extend(hh_get_vacancy(soup))
    return all_hh_vacancies


def get_sj_ru(text):
    url = 'https://russia.superjob.ru/vacancy/search/'
    referer_url = 'https://russia.superjob.ru/'

    last_page = False
    page = 1  
    all_sj_vacancies = []
    while not last_page:
        params = {
            'keywords': text,
            'page': page
        }
        soup = get_request(url, referer_url, params)
        last_page = sj_is_last_page(soup)

        progress(last_page, 'superjob') 

        page += 1
        all_sj_vacancies.extend(sj_get_vacancy(soup))
    return all_sj_vacancies


def progress(last_page, text='1'):
    print('|', end='')
    if last_page:
        print(f'\n{text}: Задание выполнено!')


def main(keyword):
    keyword = 'python'
    all_vacancies = []
    get_hh_ru(keyword)
    get_sj_ru(keyword)

if __name__ == '__main__':
    input_text = input('Введите ключевое слово для поиска вакансий: ')
    print(f'Будем искать вакансии по слову "{input_text}"')
    main(input_text)
