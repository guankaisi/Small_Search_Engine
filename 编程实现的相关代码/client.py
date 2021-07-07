import json
import requests
import getpass
from urllib.parse import urljoin
from tqdm import tqdm

# Your Search Engine Function
# from search_engine import evaluate
from flask import Flask, render_template, request
import jieba
import os
from collections import defaultdict
from collections import Counter
import numpy as np
import pickle


class Posting(object):
    def __init__(self, docid, tf=0):
        self.docid = docid
        self.tf = tf
    def __repr__(self):
        return '<docid:%d, tf: %d>' % (self.docid, self.tf)

collections = [file for file in os.listdir("C:/Users/kai'si/Desktop/编程集训/保存的网页") if os.path.splitext(file)[1] == '.txt']
# collections = collections[:501]

N = len(collections)
print("start loading:cost time about 10 seconds")
with open("C:/Users/kai'si/Desktop/编程集训/dictionary",'rb') as f:
    inverted_index = pickle.load(f)
    print("字典载入成功")

with open("C:/Users/kai'si/Desktop/编程集训/lenthgy",'rb') as f:
    doc_length = pickle.load(f)
    print("长度列表载入成功")
def query0(inverted_index,collections,query_term):
    try:
        postings_list = inverted_index[query_term][1:]  # 删去开头的-1

        results = [collections[posting.docid] for posting in postings_list]
        return results
    except:
        return []


def output_results(query,query_func = query0):
    print('query:%s,results:%s'%(query,query_func(inverted_index,collections,query)))

##获取构建倒排索引字典里面的边长列表
def get_posting_list(inverted_index, query_term):
    try:
        return inverted_index[query_term][1:]
    except KeyError:
        return []
##计算cos的夹角值，计算权重得分,这里面没有计算idf，但使用了对数词频计算的例子
##下面我的计算是要考虑idf问题
def cosine_scores(inverted_index,doc_length,querys,k=3):
    scores = defaultdict(lambda :0.0)#保存分数
    query_terms=Counter(term for term in jieba.cut(querys)if len(term.strip())>1)##将用户输入的自然语言进行分词
    for q in query_terms:
        w_tq = 1+np.log(query_terms[q])
        ##实现idf权重分数的步骤
        df1 = len(query0(inverted_index,collections,q))
        if df1 !=0:
            w_qidf = np.log(N / df1)
            w_tq = w_tq * w_qidf
            posting_list = get_posting_list(inverted_index, q)
            for posting in posting_list:
                w_td = 1 + np.log(posting.tf)
                w_didf = np.log(N / df1)
                w_td = w_td * w_didf
                scores[posting.docid] += w_td * w_tq
        else:
            pass
    results = [(docid,score/doc_length[docid])for docid,score in scores.items()]
    results.sort(key=lambda x:-x[1])
    return results


def retrieval_by_cosine_sim(inverted_index,collections,query,k=10000):
    top_scores = cosine_scores(inverted_index,doc_length,query,k=k)
    results = [(collections[docid],score)for docid,score in top_scores]
    return results
webnum=[]
namenum = []
with open("C:/Users/kai'si/Desktop/编程集训/url.txt", 'r', encoding='utf-8') as fin:
    webs = fin.readlines(-1)
for web in webs:
    flag = web.find(':')
    a = int(web[:flag])
    webnum.append(a)
with open("C:/Users/kai'si/Desktop/编程集训/name.txt",'r',encoding='utf-8') as fin:
    names = fin.readlines(-1)
for name in names:
    flag = name.find(':')
    a = int(name[:flag])
    namenum.append(a)

# print(namenum)


def evaluate(query:str) ->list:##改进改成元素是列表的词典
    doclist = retrieval_by_cosine_sim(inverted_index,collections,query)
    docnum=[]
    urls = []
    titles=[]
    for doc,num in doclist:
        doc = int(doc[0:-4])
        docnum.append(doc)
    for doc in docnum:
        index1 = webnum.index(doc)
        flag1 = webs[index1].find(':')
        url = webs[index1][flag1 + 1:-1]
        urls.append(url)
        try:
            index2 = namenum.index(doc)
            flag2 = names[index2].find(':')

            title = names[index2][flag2 + 1:-1]
            titles.append(title)
        except:
            titles.append(" ")
    urls2 = list(set(urls))
    urls2.sort(key = urls.index)##这个是最终要的列表
    titles2 = list(set(titles))
    titles2.sort(key = titles.index)
    results = []
    for i in range(20):
        try:
            results.append(urls2[i])
        except:
            return results
    return  results
base_url = 'http://183.174.228.82:8080/'

def input_idx():
    idx = input('学号：')
    assert len(idx) == 10, '学号长度必须为 10'
    return idx

def input_passwd():
    passwd = getpass.getpass('助教code (直接回车以进入调试模式，不计分)：')
    if passwd == '':
        print('=== 调试模式 ===')
    return passwd

def login(idx, passwd):
    url = urljoin(base_url, 'login')
    r = requests.post(url, data={'idx': idx, 'passwd': passwd})
    r_dct = eval(r.text)
    queries = r_dct['queries']
    if r_dct['mode'] == 'illegal':
        raise ValueError('助教密码错误，请勿尝试破解密码等非法手段，本次行为已被记录')
    print(f'{len(queries)} queries.')
    return queries

def send_ans(idx, passwd, urls):
    url = urljoin(base_url, 'mrr')
    r = requests.post(url, data={'idx': idx, 'passwd': passwd, 'urls': json.dumps(urls)})
    print()
    r_dct = eval(r.text)
    if r_dct['mode'] == 'illegal':
        raise ValueError('助教密码错误，请勿尝试破解密码等非法手段，本次行为已被记录')
    return r_dct['mode'], r_dct['mrr']

def main():
    idx = input_idx()
    passwd = input_passwd()
    queries = login(idx, passwd)
    
    tot_urls = []
    for query in tqdm(queries, desc='Searching:'):
        urls = evaluate(query)
        tot_urls.append(urls)
        

    print('等待服务器相应...', flush=True)
    mode, mrr = send_ans(idx, passwd, tot_urls)
    print(f'您的 MRR 评测结果为 [{mrr}], [{mode}] 模式')

if __name__ == '__main__':
    main()
