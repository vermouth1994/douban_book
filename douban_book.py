# coding=utf-8
import sys
import time
import urllib
import urllib2
import redis
import requests
import json
import traceback
import MySQLdb as mdb
import numpy as np
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf8')

# Some User Agents
hds = [{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}, \
       {
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'}, \
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}]


def book_spider(book_tag):
    page_num = 0
    book_list = []
    try_times = 0

    while 1:
        #url='http://www.douban.com/tag/%E5%B0%8F%E8%AF%B4/book?start=0' # For Test
        url = 'http://www.douban.com/tag/' + urllib.quote(book_tag) + '/book?start=' + str(page_num * 15)
        time.sleep(np.random.rand() * 5)
        try:
            req = urllib2.Request(url, headers=hds[page_num % len(hds)])
            source_code = urllib2.urlopen(req).read()
            plain_text = str(source_code)
        except (urllib2.HTTPError, urllib2.URLError), e:
            print e
            continue

        soup = BeautifulSoup(plain_text)
        list_soup = soup.find('div', {'class': 'mod book-list'})

        try_times += 1
        if list_soup == None and try_times < 200:
            continue
        elif list_soup == None or len(list_soup) <= 1:
            break

        for book_info in list_soup.findAll('dd'):
            title = book_info.find('a', {'class': 'title'}).string.strip()
            desc = book_info.find('div', {'class': 'desc'}).string.strip()
            desc_list = desc.split('/')
            book_url = book_info.find('a', {'class': 'title'}).get('href')
            book_sub_id = book_url.split("subject")[1].split("/")[1]

            try:
                author_info = '作者/译者： ' + '/'.join(desc_list[0:-3])
            except:
                author_info = '作者/译者： 暂无'
            try:
                pub_info = '出版信息： ' + '/'.join(desc_list[-3:])
            except:
                pub_info = '出版信息： 暂无'
            try:
                rating = book_info.find('span', {'class': 'rating_nums'}).string.strip()
            except:
                rating = '0.0'
            try:
                people_num = get_people_num(book_url)
                people_num = people_num.strip('人评价')
            except:
                people_num = '0'

            book_list.append([title, rating, people_num, author_info, pub_info, book_sub_id])
            try_times = 0
        page_num += 1
        print 'Downloading Information From Page %d' % page_num
    return book_list


def get_people_num(url):
    try:
        req = urllib2.Request(url, headers=hds[np.random.randint(0, len(hds))])
        source_code = urllib2.urlopen(req).read()
        plain_text = str(source_code)
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e
    soup = BeautifulSoup(plain_text)
    people_num = soup.find('div', {'class': 'rating_sum'}).findAll('span')[1].string.strip()
    return people_num


def do_spider(book_tag_lists):
    book_lists = []
    for book_tag in book_tag_lists:
        book_list = book_spider(book_tag)
        book_list = sorted(book_list, key=lambda x: x[1], reverse=True)
        book_lists.append(book_list)
    return book_lists


def sync_redis(book_lists, book_tag_lists):
    try:
        r = redis.Redis(host='******', port=6379, db=0, password="*****")
        p = r.pipeline()
        con = mdb.connect('******', 'root', '******', 'crawl_cms', charset="utf8")
        cur = con.cursor()
        with con:
            for i in range(len(book_tag_lists)):
                count = 1
                all_count = len(book_lists[i])
                for j in book_lists[i]:
                    try:
                        print(j[0])
                        count += 1
                        book_name = j[0]
                        this_book = {}
                        this_book["id"] = count
                        this_book["name"] = j[0]
                        if "：" in book_name or ":" in book_name:
                            book_name = book_name.replace(":", " ").replace("：", " ")
                        this_book["score"] = float(j[1])
                        this_book["score_num"] = int(j[2])
                        this_book["author"] = j[3]
                        this_book["pub"] = j[4]
                        try:
                            get_book_detail_url = "https://api.douban.com/v2/book/" + str(j[5])
                            book_detail = requests.get(get_book_detail_url).content
                            this_book["content"] = json.loads(book_detail)
                        except:
                            traceback.print_exc()
                            this_book["content"] = {}
                        p.set(book_tag_lists[i] + ':' + book_name, json.dumps(this_book, ensure_ascii=False))
                        book_value = [j[0], j[5], json.dumps(this_book["content"]), book_tag_lists[i]]
                        cur.execute('insert into douban_book(name,subject,content,menu_type) values(%s,%s,%s,%s)',
                                    book_value)
                    except:
                        traceback.print_exc()
                        continue
        p.execute()
    except:
        traceback.print_exc()


if __name__ == '__main__':
    tec = ["web", '计算机', "互联网", "编程", "科技", "数据库"]
    economic = ['经济学', '管理', "金融", "股票"]
    life = ['爱情', "生活", '旅行', "成长", "励志t", "摄影", "职场", "人际关系", "心理"]
    culture = ['文化', '历史', "哲学", "社会学", "艺术", "传记", "政治", "宗教", "电影", "思想", "军事", "音乐"]
    novel = ['言情', '推理', "科幻", "杂文", "诗歌", "随笔", "青春", "都市", "奇幻", "日本", "日本文学", "东野圭吾"]
    all_tag = [tec, economic, life, culture, novel]
    for tag in all_tag:
        for k in tag:
            print([k])
            book_lists = do_spider([k])
            sync_redis(book_lists, [k])
            time.sleep(15)
