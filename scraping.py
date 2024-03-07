import requests
import pandas as pd
from bs4 import BeautifulSoup
import random
import time


user_agent = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
base_url = 'https://web.archive.org'


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
        print(target_url)
        output_lines = [x.split(" ")[1] for x in output_lines]
        return output_lines

    except subprocess.CalledProcessError as e:
        # Handle errors if the command fails
        print("Error:", e.output)
        return None



all_snapshots = find_available_snapshots('reuters.com/sustainability')

chosen_snapshots = all_snapshots[0:1]


url_list = []
html_list = []
for snapshot in chosen_snapshots:
    url = f'https://web.archive.org/web/{snapshot}/https://www.reuters.com/sustainability/'
    print("-" * 50)
    print(f'start to scrapy the snaptshot for {snapshot}')
    response = requests.get(url, headers=user_agent)
    all_links = BeautifulSoup(response.text, 'html.parser').find_all('a', href=True)
    all_links = [l['href'] for l in all_links]
    all_links = [l for l in all_links if l[0:5]=='/web/']
    all_links = [l for l in all_links if validate_url(l)]
    all_links = ['https://web.archive.org'+l for l in all_links]

    for link in all_links:
        print(link)
        respones = requests.get(link, headers=user_agent)
        url_list.append(respones.url)
        html_list.append(respones.text)
        

df = pd.DataFrame({'url': url_list, 'html_content': html_list})
df.to_excel('example.xlsx', index=False)
