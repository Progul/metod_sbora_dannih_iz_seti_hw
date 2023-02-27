from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from instaparser.spiders.instagram import InstaSpider
from instaparser.spiders.instagram import InstagramSpider
from pymongo import MongoClient
from pprint import pprint
from instaparser import settings

if __name__ == '__main__':
    configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings)

    runner.crawl(InstaSpider)

    reactor.run()

client = MongoClient('localhost', 27017)
mongo_base = client.instagram
collection = mongo_base['instagram']

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider)
    process.start()

for item in collection.find({}):
    pprint(item)

print(f'Всего записей: {collection.count_documents({})}')
