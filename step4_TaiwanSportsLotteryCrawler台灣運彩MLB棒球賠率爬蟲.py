#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import re,os,time
import requests as r
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
from collections import OrderedDict
import pymongo

#台灣運彩的MLB棒球賠率爬蟲
#要用phantomjs
#可以進MongoDB 要改65行的IP

def TSLcralwer():
    HOST = "https://www.sportslottery.com.tw/web/guest/sports-betting#m/all/s-443" #棒球s-443
    driver = webdriver.PhantomJS(executable_path='E:/phantomjs-2.1.1-windows/bin/phantomjs')
    driver.get(HOST)    # 輸入範例網址，交給瀏覽器 
    pageSource = driver.page_source    # 取得網頁原始碼 (含 JavaScript)
    soup = BeautifulSoup(pageSource, 'lxml')
    div_baseball=soup.find_all(class_="tab-content")
    div_content=soup.find_all(class_="bets live clearfix")

    Container=soup.find(id="upcomingEventsPerSportContainer")
    timetitle=Container.find_all(class_="title")
    game_dict_list=list()
    for tag in timetitle:    
        date_str=tag.text.replace('民國 ','').split(' 年 ')
        year_str=str(int(date_str[0])+1911)
        game_date=datetime.strptime(date_str[1], "%m 月 %d 日").strftime(year_str+"-%m-%d")    
        for sibling in tag.next_siblings:
            game_dict=dict()
            if sibling.attrs['class']==['bets', 'live', 'clearfix']:
                game_dict["game_ID"]=sibling.find(class_="tooltipclass event-code two-line").text            
                game_dict["pass"]=sibling.find(class_="tooltipclass event-code indicator two-line").text
                game_time_str=sibling.find(class_="tooltipclass event-time").text.split(" (")[0]
                game_datetime_str=game_date+' '+game_time_str
                game_dict['game_datetime']=game_datetime_str
                game_timestamp = time.mktime(time.strptime(game_datetime_str, '%Y-%m-%d %H:%M'))
                game_dict['game_timestamp']=game_timestamp
                game_dict["title"]=sibling.find(class_="tooltipclass grad-b bet two forBetting ")["data-original-title"].replace("<br></a>",":")
                Away_Home_id=sibling.find_all(class_="tooltipclass grad-b bet two forBetting ")
                Away_Home_name=sibling.find_all(class_="ellipsis longer")
                Away_Home_odds=sibling.find_all(class_="pull-right")
                game_dict["away_idd"]=Away_Home_id[0]["id"]
                game_dict["home_idd"]=Away_Home_id[1]["id"]
                game_dict["away_team"]=Away_Home_name[0].text
                game_dict["home_team"]=Away_Home_name[1].text
                game_dict["away_odds"]=Away_Home_odds[0].text
                game_dict["home_odds"]=Away_Home_odds[1].text      
                crawled_time=float()
                crawled_time=time.time()
                game_dict["crawled_timestamp"]= crawled_time
                game_dict["crawled_datetime"]=time.strftime("%Y-%m-%d %H:%M:%S")
                game_dict_list.append(game_dict)
            else:
                break
    print(game_dict_list[0])
    with open('./TaiwanSportsLottery.json', 'a+', encoding='utf-8') as f:
        f.write(json.dumps(game_dict_list, indent=4, ensure_ascii=False)) 
    driver.close()
    return game_dict_list

def data_insert(dic):
    client = pymongo.MongoClient("localhost", 27017)
    # client = pymongo.MongoClient("66.66.100.118", 27017)
    db = client['spadeAce']
    nownews_news = db.TaiwanSportsLottery    
    nownews_news.insert(dic)

if __name__ == "__main__":    
    data_insert(TSLcralwer())

