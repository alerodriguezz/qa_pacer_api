import requests
import os 
import json 
import mechanicalsoup
import wget

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

print("\nPrinting nested dictionary as a key-value pair","\n")

br= mechanicalsoup.StatefulBrowser()
login_link="https://qa-login.uscourts.gov/csologin/login.jsf"

br.open(login_link)

br.get_current_page()
br.select_form('form[id="loginForm"]')
br.get_current_form()

br["loginForm:loginName"]= my_login
br["loginForm:password"]= my_pass
save_button = br.get_current_page().find('button', id='loginForm:fbtnLogin')
br.submit_selected(btnName=save_button)
br.launch_browser()


for i in obj['content']:
  if "caseLink" in i.keys():
    print("Court ID:", i['courtId'])
    print("Court Title :", i['caseTitle'])
    link = i['caseLink'].replace("iqquerymenu","qryParties")
    print("Link:", link,"\n")

  


#logout 
url="https://qa-login.uscourts.gov/services/cso-logout"
authHeaders={'Content-type': 'application/json',
'Accept': 'application/json'}
authBody={
  "nextGenCSO": myToken,
}


logoutResponse = requests.post(url,json=authBody,headers=authHeaders)

print ("Logout response",logoutResponse.json())

