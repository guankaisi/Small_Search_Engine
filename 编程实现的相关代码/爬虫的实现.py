###第二天的作业用requests爬取所有相关连接并且保存html文件

from bs4 import BeautifulSoup
import requests
import time
import urllib
from urllib.parse import urljoin
import pickle

##输入种子
input_urls=['http://jiaowu.ruc.edu.cn','http://ctd.ruc.edu.cn','http://fangxue.ruc.edu.cn','http://iss.ruc.edu.cn','http://xsc.ruc.edu.cn']
def get_html(uri,headers={}):
    try:
        r = requests.get(uri, headers=headers)
        r.raise_for_status()
        r.encoding = "UFT_8"
        return r.text
    except:
        return None


def savedic(dic):
    with open('url.txt','w',encoding='utf-8') as f:
        for key,value in dic.items():
            f.write(str(key))
            f.write(':')
            f.write(value)
            f.write('\n')















# oneurl =input_urls[0]
# html_doc = get_html(oneurl)
#
# soup = BeautifulSoup(html_doc,"html.parser")
# urls = soup.find_all('a')
#
# all = []
# for num,url in enumerate(urls):
#
#     try:
#         print(url['href'])
#         if num==0:
#             continue
#         elif url['href']=='#':
#             continue
#         elif url['href'][0:4]!='http':
#             url['href']=oneurl+'/'+url['href']
#             all.append(url['href'])
#         else:
#             all.append(url['href'])
#     except:
#         continue
# print(all)

##将第一天写的函数引入,,改进与提高，提高它的robust性质，即使出错了也能跑
def crawl_all_urls(oneurl,html_doc):
    try:
        soup = BeautifulSoup(html_doc, "html.parser")
        urls = soup.find_all('a')
        all = []
        for url in urls:

            if url['href'][0:4] != 'http':
                url['href'] = urljoin(oneurl, url['href'])
                all.append(url['href'])
        return all



    except:
        print('fail')
        return None


headers = {'user_agent':'my-app/0.0.1'}
##初始化队列，采用广度优先搜索的方式

##要把上一次的queue保存下来，并且要导入进来

queue = []
with open('queue','rb') as f:
    queue = pickle.load(f)
    print("队列载入成功")
used_urlset = set()
for url in input_urls:
    queue.append(url)

count = 0
wait_time = 1
htmlpath = "C:/Users/kai'si/Desktop/编程集训/保存的网页/"

##创建一个空字典用来保存url和count的对用关系
dic = {}
while len(queue)!=0:
    count +=1
    url = queue.pop(0)
    print(queue)
    used_urlset.add(url)
    html_doc = get_html(url,headers = headers)
    url_sets = crawl_all_urls(url,html_doc)
    try:
        for new_url in url_sets:
            if new_url in used_urlset:
                continue
            else:
                queue.append(new_url)
      ##保存html文件
        with open('queue', 'wb') as f:
            pickle.dump(queue, f)
            print('队列保存成功')
        if count < 10:
            path = htmlpath + '0' + str(count) + '.html'
        else:
            path = htmlpath + str(count) + '.html'
        with open(path, 'w', encoding='utf-8') as f:
            print('保存{}'.format(path))
            f.write(html_doc)
            f.close()
        dic[count] = url
        savedic(dic)
        if wait_time > 0:
            print("等待{}秒之后开始抓取".format(wait_time))
        time.sleep(wait_time)
    except:
        print('失败了但是要继续')
        continue
##全部代码完成
