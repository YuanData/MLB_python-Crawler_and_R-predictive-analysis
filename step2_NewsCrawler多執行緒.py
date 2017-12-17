#!/usr/bin/env python3
# coding: utf-8
import queue
import threading

from bs4 import BeautifulSoup
import requests,json,time

class Worker(threading.Thread):

    def __init__(self, work_queue):
        super().__init__()
        self.work_queue = work_queue


    def run(self):
        while True:
            try:
                url = self.work_queue.get()
                self.get_news_list(url)
            finally:
                self.work_queue.task_done()


    def get_news_list(self, url):
        try:
            result = requests.get(url)
            response = result.text
            soup = BeautifulSoup(response, 'lxml')
            for tag in soup.select('div.media-body > a'):
                if tag['href'] is "":
                    continue
                else:
                    article_url = "http://www.nownews.com"\
                    +tag['href']
                    url_list.append(article_url)
        except Exception as ecpt:
            print(ecpt)


def work_main_step():
    page_list = get_news_in_page()
    work_queue = queue.Queue()
    threading_no=10
    for i in range(threading_no):
        worker = Worker(work_queue)
        worker.daemon = True
        worker.start()
    for url in page_list:
        work_queue.put(url)
    work_queue.join()


def get_news_in_page():
    totalPage = 1285
    page_list = []
    for page in range(1,totalPage+1):
        news_url="http://www.nownews.com\
        /search/MLB/{}".format(page)
        page_list.append(news_url)
    return page_list


if __name__ == "__main__":
    try:
        tStart = time.time()
        url_list = []
        out_put_list=[]
        work_main_step()
        work_second_step()
        
        with open('Nownews_keywords.json', 'w+',encoding= 'utf-8') as f:
            f.write(json.dumps(out_put_list, indent = 4, ensure_ascii=False))
    finally:
        with open('Time_record_keywords.txt', 'a') as f:
            print ('總共花時間 %d seconds' % (time.time() - tStart),file=f)
