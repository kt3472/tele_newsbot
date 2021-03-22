import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import telegram
from sklearn.feature_extraction.text import TfidfVectorizer
from konlpy.tag import Kkma, Twitter
from konlpy.utils import pprint
import time


key_words = "수소"


url1 = "https://search.naver.com/search.naver?&where=news&query="+key_words+"&sm=tab_pge&sort=1&photo=0&field=0&reporter_article=&pd=7&"
url2 = "ds=2021.03.19.16.01&de=2021.03.19.17.01"
url3 = "&docid=&nso=so:dd,p:1h,a:all&mynews=0&start="
url4 = "&refresh_start=0"

page_num = [1, 11,21,31,41,51,61,71,81,91]

tm =  time.time()
tm = time.localtime(tm)

year = str(tm.tm_year)
month = str(tm.tm_mon)
day = str(tm.tm_mday)
hour = str(tm.tm_hour)
hour_before = str(tm.tm_hour - 1)
minute = "01"


start_time = year + "." + month + "." + day + "." + hour_before + "." + minute
end_time = year + "." + month + "." + day + "." + hour + "." + minute


data = []

for i in page_num:
    
    url = url1 + "ds=" + start_time +"&de=" + end_time + url3 + str(i) + url4
    
    #print(url)
    #print("-------------------")
    
    html = requests.get(url)
    
    soup = bs(html.content, 'html.parser')
    
    li_tmp = soup.find_all('li', {'class':'bx'})
    
    #print(li_tmp)
    
    for i in li_tmp:
    
        try :

            tit = i.find('a',{'class':'news_tit'}).text
            #link = i.find('a',{'class':'info'})

            link = i.find_all('a',{'class':'info'})[1]['href']
            dsc = i.find('div',{'class':'news_dsc'}).text

            data.append([tit, dsc, link])

            #print(link)
            #print("--------------------------------")

        except:

            continue



df1 = pd.DataFrame(data, columns = ['title','text', 'links'])  

        
mydoclist = list(df1['text'])
kkma = Kkma()
doc_nouns_list = []
for doc in mydoclist:
    
    nouns = kkma.nouns(doc)
    doc_nouns = ''
    
    for noun in nouns :
        
        doc_nouns += noun + ' '
        
    
    doc_nouns_list.append(doc_nouns)


tfidf_vectorizer = TfidfVectorizer(min_df=1)
tfidf_matrix = tfidf_vectorizer.fit_transform(doc_nouns_list)
document_distances = (tfidf_matrix * tfidf_matrix.T)
id_result = pd.DataFrame(document_distances.toarray())


set_df = {}

for i in id_result.columns:
    
    temp_list = []
    
    for j in id_result.columns:
        
        #print(id_result[i][j])

        if id_result[i][j] > 0.1 :

            temp_list.append(j)

    
    
    set_df[i] = temp_list


result = {}

for key,value in set_df.items():
    
    #print(key)
    #print(value)
    
    value = [value[0]]
    
    if value not in result.values():
        result[key] = value


bot = telegram.Bot(token='토큰')
chat_id = "id"


for i in result.keys():
    
    send_message = df1['links'][i]

    bot.sendMessage(chat_id=chat_id, text=send_message)


