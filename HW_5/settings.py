from pymongo import MongoClient


HOST = '192.168.2.230'  # IP-адрес
PORT = 27017  # порт

# для подключения к MongoDB
# создаем объект класса MongoClient
client = MongoClient(HOST, PORT)
# указатель на базу данных:
db = client['letters_db']
# коллекции:
letters = db['letters']  # письма
duplicates = db['duplicates']  # дубликаты
