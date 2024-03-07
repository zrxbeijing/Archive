import argparse
from pkg_resources import get_distribution

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from wayback_machine_scraper.mirror_spider import MirrorSpider

from argparse import Namespace

args_dic = {'domains': ['news.ycombinator.com'],
            'allow': 'id=13857086$',
            'output': 'new_website',
            'deny': (),
            'unix': False,
            'verbose': False,
            'concurrency': 10.0,
            'from': '20200101',
            'to': '20231001'}

args = Namespace(**args_dic)

config = {
    'domains': args.domains,
    'directory': args.output,
    'allow': args.allow,
    'deny': args.deny,
    'unix': args.unix,
}

settings = Settings({
    'USER_AGENT': (
        'Wayback Machine Scraper/{0} '
        '(+https://github.com/sangaline/scrapy-wayback-machine)'
    ).format(get_distribution('wayback-machine-scraper').version),
    'LOG_LEVEL': 'DEBUG' if args.verbose else 'INFO',
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy_wayback_machine.WaybackMachineMiddleware': 5,
    },
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_DEBUG': args.verbose,
    'AUTOTHROTTLE_START_DELAY': 1,
    'AUTOTHROTTLE_TARGET_CONCURRENCY': args.concurrency,
    'WAYBACK_MACHINE_TIME_RANGE': (getattr(args, 'from'), args.to),
})

# start the crawler
process = CrawlerProcess(settings)
process.crawl(MirrorSpider, **config)
process.start()


