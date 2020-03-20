from bs4 import BeautifulSoup
import requests
import pandas as pd
from urllib.request import urlopen
from urllib import request
import json
import re
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #Change the default encoding of standard output

def Scraping(url='https://www.coronazaehler.de'):
  response = requests.get(url)
  response.encoding=response.apparent_encoding
  soup = BeautifulSoup(response.text ,'lxml')
  #get IT/100K of every state and the sum IT/100k
  table_sum=soup.find('table',{"id":"Deutschland"})
  item=table_sum.find_all('tr',{"onclick":re.compile('window.location')})
  item_sum=table_sum.find('tr',{"style":"border-top: 3px solid white;"})
  Sum_I100K=item_sum.find_all('td')[1].get_text()#the sum IT/100k 
  Stadt_Sum_I100K={} #define list containing IT/100K of each state
  for i in item:
    item_sub=i.find_all('td')   
    Stadt_Sum_I100K[item_sub[0].get_text()]=item_sub[1].get_text()

  sum_Infiziert=soup.find('h4',{"class":"red bold"}).get_text()#Total confirmed cases in Germany 
  sum_Genesen=soup.find('h4',{"class":"bold green"}).get_text()#Total number of cures in Germany 
  sum_Verstorben=soup.find('h4',{"class":"bold gray"}).get_text()#Total deaths in Germany 
  res={}
  res['Infiziert']=sum_Infiziert
  res['Genesen']=sum_Genesen 
  res['Verstorben']= sum_Verstorben 
  res['I/100K']=Sum_I100K

  Bundesland_list=[]#the state list
  Infiziert_list=[]#the confirmed cases of each state
  Verstorben_list=[]#Total deaths in each state
  Bundeslands= soup.find_all('h4',{"class":"card-title text-center"})
  Infiziert=soup.find_all('h5',{"class":"card-title red mb-0"})
  Verstorben=soup.find_all('h5',{"class":"card-title gray mb-0"})
  for i in range(16):
    Bundesland_list.append(Bundeslands[i].get_text())
    if len(Infiziert[i].get_text())<1:
       Infiziert_list.append(0)
    else:  
       Infiziert_list.append(Infiziert[i].get_text())
    if len(Verstorben[i].get_text())<1:
       Verstorben_list.append(0)
    else:
       Verstorben_list.append(Verstorben[i].get_text())

  tables = soup.find_all('table',{"class":"scrollTable"})#table of each city
  for m in range(16):
    Stadt=[]#the cities in each state
    Faelle=[]#the conformed cases in each city
    I100K=[] #the I/100K in each city
    landkreis={}
    Jede_Stadt=[]
    items0=tables[m].find_all('td',{"class":"text-left"})
    items1=tables[m].find_all('td',{"class":"text-right"})
    items2=tables[m].find_all('td',{"class":"red bold text-right"})
    for i in items0: 
      Stadt.append(i.get_text())
    for j in items2:
      Faelle.append(j.get_text())
    for k in items1: 
      try:     
        I100K.append(k.find('span').get_text())
      except:
        pass
    landkreis['Infiziert']=Infiziert_list[m]
    landkreis['Verstorben']=Verstorben_list[m]
    landkreis['I/100k']=Stadt_Sum_I100K[Bundesland_list[m]]
    for i in range(len(Stadt)): 
      l={}  
      l['Stadt']=Stadt[i]
      l['Fälle']=Faelle[i]
      l['I/100K']=I100K[i]
      Jede_Stadt.append(l)	
    landkreis['Jede Stadt']=Jede_Stadt 
    res[Bundesland_list[m]]=landkreis
     
  with open('Scraping_data.txt', 'w',encoding="utf-8") as f:
    json.dump(res,f,ensure_ascii=False,indent=2)

if __name__=="__main__":
  Scraping()