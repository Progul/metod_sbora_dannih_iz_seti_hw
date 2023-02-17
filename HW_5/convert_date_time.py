from datetime import datetime
from datetime import date
from datetime import timedelta


def convert_to_datetime(date_str: str):
        months = {'января': '01',
              'февраля': '02',
              'марта': '03',
              'апреля': '04',
              'мая': '05',
              'июня': '06',
              'июля': '07',
              'августа': '08',
              'сентября': '09',
              'октября': '10',
              'ноября': '11',
              'декабря': '12'}
    inp_date = date_str.split(', ')[0]
    inp_time = date_str.split(', ')[1]
    if 'Сегодня' in inp_date:
        res_date = date.today()
    elif 'Вчера' in inp_date:
        res_date = date.today() - timedelta(days=1)
    else:
        split_date = inp_date.split(' ')
        day = split_date[0]
        month = split_date[1]
        if len(split_date) == 3:
            year = split_date[2]
        else:
            year = date.today().year
        res_month = months.get(month)
        format_str = '%d-%m-%Y'
        res_date = datetime.strptime(f'{day}-{res_month}-{year}', format_str).date()
    res_time = datetime.strptime(inp_time, '%H:%M').time()
    res_date_time = datetime.combine(res_date, res_time)
    return res_date_time


def main():
    input_dates = ['Сегодня, 1:30',
                   'Вчера, 20:51',
                   '13 февраля, 08:05',
                   '15 февраля 2023, 10:24']
    for i in input_dates:
        convert_to_datetime(i)


if __name__ == '__main__':
    main()
