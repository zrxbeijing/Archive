import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from archiv.items import ArchivScraperItem
import pandas as pd
from bs4 import BeautifulSoup
from newsplease import NewsPlease
import os


def validate_url(url):
    # check detailed url pattern
    check = False
    timestamp_str = url.split('/')[2]
    rest_url = url.split('//')[-1]
    if len(timestamp_str)==14 and timestamp_str.isdigit() and len(rest_url.split('/'))==5 and "www.reuters.com" in rest_url:
        check = True

    return check


def find_available_snapshots(target_url):
    import subprocess
    # Define the curl command as a list of strings
    curl_command = ['curl', '-X', 'GET', 'http://web.archive.org/cdx/search/cdx?url='+target_url]
    try:
        completed_process = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        # Get the standard output and standard error
        output = completed_process.stdout
        output_lines = output.splitlines()
        output_lines = [x.split(" ")[1] for x in output_lines]
        return output_lines

    except subprocess.CalledProcessError as e:
        # Handle errors if the command fails
        print("Error:", e.output)
        return None


class ArchivSpider(CrawlSpider):
    name = 'archiv'

    def __init__(self, *args, **kwargs):
        super(ArchivSpider, self).__init__(*args, **kwargs)
        available_snapshots = find_available_snapshots('reuters.com/sustainability')[-50:]
        self.start_urls = [f'https://web.archive.org/web/{snapshot}/https://www.reuters.com/sustainability/' for snapshot in available_snapshots]
        self.items = []

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        all_links = BeautifulSoup(response.text, 'html.parser').find_all('a', href=True)
        all_links = [l['href'] for l in all_links]
        all_links = [l for l in all_links if l[0:5]=='/web/']
        all_links = [l for l in all_links if validate_url(l)]
        all_links = [l.split('//')[1] for l in all_links]

        # find new links
        new_links = []
        for link in all_links:
            snapshots = find_available_snapshots(link)
            if len(snapshots)>0:
                # find the earliest snapshot
                new_link = 'https://web.archive.org/web/'+snapshots[0]+'id_'+'/https://'+link
                new_links.append(new_link)

        for link in new_links:
            yield scrapy.Request(link, callback=self.parse_links)


    def parse_links(self, response):
        item = ArchivScraperItem()
        result = NewsPlease.from_html(response.text)
        item['url'] = response.url
        item['title'] = result.title
        item['authors'] = result.authors
        item['date_publish'] = result.date_publish
        item['text'] = result.maintext

        # save a copy locally
        copy = response.url + '\n' + result.title + '\n' + str(result.authors) + '\n' + result.date_publish.strftime("%Y-%M-%d-%H:%M:%S") + '\n' + result.maintext 
        key_url = response.url.split('/')[-2]
        file_name = result.date_publish.strftime("%Y-%m-%d %H-%M-%S") + '-' + key_url + '.txt'


        if not os.path.exists(file_name):
            with open(file_name, 'w') as f:
                f.write(copy)
        
        self.items.append(item)


    def closed(self, reason):
        if self.items:
            df = pd.DataFrame([dict(item) for item in self.items])
            df.to_excel('new_scraped_data.xlsx', index=False)
