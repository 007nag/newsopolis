import pandas as pd
from datetime import timedelta,datetime
from gensim import models
import pyLDAvis
import pyLDAvis.gensim_models
import pickle
pyLDAvis.enable_notebook()




def get_topics(strt_date, end_date):
    with open("dictionary",'rb') as fp:
        dictionary = pickle.load(fp)
    
    model   =  models.LdaModel.load('lda.model')
    news_df =  pd.read_csv('news-full-data.csv',encoding='utf-8')
        
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
    for index, score in sorted(model[bow_vector], key=lambda tup: -1*tup[1]):
        print("Score: {}\t Topic: {}".format(score, model.print_topic(index, 5)))
    test_vis = pyLDAvis.gensim_models.prepare(model, [bow_vector], dictionary=model.id2word)
    pyLDAvis.save_html(test_vis, 'templates/lda.html')