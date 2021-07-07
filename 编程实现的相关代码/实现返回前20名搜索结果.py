##day5编程集训几天的任务是重新构建爬虫网页，然后设计函数与字典相互对应，返回预测分数最大的前20各url
###任务一实现一个倒排索引
import jieba
import os
from collections import defaultdict
from collections import Counter
import numpy as np
import pickle
import time as t
filepath1 = "C:/Users/kai'si/Desktop/编程集训/保存的网页/"
filepath2 = "C:/Users/kai'si/Desktop/编程集训/"
collections = [file for file in os.listdir('保存的网页') if os.path.splitext(file)[1] =='.txt']
# collections = collections[:501]

N = len(collections)
print(N)
#N为集合中文档的数量
#构造term_docid_pairs，元组对列表，还有文件长度列表,因为但是运行的时间过长，我们将term_docid_pairs保存到一个txt文档之中
term_docid_pairs = []
doc_length = []
for docid , filename in enumerate(collections):
    with open(os.path.join(filepath1,filename),'r',encoding='utf-8') as fin :
        terms = [term for term in jieba.cut(fin.read()) if len(term.strip())>1]

        for term in terms:
            term_docid_pairs.append((term,docid))
        print('done',docid)

        ##统计tf，用Counter字典定义了这个term出现的频数，value就是
        term_counts = np.array(list(Counter(terms).values()))

        log_tf = 1 + np.log(term_counts)
        doc_length.append(np.sqrt(np.sum(log_tf**2)))##用词汇频率定义文本长度
with open('lenthgy','wb') as f:
    pickle.dump(doc_length,f)
    print("列表保存成功")
#排序，默认情况下两个tuple比较大小就是先按照第一个元素比较，在按照第二个元素比，因此不用key来改变
term_docid_pairs = sorted(term_docid_pairs)
#
#构造倒排索引
#posting list中每一项为Postin类对象
class Posting(object):
    def __init__(self,docid,tf=0):
        self.docid = docid
        self.tf = tf
    def __repr__(self):
        return '<docid:%d, tf: %d>'%(self.docid,self.tf)
# 为了编程实现方便，我们在每个posting list开头加上了一个用来标记开头的-1，docid从0 开始
# 注意这段代码在只有termdocid派人但是已经排序时才是正确的
# 思考一下，如果不用Posting这个类，只用元组的列表是否合适
inverted_index = defaultdict(lambda: [Posting(-1,0)])
# ##这一步是为了构建Postinglist即变长度列表，列表的元素都是Posting类其中储存了docid和tf信息
for term,docid in term_docid_pairs:
    posting_list = inverted_index[term]
    if docid!=posting_list[-1].docid:
        posting_list.append(Posting(docid,1))
    else:
        posting_list[-1].tf+=1
inverted_index = dict(inverted_index)##注意了我们需要的是什么
# 将这个列表保存
with open('dictionary','wb') as f:
    pickle.dump(inverted_index,f)
    print('字典保存成功')

print("start loading:cost time about 10 seconds")
with open('dictionary','rb') as f:
    inverted_index = pickle.load(f)
    print("字典载入成功")

with open('lenthgy','rb') as f:
    doc_length = pickle.load(f)
    print("长度列表载入成功")





##将这和Counter变回普通字典
##定义一个简单的查询函数，这里会需要inveted_index和doc_length两个列表需要保存
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
        if df1!=0:
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


# x = output_results('人大教室老师',query_func = retrieval_by_cosine_sim)

##下面这个函数就是为了将上述返回的文件名列表，转换成url的列表,变成有名字和url的列表
webnum=[]
namenum = []
with open('url.txt', 'r', encoding='utf-8') as fin:
    webs = fin.readlines(-1)
for web in webs:
    flag = web.find(':')
    a = int(web[:flag])
    webnum.append(a)
with open('name.txt','r',encoding='utf-8') as fin:
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
            results.append({'title':titles2[i],'url':urls2[i]})
        except:
            return results
    return  results

x = evaluate('关开思中国人民大学')
print(x)







































