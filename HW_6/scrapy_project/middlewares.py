from scrapy import signals

from itemadapter import is_item, ItemAdapter


class Project1SpiderMiddleware:
    

    @classmethod
    def from_crawler(cls, crawler):
        # Этот метод используется Scrapy для создания пауков.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Вызывается для каждого ответа, который проходит через паука
	# промежуточное программное обеспечение и в spider.

	# Должен возвращать None или вызывать исключение.
        return None

    def process_spider_output(self, response, result, spider):
       	# Вызывается с результатами, возвращенными от Spider

	# Должен возвращать итерацию запроса или объектов item.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Вызывается, когда метод spider или process_spider_input()
	# (из другого промежуточного программного обеспечения spider) вызывает исключение.
	
    def process_start_requests(self, start_requests, spider):
        # Вызывается с помощью запросов запуска spider и работает
	# аналогично методу process_spider_output(), за исключением
	# что с ним не связан ответ.
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class Project1DownloaderMiddleware:
    	# Вызывается, когда метод spider или process_spider_input()
	# (из другого промежуточного программного обеспечения spider) вызывает исключение.

	# Должен возвращать либо None, либо итерацию объектов Request или itemпроходить


    @classmethod
    def from_crawler(cls, crawler):
	# Этот метод используется Scrapy для создания ваших пауков.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Вызывается для каждого запроса, проходящего через загрузчик
        # промежуточное программное обеспечение.

        return None

    def process_response(self, request, response, spider):
        # Вызывается с ответом, возвращенным от загрузчика.

       
        return response

    def process_exception(self, request, exception, spider):
        # Вызывается, когда обработчик загрузки или process_request()
        # (из другого промежуточного программного обеспечения загрузчика) вызывает исключение.

        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
