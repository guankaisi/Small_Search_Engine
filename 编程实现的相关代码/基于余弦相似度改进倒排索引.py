###任务一实现一个倒排索引
import jieba
import os
from collections import defaultdict
from collections import Counter
import numpy as np
filepath1 = "C:/Users/kai'si/Desktop/编程集训/保存的网页/"
collections = [file for file in os.listdir('保存的网页') if os.path.splitext(file)[1] =='.txt']
N = len(collections)
##N为集合中文档的数量

###构造term_docid_pairs，元组对列表，还有文件长度列表
term_docid_pairs = []
doc_length = []

for docid , filename in enumerate(collections):
    with open(os.path.join(filepath1,filename),encoding='utf-8') as fin :
        terms = [term for term in jieba.cut(fin.read()) if len(term.strip())>1]
        for term in terms:
            term_docid_pairs.append((term,docid))
        ##统计tf，用Counter字典定义了这个term出现的频数，value就是
        term_counts = np.array(list(Counter(terms).values()))

        log_tf = 1 + np.log(term_counts)
        doc_length.append(np.sqrt(np.sum(log_tf**2)))##用词汇频率定义文本长度


##排序，默认情况下两个tuple比较大小就是先按照第一个元素比较，在按照第二个元素比，因此不用key来改变
term_docid_pairs = sorted(term_docid_pairs)

##构造倒排索引
##posting list中每一项为Postin类对象
class Posting(object):
    def __init__(self,docid,tf=0):
        self.docid = docid
        self.tf = tf
    def __repr__(self):
        return '<docid:%d, tf: %d>'%(self.doid,self.tf)
##为了编程实现方便，我们在每个posting list开头加上了一个用来标记开头的-1，docid从0 开始
##注意这段代码在只有termdocid派人但是已经排序时才是正确的

inverted_index = defaultdict(lambda: [Posting(-1,0)])
##这一步是为了构建Postinglist即变长度列表，列表的元素都是Posting类其中储存了docid和tf信息
for term,docid in term_docid_pairs:
    posting_list = inverted_index[term]
    if docid!=posting_list[-1].docid:
        posting_list.append(Posting(docid,1))
    else:
        posting_list[-1].tf+=1

inverted_index = dict(inverted_index)
##将这和Counter变回普通字典

##定义一个简单的查询函数
def query(inverted_index,collections,query_term):
    postings_list = inverted_index[query_term][1:]#删去开头的-1
    results = [collections[posting.docid] for posting in postings_list]
    return results

def output_results(query,query_func = query):
    print('quety:%s,results:%s'%(query,query_func(inverted_index,collections,query)))

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
    query_terms=Counter(term for term in jieba.cut(querys))##将用户输入的自然语言进行分词
    for q in query_terms:
        w_tq = 1+np.log(query_terms[q])
        ##实现idf权重分数的步骤
        df1 = len(query(inverted_index,collections,q))
        w_qidf = np.log(N/df1)
        w_tq = w_tq*w_qidf
        posting_list = get_posting_list(inverted_index,q)
        for posting in posting_list:
            w_td = 1+np.log(posting.tf)
            w_didf=np.log(N/df1)
            w_td = w_td*w_didf
            scores[posting.docid]+=w_td * w_tq
    results = [(docid,score/doc_length[docid])for docid,score in scores.items()]
    results.sort(key=lambda x:-x[1])
    return results[0:k]


def retrieval_by_cosine_sim(inverted_index,collections,query,k=10):
    top_scores = cosine_scores(inverted_index,doc_length,query,k=k)
    results = [(collections[docid],score)for docid,score in top_scores]
    return results


x = output_results('人大教室老师',query_func = retrieval_by_cosine_sim)
print(x)


































