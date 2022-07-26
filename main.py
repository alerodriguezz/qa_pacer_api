import requests
import os 
import json 
import mechanicalsoup
import warnings
import pandas as pd
from commonregex import CommonRegex
import re

warnings.filterwarnings(action='ignore')

my_login = os.environ['user']
my_pass = os.environ['pass']


#Authentification
authUrl="https://qa-login.uscourts.gov/services/cso-auth"
authHeaders={'Content-type': 'application/json',
'Accept': 'application/json'}
authBody={
  "loginId": my_login,
"password": my_pass,
"clientCode": "testclientcode",
"redactFlag": "1"
}

authResponse = requests.post(authUrl,json=authBody,headers=authHeaders)


print("Authentication response: ",authResponse.json(),"\n")

myToken = authResponse.json()['nextGenCSO']

#save token 

print ("token: ",myToken,"\n")

#Batch Party Search

batchHeaders={'Content-type': 'application/json',
'Accept': 'application/json','X-NEXT-GEN-CSO': myToken }
batchBody={
"federalBankruptcyChapter" : [ 11 ],
"dateFiledFrom": "2016-01-01",
"dateFiledTo":"2016-01-31", 
}

batchUrl="https://qa-pcl.uscourts.gov/pcl-public-api/rest/cases/find"

batchResponse = requests.post(batchUrl,json=batchBody,headers=batchHeaders)

obj=batchResponse.json()


#print("Search response: ",json.dumps(obj,indent=4),"\n")


print("Search response: ",json.dumps(obj["receipt"],indent=4),"\n")
print("Search response: ",json.dumps(obj["pageInfo"],indent=4),"\n")
#print("Search response: ",json.dumps(obj["content"],indent=4),"\n")


print("\nPrinting nested dictionary as a key-value pair","\n")



br= mechanicalsoup.StatefulBrowser()
login_link="https://qa-login.uscourts.gov/csologin/login.jsf"

br.open(login_link)

br.get_current_page()
br.select_form('form[id="loginForm"]')
br.get_current_form()

br["loginForm:loginName"]= my_login
br["loginForm:password"]= my_pass
br.submit_selected()

data={
  'Name':[],
  'Address':[],
  'Phone Number':[]
}
"""'SSN':[],
  'Bankruptcy Chapter': [],
  'Date Filed' : [],
  'Case Id' : []"""
for i in obj['content']:
  if "caseLink" in i.keys():
    print("Court ID: ", i['courtId'])
    print("Case ID: ",i['caseId'])
    print("Court Title :", i['caseTitle'])
    print("Federal Bankruptcy Chapter: ", i['bankruptcyChapter'])
    print("Date Filed: ",i['dateFiled'])
    link = i['caseLink'].replace("iqquerymenu","NoticeOfFiling")
    #print("Link:", link,"\n")
    br.open(link,verify=False)
    try:
      br.get_current_page()
      br.select_form('form[id="referrer_form"]')
      br.get_current_form()
      br.submit_selected()
      #br.launch_browser()
    except:
      print("no referrer form") 
    print("Debtor Info: \n")
    #print (br.get_current_page().find("p",id="3").b.text,"\n\n")


    # retrieve debtor name
    name= br.get_current_page().find("p",id="3").b.text
    print(name)
    if (name=="Box Check"):
      print ("\n---------------------------------------------\n")
      pass
    else:
    

      #remove name from paragraph string obj
      paragraph = br.get_current_page().find("p",id="3").text.replace(name,"")
      
      #retrieve debtor address w/ regex
      address_validate_pattern = r"(?:(\d+ [A-Za-z][A-Za-z ]+)[\s,]*([A-Za-z#0-9][A-Za-z#0-9 ]+)?[\s,]*)?(?:([A-Za-z][A-Za-z ]+)[\s,]+)?((?=AL|AK|AS|AZ|AR|CA|CO|CT|DE|DC|FM|FL|GA|GU|HI|ID|IL|IN|IA|KS|KY|LA‌​|ME|MH|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|MP|OH|OK|OR|PW|PA|PR|RI|SC|SD‌​|TN|TX|UT|VT|VI|VA|WA|WV|WI|WY)[A-Z]{2})(?:[,\s]+(\d{5}(?:-\d{4})?))?"
      temp=re.search(address_validate_pattern, paragraph) 
      address=temp.group()
      print (address)
  
      #remove address from paragraph string obj
      paragraph = paragraph.replace(address,"")
  
      #retrieve phone number 
      parser= CommonRegex(paragraph)
      phone_num=parser.phones[:1]
      print("phone number: ",str(phone_num)[2:-2])
  
      #remove phone num from paragraph string obj
      paragraph = paragraph.replace(str(phone_num)[2:-2],"")
      
  
      ssn_or_tax_num=paragraph.split(' ')[0]
      temp_num=paragraph.split(' ')[-1]
  
      print ('\n',ssn_or_tax_num,": ", temp_num)
      print ("\n---------------------------------------------\n")

#address= 


    if name:
      data['Name'].append(name)
    else:
      data['Name'].append("n/a")
    if address:
      data['Address'].append(address)
    else:
      data['Address'].append("n/a")
    if phone_num:
      data['Phone Number'].append(str(phone_num)[2:-2])
    else:
      data['Phone Number'].append("n/a")
print(data)
table = pd.DataFrame(data)
#table = pd.DataFrame.from_dict(data)

table.index+= 1
print(table)

table.to_csv('debtors.csv',sep=',',encoding='utf-8')
"""
parser= CommonRegex()
print (parser.addresses(paragraph))
"""
   
    




    
  


#logout 
url="https://qa-login.uscourts.gov/services/cso-logout"
authHeaders={'Content-type': 'application/json',
'Accept': 'application/json'}
authBody={
  "nextGenCSO": myToken,
}


logoutResponse = requests.post(url,json=authBody,headers=authHeaders)

print ("Logout response",logoutResponse.json())

