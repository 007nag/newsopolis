

from json import dumps

from flask import Flask, render_template, request, redirect
import pickle
import os 
import cv2
import numpy as np
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
import speech_recognition as sr
from sentence_transformers import SentenceTransformer
import pandas as pd
from datetime import timedelta,datetime,date
from gensim import models
import pyLDAvis
import pyLDAvis.gensim_models
import pickle
model = SentenceTransformer('./paraphrase-MiniLM-L6-v2')

fff = open("documents.pkl",'rb')
docs = pickle.load(fff)

fff.close()
def speech2text():
    speechrec = sr.Recognizer()
    res=""
    try:
        with sr.Microphone() as mic_source:
            speechrec.adjust_for_ambient_noise(mic_source, duration=0.2)
            get_audio = speechrec.listen(mic_source)
            res  = speechrec.recognize_google(get_audio)
    
    except:
        pass 
    return res



from elasticsearch import Elasticsearch
es = Elasticsearch("http://localhost:9200")
def get_embedding(s):
    embedding=model.encode([s])
    return embedding[0]

app = Flask(__name__)

with open("lda/dictionary",'rb') as fp:
    dictionary = pickle.load(fp)
ldamodel   =  models.LdaModel.load('lda/lda.model')
news_df =  pd.read_csv('news-full-data.csv',encoding='utf-8')
def get_topics(strt_date, end_date):
    
        
    df = pd.DataFrame()
    strt_date_tok = strt_date.split('-')
    strt_date_yr     = int(strt_date_tok[0])
    strt_date_month  = int(strt_date_tok[1])
    strt_date_day    = int(strt_date_tok[2])
    
    end_date_tok     = end_date.split('-')
    end_date_yr      = int(end_date_tok[0])
    end_date_month   = int(end_date_tok[1])
    end_date_day     = int(end_date_tok[2])
    
    start=datetime(year=strt_date_yr,month=strt_date_month,day=strt_date_day)
    end=datetime(year=end_date_yr,month=end_date_month,day=end_date_day)
    for dat in pd.date_range(start,end,freq='d'):
        dat=str(dat).replace("-","/")[:10] + "/"
        df = pd.concat([df, news_df.loc[news_df['date'] == dat]], ignore_index=True, sort=False)
        #print(df.shape)
    final_doc = []
    bow_corpus = []
    for index, row in df.iterrows():
        tok_list = row['headline'].strip('[]').split(',')
        for tok in tok_list:
            final_doc.append(tok[1:-1])
        tok_list = row['content'].strip('[]').split(',')
        for tok in tok_list:
            final_doc.append(tok[1:-1])
       
    print(len(final_doc))
    bow_vector = dictionary.doc2bow(final_doc)
    test_vis = pyLDAvis.gensim_models.prepare(ldamodel, [bow_vector], dictionary=ldamodel.id2word)
    pyLDAvis.save_html(test_vis, 'templates/lda.html')

def get_autocomplete(query,fromdate,todate,categories):
    
    queryy = {
        "bool":
         {
               "must":[
             { "multi_match": {
               "query": query,
               "type": "bool_prefix",
               "fields": [
                   "title",
                   "title._2gram",
                   "title._3gram"
               ]
           }}],
             "filter":
             [
                 {
                     "terms":{
                         "category":categories
                     }

                 },
                 {
                     "range":{
                         "date":{"gte":fromdate ,
                         "lte":todate}
                     }

                 }

             ]

         }   

        }
    res=[]
    for i in es.search(index="autocomplete",body={'size': 5,'query': queryy})['hits']['hits']:
        res.append(i['_source']['title'])
    return res 
@app.route("/lda.html",methods=['GET'])
def ldaroute():
    return render_template("lda.html")
@app.route("/lda",methods=['POST'])
def lda_function():
    if request.method=='POST':
        fromdate = request.values.get("fromdate")
        todate = request.values.get("todate")
        print(fromdate,todate)
        get_topics(fromdate,todate)
        return "success"
        
@app.route("/autocomplete",methods=['POST'])
def autocompletefunc():
    if request.method=='POST':
        print('autocomplete')
        queryy= request.form['query']
        
        fromdate=request.form['fromdate']
        todate=request.form['todate']
        categories=[]
        for i in ("national","international","business","sport","frontpage"):
            if request.form.get(i):
                categories.append(i)
        if not categories:
            categories=["national","international","business","sport","frontpage"]
        
        z=get_autocomplete(queryy,fromdate,todate,categories)
        res=''
        for i in z: 
            res+= '<p  class="autocompleteelements" >'+i+'</p>'
        return res 
@app.route("/speech",methods=['GET'])
def funccc():
    if request.method=='GET':
        text=speech2text()
        return {"text":text}
@app.route("/",methods=['GET','POST'])
def send_query():
    
    if request.method=='POST':
        print('ok')
        #img = Image.open(request.files['image']).convert('L')
        try:
            imagefile = request.files['image']
        except:
            imagefile = None
        if imagefile and imagefile.filename!='':
            imagefile.save("ocr.jpg")  
            img=cv2.imread("ocr.jpg",0)
            queryy = pytesseract.image_to_string(img)
        else:
            
            if 'query' in request.form:
                queryy= request.form['query']
            else:
                return render_template("index.html")
        
        
              
        
        """img = np.array(img)
        img=img.astype(np.float)"""
        fromdate=request.form['fromdate']
        todate=request.form['todate']
        offset=int(request.form['offset'])
        categories=[]
        for i in ("national","international","business","sport","frontpage"):
            if request.form.get(i):
                categories.append(i)
        if not categories:
            categories=["national","international","business","sport","frontpage"]
        print(fromdate,todate,offset,categories)
        
        if queryy=="":
            queryy='e'
        if request.form.get("boolean"):
            
            
            data=[{"date":docs[i-1][0],"title":docs[i-1][1],"doc":docs[i-1][2]} for i in bool_query(queryy,categories,fromdate,todate,100,0.2)]
        else:
            data=[{"date":docs[i-1][0],"title":docs[i-1][1],"doc":docs[i-1][2]} for i in get_ids(queryy,categories,fromdate,todate,100,0.3,offset)]
        
        return render_template("upload.html",data=data)
    else:
        return render_template("index.html")
def get_ids(query_phrase,categories,from_date, to_date, size,threshold,offset=0):
    queryssss = get_embedding(query_phrase)
    
    script_query = {
    "script_score": {
    "query": {
    "bool":
     {


         "filter":
         [
             {
                 "terms":{
                     "category":categories
                 }

             },
             {
                 "range":{
                     "date":{"gte":from_date,
                     "lte":to_date}
                 }

             }

         ]

     }   

    },
    "script": {
    "source": """

    double a =cosineSimilarity(params.query_vector, 'Doc_vector');
    if (a<0) a=0;
    return a;

    """,
    "params": {"query_vector": queryssss }
    }}}
    
    response = es.search(index="documents",body={'from':offset,'size': size,'query': script_query})
    return [int(i['_id']) for i in response['hits']['hits'] if float(i['_score'])>=threshold]
def bool_query(query,categories,from_date,to_date,size,threshold):
    def f(i,j):
        op=[]
        st=[]
        no=False 
        while i<=j:

            if q[i]=='(':
                z=f(i+1,p[i]-1)
                i=p[i]+1
                if no:
                    z=set(iii for iii in range(111000) if iii not in z)
                    #z=not z
                st.append(z)


            elif q[i] in ('AND','OR'):

                if q[i]=='OR':
                    while op:

                        operator=op.pop()

                        a=st.pop(-1)
                        b=st.pop(-1)

                        if operator=='AND':
                            st.append(a.intersection(b))
                            #st.append(a and b)
                        else:
                            st.append(a.union(b))
                            #st.append(a or b)
                else:
                    while op and op[-1]=='AND':
                        operator=op.pop()
                        a=st.pop(-1)
                        b=st.pop(-1)
                        st.append(a.intersection(b))
                        #st.append(a and b)

                op.append(q[i])
                i+=1


            elif q[i]=='NOT':
                no=True 
                i+=1 
            else:
                z=ids[q[i]]
                if no:
                    z=set(iii for iii in range(111000) if iii not in z)
                    #z=not z 
                st.append(z)
                i+=1
        while op:
            operator=op.pop()
            a=st.pop(-1)
            b=st.pop(-1)
            if operator=='AND':
                st.append(a.intersection(b))
                #st.append(a and b)
            else:
                st.append(a.union(b))
                #st.append(a or b)
        return st[-1]

    
    se=set()
    

    #q='a AND NOT ( b AND c )'
    
    q=query.replace("("," ( ").replace(")"," ) ").split()
    l=len(q)
    st=[]
    p={}
    ids={}
    for i in range(l):
        if q[i]=='(':
            st.append(i)
        elif q[i]==')':
            p[st.pop(-1)]=i 
        elif q[i] not in ("AND","OR","NOT"):
            if q[i] not in ids:
                ids[q[i]]=set(get_ids(q[i],categories,from_date,to_date,9999,threshold))
                
    
    
    return list(f(0,l-1))[:100]


dff = pd.read_pickle("./df.pkl")
def get_trending_headlines(start_date,end_date,categories):
    year, month, day = map(int, start_date.split('-'))
    start_date = date(year, month, day)
    year, month, day = map(int, end_date.split('-'))
    end_date = date(year, month, day)
    mapping={'frontpage': 'frontpag', 'sport': 'sport', 'business': 'busi', 'national': 'nation', 'international': 'intern'}
    categories=[mapping[i] for i in categories]
    df=dff[dff.category.isin(categories)]
    df=df.reset_index(drop=True)
    df = df[(pd.Timestamp(start_date)<=df.date) & (df.date<=pd.Timestamp(end_date))]
    df=df.reset_index(drop=True)
    grouped=df.groupby(by='date')
    d=dict()
    for i in grouped:
        curr_df=i[1]
        s=set()
        for j in curr_df.named_tags:
            if len(j)>=2:
                for l in range(len(j)-1):
                    curr_bigram=tuple(sorted([j[l].lower(),j[l+1].lower()]))
                    s.add(curr_bigram)
        for j in s:
            if j in d:
                d[j]+=1
            else:
                d[j]=1
    d = dict(sorted(d.items(), key=lambda item: item[1],reverse=True))
    d_list = list(d.keys())[:10]
    def return_headline(tple):
        
        sse=set()
        res=""
        for i in range(len(df.named_tags)):
            string_list = [i.lower() for i in df.named_tags[i]]
            if (tple[0] in string_list) and (tple[1] in string_list):
                if df.unpreprocessed_headline[i] not in sse:
                    
                    res+="<p class='headlineparagraph'>"+df.unpreprocessed_headline[i]+"</p>"
                    sse.add(df.unpreprocessed_headline[i])
                    if len(sse)>=10:break 
        return res 
    res={}
    for tple in d_list:
        res[str(tple[1])+" "+str(tple[0])]=return_headline(tple)
    return res 

@app.route("/trendingheadlines",methods=['POST'])
def trendingheadlinesfunc():
    if request.method=='POST':
        fromdate=request.form['fromdate']
        todate=request.form['todate']
        categories=[]
        for i in ("national","international","business","sport","frontpage"):
            if request.form.get(i):
                categories.append(i)
        if not categories:
            categories=["national","international","business","sport","frontpage"]
        zzz=get_trending_headlines(fromdate,todate,categories)
        return dumps(zzz) 


@app.route("/covid_lda.html",methods=['GET'])
def covid_lda():
    return render_template("covid_lda.html")
@app.route("/f_lda.html",methods=['GET'])
def finance_lda():
    return render_template("f_lda.html")
if __name__=="__main__":
    app.run(debug=True)
