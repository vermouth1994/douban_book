# coding=utf-8
import requests
from bs4 import BeautifulSoup
import os

headers = {'referer': 'http://jandan.net/',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'}


# 保存图片
def save_jpg(res_url):
    index = 0
    file_list = []
    for f in os.listdir("/mnt/xys/crawl/pic/jiandan/"):
        file_list.append(int(f.split(".")[0]))
    if len(file_list) == 0:
        max_file_num = 1
    else:
        max_file_num = max(file_list) + 1
    index += max_file_num
    html = BeautifulSoup(requests.get(res_url, headers=headers).text, "html5lib")
    for link in html.find_all('a', {'class': 'view_img_link'}):
        with open('/mnt/xys/crawl/pic/jiandan/{}.{}'.format(index, link.get('href')[
                                                                   len(link.get('href')) - 3: len(link.get('href'))]),
                  'wb') as jpg:
            jpg.write(requests.get("http:" + link.get('href')).content)
        index += 1


# 抓取煎蛋妹子图片，默认抓取2页
if __name__ == '__main__':
    url = 'http://jandan.net/ooxx'
    for i in range(0, 2):
        save_jpg(url)
        url = BeautifulSoup(requests.get(url, headers=headers).text).find('a', {'class': 'previous-comment-page'}).get(
            'href', "lxml")
    print("done.....")