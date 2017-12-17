#!/usr/bin/env python3
# coding: utf-8
import time,json,requests,os
from bs4 import BeautifulSoup
import pymongo

#用時間戳記來比對確保爬蟲資料不重複儲存
#將新的新聞存入MongoDB

startPage =1
endPage = 2 #搜尋MLB約有1284多頁
def get_news_in_page():
    for page in range(startPage,endPage+1):       
        news_url="http://www.nownews.com/search/MLB/{}".format(page)
        get_news_list(news_url)
        

def get_news_list(news_url):
    result = requests.get(news_url)
    response = result.text
    soup = BeautifulSoup(response, 'lxml')
    for tag in soup.select('div.media-body > a'):
        if tag['href'] is "":
            continue
        else:
            article_url = "http://www.nownews.com"+tag['href']
            get_news_contents(article_url)

def get_news_contents(article_url):
    result = requests.get(article_url)
    if result.status_code == 200:
        response = result.text
        soup = BeautifulSoup(response, "lxml")    
        newsdatetime= soup.select('div.news-info')[0].text.split()
        newsdatetime_str=(newsdatetime[0])+'.'+(newsdatetime[2])
        timestampforcheck=time.mktime(time.strptime(newsdatetime_str, "%Y.%m.%d.%H:%M"))
        global checktimestamp
        #時間比對檢查
        if timestampforcheck>checktimestamp:
            script_json=soup.find(attrs={"type": "application/ld+json"})
            json_script=json.loads(script_json.text)        
            dic = dict()
            dic['Date']=json_script["datePublished"]
            dic['Title'] =json_script["headline"].replace("\u3000"," ")
            dic['Link']=json_script["mainEntityOfPage"]["@id"] 
            dic['serialNumber']=json_script["mainEntityOfPage"]["@id"].split('/')[-1]
            dic['keywords'] = soup.find("meta",{"name":"news_keywords"}).get("content")
            dic['articleBody']=json_script["articleBody"]
            dic['image_url']=json_script["image"]["url"]
            dic['author']=json_script["author"]["name"]
            dic['datetime']=newsdatetime_str
            dic['timestamp']=time.mktime(time.strptime(newsdatetime_str, "%Y.%m.%d.%H:%M"))
            con=''
            for p in soup.select('div.body > p'):
               con+=p.text.replace('\r','').replace('\t','').strip()
            dic['Content'] = con
#            print(dic['Link'])            
            data_insert(dic) #存入mongodb
            global out_put_list
            out_put_list.append(dic)

def data_insert(dic):
    client = pymongo.MongoClient("54.249.57.118", 27017)
    db = client['spadeAce']
    nownews_news = db.awsmongoNownews    
    nownews_news.insert(dic)
    
if __name__ == "__main__":
    try:
        start_time = time.time()
        out_put_list=list()    
        f = open('./NownewsMLB_ALL.json', 'r', encoding='utf-8')
        cralwered = f.read()
        #讀取時間戳記當檢查點
        checktimestamp=json.loads(cralwered)[0]['timestamp']        
        get_news_in_page() #爬蟲主程式
        out_put_list += json.loads(cralwered)    # json.loads只能讀取str，將舊的新聞接在新爬取的新聞後面
        f.close()    
        with open('./NownewsMLB_ALL.json', 'w+', encoding='utf-8') as f:       # 使用 'w+' 附蓋舊檔案
            f.write(json.dumps(out_put_list, indent=4, ensure_ascii=False))    # 將JSON格式的檔案寫入
    
    except Exception as ecpt:
        with open('./Nownews_MLB_err.txt', 'a') as f:
            print('中斷時間:{}\n\t{}\n\t'.format(time.strftime("%Y/%d/%m/%p %I:%M:%S"),ecpt),file=f)         
    finally:
        with open('./Nownews_MLB_log.txt', 'a') as f:
            print('程式結束:{}'.format(time.strftime("%Y/%d/%m/%p %I:%M:%S")),file=f)
            print('總共時間:{}'.format(round((time.time()-start_time),2)),file=f)
        



