import requests
import os 
import json 
import mechanicalsoup
import warnings
import pandas
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
  'Name/Business':[],
  'Address':[],
  'Phone Number':[],
  'SSN':[],
  'Bankruptcy Chapter': [],
  'Date Filed' : [],
  'Case Id' : []
}

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

    name= br.get_current_page().find("p",id="3").b.text
    print(name)
    paragraph = br.get_current_page().find("p",id="3").text.replace(name,"")
    print (paragraph)

    """
    parser= CommonRegex()
    print (parser.addresses(paragraph))
    """
    street_address_validate_pattern = r"(?:((?:\d[\d ]+)?[A-Za-z][A-Za-z ]+)[\s,]*([A-Za-z#0-9][A-Za-z#0-9 ]+)?[\s,]*)?(?:([A-Za-z][A-Za-z ]+)[\s,]+)?((?=AL|AK|AS|AZ|AR|CA|CO|CT|DE|DC|FM|FL|GA|GU|HI|ID|IL|IN|IA|KS|KY|LA‌​|ME|MH|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|MP|OH|OK|OR|PW|PA|PR|RI|SC|SD‌​|TN|TX|UT|VT|VI|VA|WA|WV|WI|WY)[A-Z]{2})(?:[,\s]+(\d{5}(?:-\d{4})?))?"
    address=re.findall(street_address_validate_pattern, paragraph) 

    print (address.group())

    print ("\n---------------------------------------------\n")

    #address= 



    
  


#logout 
url="https://qa-login.uscourts.gov/services/cso-logout"
authHeaders={'Content-type': 'application/json',
'Accept': 'application/json'}
authBody={
  "nextGenCSO": myToken,
}


logoutResponse = requests.post(url,json=authBody,headers=authHeaders)

print ("Logout response",logoutResponse.json())

