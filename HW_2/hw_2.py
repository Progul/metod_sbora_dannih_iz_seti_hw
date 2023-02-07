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

По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
Структура должна быть одинаковая для вакансий с обоих сайтов.
Общий результат можно вывести с помощью dataFrame через pandas.
Сохраните в json либо csv.

"""
import json
from pprint import pprint
import re

import requests
from bs4 import BeautifulSoup
import pandas as pd


def save_data_to_json(input_data: list, file_name: str = 'output_data'):
    """
    Функция сохранения полученных данных в файл json.
    :param input_data:
    :param file_name:
    :return:
    """
    file_name += '.json'
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(input_data, file, indent=2, ensure_ascii=False)


def hh_get_head(soup):
    """
    Получение данных из заголовка страницы вида: "4 430 вакансий «python»"
    :param soup:
    :return:
    """
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
    """
    Проверка последней страницы выдачи hh.ru
    :param soup:
    :return:
    """
    div_pager_find = soup.find('div', {'class': 'pager'})
    last_content_div_pager = div_pager_find.contents[-1]
    if last_content_div_pager.text != 'дальше':
        return True


def sj_is_last_page(soup):
    """
    Проверка последней страницы выдачи superjob.ru
    :param soup:
    :return:
    """
    a_pager_find = soup.find('a', {
        'class': ['f-test-button-dalshe', 'f-test-link-Dalshe'],
        'rel': 'next'
    })
    if not a_pager_find:
        return True


def hh_get_vacancy(soup):
    """
    Получение данных вакансий hh.ru
    :param soup:
    :return:
    """
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
            'employer_link': None
        }
        # получение наименования вакансии:
        vacancy_a = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
        # print(vacancy_a.text)
        vacancy_dict['vacancy_name'] = vacancy_a.text
        # получение ссылки на вакансию:
        vacancy_dict['vacancy_link'] = vacancy_a.get('href').split('?')[0]
        # получение зар.платы:
        span_salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})

        # <a class="bloko-link bloko-link_kind-tertiary" data-qa="vacancy-serp__vacancy-employer"
        vacancy_employer = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})
        vacancy_dict['employer'] = vacancy_employer.text.replace(u'\xa0', ' ')
        vacancy_dict['employer_link'] = url_prefix + vacancy_employer.get('href').split('?')[0]
        vacancy_dict['source'] = url_prefix

        if span_salary:
            # print(span_salary.text)
            salary_text = span_salary.text
            # print(salary_text)
            salary_list = salary_text.split(' ')
            # print(salary_list)
            if salary_list[0] == 'от':
                salary_list[1] = salary_list[1].replace('\u202f', '')  # text.replace(u'\xa0', '')
                vacancy_dict['min_salary'] = int(salary_list[1])
                vacancy_dict['max_salary'] = None
                vacancy_dict['currency'] = salary_list[2]
            elif salary_list[0] == 'до':
                salary_list[1] = salary_list[1].replace('\u202f', '')  # text.replace(u'\xa0', '')
                vacancy_dict['min_salary'] = None
                vacancy_dict['max_salary'] = int(salary_list[1])
                vacancy_dict['currency'] = salary_list[2]
            elif salary_list[1] == '–':
                salary_list[0] = salary_list[0].replace('\u202f', '')  # text.replace(u'\xa0', '')
                salary_list[2] = salary_list[2].replace('\u202f', '')  # text.replace(u'\xa0', '')
                vacancy_dict['min_salary'] = int(salary_list[0])
                vacancy_dict['max_salary'] = int(salary_list[2])
                vacancy_dict['currency'] = salary_list[3]
        # print(vacancy_dict)
        list_vacancies.append(vacancy_dict)
    return list_vacancies


def get_request(url, referer_url, params):
    """
    Создание подключения и получение данных
    :param url:
    :param referer_url:
    :param params:
    :return:
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 '
                      'Safari/537.36',
        'Referer': referer_url,
        'Connection': 'keep-alive',
        'Vary': 'User-Agent'
    }
    session = requests.session()
    response = session.get(url, headers=headers, params=params, timeout=5)
    input_text = response.text
    # soup = BeautifulSoup(input_text, 'lxml')
    return BeautifulSoup(input_text, 'lxml')


def sj_get_vacancy(soup):
    """
    Получение данных вакансий superjob.ru
    :param soup:
    :return:
    """
    # _19nio
    div_vacancies = soup.find('div', {'class': ['_19nio']})

    # document.getElementsByClassName('_37mRb z4PWH _2Rwtu');  span
    div_vacancies = div_vacancies.find_all('div', {'class': '_2J3hU ZsUty GSXRd MgbFi'})
    # print(len(div_vacancies))

    # - зар.плата
    list_vacancies = []
    url_prefix = 'https://russia.superjob.ru'
    # count = 0
    for vacancy in div_vacancies:
        vacancy = vacancy.parent
        # print('-------------------')
        vacancy_dict = {
            'vacancy_name': None,
            'vacancy_link': None,
            'min_salary': None,
            'max_salary': None,
            'currency': None,
            'employer': None,
            'employer_link': None
        }

        # получение наименования вакансии:
        vacancy_a = vacancy.find_all('a', {'class': ['_1IHWd', '_2b9za', '_-6lxq', 'HyxLN']})
        vacancy_dict['vacancy_name'] = vacancy_a[0].text
        # if vacancy_a[0].text:
        #     count += 1
        # получение ссылки на вакансию:
        vacancy_dict['vacancy_link'] = url_prefix + vacancy_a[0].get('href')

        # получение зар.платы:
        span_salary = vacancy.find('span', {'class': ['f-test-text-company-item-salary']}).text

        # Название компании
        vacancy_dict['employer'] = vacancy_a[-1].text
        # ссылка на профиль компании
        vacancy_dict['employer_link'] = url_prefix + vacancy_a[-1].get('href')
        # url_prefix + vacancy_employer.get('href').split('?')[0]
        vacancy_dict['source'] = url_prefix

        # vacancy_dict['employer_link'] = url_prefix + vacancy_employer.get('href').split('?')[0]
        #         vacancy_dict['source'] = url_prefix

        # от N руб./месяц | до N руб./месяц
        pattern1 = r'^(\D{2})\s(\d+.\d+)\s(\w*..\w*$)'
        # N - M руб./месяц
        pattern2 = r'^(\d+.\d+)\s.\s(\d+.\d+)\s(\w*..\w*$)'
        # N руб./месяц
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
        list_vacancies.append(vacancy_dict)
    # print(count)
    return list_vacancies


def get_hh_ru(text):
    """
    Создание списка вакансий с сайта hh.ru
    :param text:
    :return:
    """
    # https://hh.ru/search/vacancy?area=113&search_field=name&search_field=description&text=python&from=suggest_post
    # area=113 - регион Россия
    # search_field=name - поиск В названии вакансии
    # search_field=description - поиск В описании вакансии
    # text=python - текст поиска
    # salary=95000&only_with_salary=true - от 95 000 руб. и Указан доход
    # Язык поисковых запросов - https://hh.ru/article/1175
    # 6 вакансий «NAME:(python OR java) and COMPANY_NAME:Headhunter»
    # https://hh.ru/search/vacancy?text=NAME%3A%28python+OR+java%29+and+COMPANY_NAME%3AHeadhunter

    url = 'https://hh.ru/search/vacancy'
    referer_url = 'https://hh.ru/'

    # ключевое слово - что ищем:
    # text = 'python'

    # где ищем:
    # name - в названии вакансии
    # description - в описании вакансии
    search_field = ['name', 'description']
    last_page = False
    page = 0  # начинается с "page=0"
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

        # --------------------------------------------- hh_get_head
        if page == 0:
            print(hh_get_head(soup))
        # --------------------------------------------- hh_get_head

        # last page
        last_page = hh_is_last_page(soup)

        progress(last_page, 'hh.ru')  # процесс идёт

        # print(page)
        page += 1
        # --------------------------------------------- hh_get_vacancy
        all_hh_vacancies.extend(hh_get_vacancy(soup))
        # --------------------------------------------- hh_get_vacancy
    return all_hh_vacancies


def get_sj_ru(text):
    """
    Создание списка вакансий с сайта superjob.ru
    :param text:
    :return:
    """
    url = 'https://russia.superjob.ru/vacancy/search/'
    referer_url = 'https://russia.superjob.ru/'

    # ключевое слово - что ищем:
    # text = 'python'

    last_page = False
    page = 1  # начинается с "page=1"
    all_sj_vacancies = []
    while not last_page:
        params = {
            'keywords': text,
            'page': page
        }
        soup = get_request(url, referer_url, params)

        # last page
        last_page = sj_is_last_page(soup)

        progress(last_page, 'superjob')  # процесс идёт

        page += 1
        # # --------------------------------------------- sj_get_vacancy
        all_sj_vacancies.extend(sj_get_vacancy(soup))
        # # --------------------------------------------- sj_get_vacancy
    return all_sj_vacancies


def progress(last_page, text='1'):
    """
    Функиия для отображения процесса работы скрипта
    :param text:
    :param last_page:
    :return:
    """
    print('|', end='')
    if last_page:
        print(f'\n{text}: Задание выполнено!')


def main(keyword):
    # ключевое слово - что ищем:
    keyword = 'python'
    all_vacancies = []
    all_vacancies.extend(get_hh_ru(keyword))
    all_vacancies.extend(get_sj_ru(keyword))
    save_data_to_json(all_vacancies, 'all_vacancies')
    df = pd.DataFrame(all_vacancies)
    df.to_excel('all_vacancies.xlsx')


if __name__ == '__main__':
    # ключевое слово - что ищем:
    input_text = input('Введите ключевое слово для поиска вакансий: ')
    print(f'Будем искать вакансии по слову "{input_text}"')
    main(input_text)

#
