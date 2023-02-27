# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo import MongoClient, errors


class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.instagram

    def process_item(self, item, spider):
        collection = self.mongobase[item.get('username')]
        collection.insert_one(item)
        return item

        self.mongo_base = client.instagram

    def add_to_db(self, item, collection_name):
        collection = self.mongo_base[collection_name]
        collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)
        pass

    def process_item(self, item, spider):
        collection_name = spider.name
        user = {
            '_id': item['user_id'],
            'user_id': item['user_id'],
            'user_name': item['user_name'],
            'full_name': item['full_name'],
            'is_followed_by': item['is_followed_by'],
            'photo': item['photo'],
            'follows': item['follows']
        }

        self.add_to_db(user, collection_name)

        return item