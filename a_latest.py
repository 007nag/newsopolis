import re
from bs4 import BeautifulSoup
import requests

from datetime import timedelta,datetime
start=datetime(year=2017,month=2,day=24)
end=datetime(year=2017,month=12,day=31)
import pandas
import time
#z=[]
day=0

f = open('news-dump.txt','a',encoding='utf-8')

for dat in pandas.date_range(start,end-timedelta(days=1),freq='d'):
    dat=str(dat).replace("-","/")[:10] + "/"
    url='https://www.thehindu.com/archive/print/' + dat
    req = requests.get(url)
    # f.write(str(req.content))
    # break


    soup = BeautifulSoup(req.content,'html.parser')
 
    #soup.find_all("div",{"id":re.compile("content-body-*")})
    for k in soup.find_all("div",{"class":"tpaper-container"}): 
        idx = 0       
        for i in k.find_all('a'):
            if 'href' in str(i) and i['href'][:5].strip()=='https':
                if(idx==0):
                    idx+=1
                    continue
                headline_list = i['href'].split('/')
                headline = headline_list[4]
                if(headline == 'tp-national'):
                    if('tp-' in headline_list[5]):
                        idx+=1
                        continue
                    headline = headline_list[5]
                if(headline == 'tp-international'  or headline == 'tp-business' or headline == 'tp-sports'):
                    headline = headline+ '$'+ headline_list[5]
                if(headline == 'tp-miscellaneous' or headline == 'tp-features' or headline=='tp-life' or headline=='tp-in-school' or headline == 'tp-opinion'):
                    continue

                    
                req1 = requests.get(i['href'])
                soup1 = BeautifulSoup(req1.content,'html.parser')
                content = soup1.find_all("div",{"id":re.compile("content-body-*")})
                if(len(content)>0):
                    f.write(dat)
                    f.write('\n')
                    f.write(headline)
                    f.write('\n')
                    # f.write(i['href'])
                    # f.write('\n')
                    #z+= content[0]
                    f.write(re.sub('<[^<]+?>', '', str(content[0])))
                    f.write('\n\n')
                    # f.write('**************************************')
                    # f.write('\n\n')
                idx+=1
    print(day+1,end='\r')
    day+=1     
    if(day%10==0):
        print('sing\n')
        time.sleep(5)

    
