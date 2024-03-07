import pandas as pd
from newsplease import NewsPlease


df = pd.read_excel('archiv/new_scraped_data.xlsx')


result = [NewsPlease.from_html(html) for html in df['html_content']]

df['title'] = [r.title for r in result]
df['text'] = [r.maintext for r in result]
