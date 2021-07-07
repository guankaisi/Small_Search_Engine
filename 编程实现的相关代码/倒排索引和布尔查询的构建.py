###任务一实现一个倒排索引
import jieba
import os
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
# ##第一步将这些网页的正文用txt保存下来
collections = [file for file in os.listdir('保存的网页')if os.path.splitext(file)[1] =='.html']

filepath1 = "C:/Users/kai'si/Desktop/编程集训/保存的网页/"

for num,web in enumerate(collections):
    path = filepath1+web
    with open(path,'r',encoding='utf-8') as h:
        txt = h.read(-1)
        soup = BeautifulSoup(txt,'html.parser')
        txt = soup.text
    path = path[:-4]+'txt'
    with open(path,'w',encoding='utf-8') as h :
        h.write(txt)
        print("save ",num)

# 倒排索引构建样例
# 找出所有教师的正文信息
collections = [file for file in os.listdir('保存的网页') if os.path.splitext(file)[1] =='.txt']
###构造term_docid_pairs
term_docid_pairs = []
for docid , filename in enumerate(collections):
    with open(os.path.join(filepath1,filename),encoding='utf-8') as fin :
        for term in jieba.cut(fin.read()):
            ##必要的过滤，建议实现一个更复杂的函数,目的是出去哪些空格，标点符号
            if len(term.strip())<=1:
                continue
            term_docid_pairs.append((term,docid))
##第一步我先把昨天爬取网页的txt文档提取出来,上午不用着急开始做，先把思路弄懂
##倒排检索的目标：返回用户信息需求相关的信息的文档，现在差不多弄明白了倒排索引的基本操作
# doc0 = '互联网大数据管理，信息检索（互联网搜索），数据挖掘和机器学习'
# doc1 = '主要研究方向为为信息检索，网络搜索，搜索用户行为分析和机器学习'
# term_docid_pairs = [(t.strip(),0) for t in jieba.lcut(doc0) if len(t.strip())>1] + \
#     [(t.strip(),1) for t in jieba.lcut(doc1) if len(t.strip())>1]
# print(term_docid_pairs)
##排序，默认情况下两个tuple比较大小就是先按照第一个元素比较，在按照第二个元素比骄傲，因此不用key来改变
term_docid_pairs = sorted(term_docid_pairs)
##构造倒排索引
##为了编程实现方便，我们在每个posting list开头加上了一个用来标记开头的-1，docid从0 开始
##注意这段代码在只有termdocid派人但是已经排序时才是正确的
inverted_index = defaultdict(lambda :[-1])
for term,docid in term_docid_pairs:
    postings_list = inverted_index[term]
    if docid != postings_list[-1]:
        postings_list.append(docid)

##定义一个简单的查询函数
def query(inverted_index,collections,query_term):
    docid_list = inverted_index[query_term][1:]
    results = [collections[docid] for docid in docid_list]
    return results

def output_results(query,query_func = query):
    print('quety:%s,results:%s'%(query,query_func(inverted_index,collections,query)))

output_results('刘伟')
##合并两个postings list
l1 = [1,2,3,4]
l2 = [2,3,4,5]
def intersection(l1,l2):
    answer = []
    p1,p2 = iter(l1),iter(l2)
    try:
        docID1,docID2 = next(p1),next(p2)
        while True:
            if docID1 == docID2:
                answer.append(docID1)
                docID1,docID2 = next(p1),next(p2)
            elif docID1<docID2:
                docID1 = next(p1)
            else:
                docID1 = next(p2)
    except StopIteration:
        pass
    return answer
##实现or逻辑的归并
def merge(l1,l2):
    l,r = 0,0
    answer = []
    while l<len(l1) and r < len(l2):
        if l1[l]<l2[r]:
            answer.append(l1[l])
            l+=1
        else:
            answer.append(l2[r])
            r+=1
    answer+=l1[l:]
    answer+=l2[r:]
    return answer


def logic_and_query(inverted_index,collections,queries):
    #第一个querie的结果
    l1 = inverted_index[queries[0]][1:]
    for q in queries[1:]:
        l2 = inverted_index[q][1:]
        l1 = intersection(l1,l2)
    results = [collections[docid]for docid in l1]
    return results
##接下来完成逻辑或的任务
def logic_or_query(inverted_index,collections,queries):
    l1 = inverted_index[queries[0]][1:]
    for q in queries[1:]:
        l2 = inverted_index[q][1:]
        l1 = merge(l1, l2)
    results = [collections[docid] for docid in l1]
    return sorted(list(set(results)))



x = logic_and_query(inverted_index,collections,('人大','中心'))
y = logic_or_query(inverted_index,collections,('人大','中心'))
print(x)
print(y)



