from flask import Flask, render_template, request, redirect
import tensorflow_hub as hub
import os 
import cv2
import numpy as np
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
import speech_recognition as sr

def speech2text():
    r = sr.Recognizer()
    text=""	
    try:
        with sr.Microphone() as source2:
            r.adjust_for_ambient_noise(source2, duration=0.2)
            audio2 = r.listen(source2)
            text  = r.recognize_google(audio2)
            text  = text.lower()
    except:
        pass 
    return text 


model = hub.load("../model")
from elasticsearch import Elasticsearch
es = Elasticsearch("http://localhost:9200")
def get_embedding(s):
    embedding=model([s])
    return embedding.numpy()[0]

app = Flask(__name__)
@app.route("/")
def zz():
    return render_template("index.html")

@app.route("/speech",methods=['GET'])
def funccc():
    if request.method=='GET':
        text=speech2text()
        return {"text":text}
@app.route("/send_query",methods=['POST','GET'])
def upload():
    if request.method=='POST':
        #img = Image.open(request.files['image']).convert('L')
        imagefile = request.files.get('image', '')
        if imagefile.filename!='':
            imagefile.save("ocr.jpg")  
            img=cv2.imread("ocr.jpg",0)
            queryy = pytesseract.image_to_string(img)
        else:
            queryy= request.form['query']
        
        print(queryy)
              
        
        """img = np.array(img)
        img=img.astype(np.float)"""
        fromdate=request.form['fromdate']
        todate=request.form['todate']
        categories=[]
        for i in ("national","international","business","sport","miscellaneous"):
            if request.form.get(i):
                categories.append("tp-"+i)
        if not categories:
            categories=["tp-national","tp-international","tp-business","tp-sport","tp-miscellaneous"]
        print(categories,fromdate,todate)
        
        if queryy=="":
            queryy='e'
        if request.form.get("boolean"):
            data=[{"_id":i, "_score":0} for i in bool_query(queryy,categories,fromdate,todate,100,0.1)]
        else:
            data=[{"_id":i, "_score":0} for i in get_ids(queryy,categories,fromdate,todate,100,0.1)]
        print(len(data))
        return render_template("upload.html",data=data)
    else:
        return render_template("index.html")
def get_ids(query_phrase,categories,from_date, to_date, size,threshold):
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
    
    response = es.search(index="documents",body={'size': size,'query': script_query})
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
                    z=set(iii for iii in range(50000) if iii not in z)
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
                    z=set(iii for iii in range(50000) if iii not in z)
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

    x=[]
    se=set()
    y=[{'a','c'},{'b','d','f'},{'a','b','c','d','e'},{'a','c','f'},{'c','d'}]

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
                ids[q[i]]=set(get_ids(q[i],categories,from_date,to_date,size,threshold))
                
    
    
    return f(0,l-1)
if __name__=="__main__":
    app.run(debug=True)
