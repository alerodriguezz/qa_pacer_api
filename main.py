import requests
import os 
import json 
import mechanize
import ssl

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

for i in obj['content']:
  if "caseLink" in i.keys():
    print("Court ID:", i['courtId'])
    print("Court Title :", i['caseTitle'])
    link = i['caseLink'].replace("iqquerymenu","qryParties")
    print("Link:", link,"\n")




  
    ssl._create_default_https_context = ssl._create_unverified_context
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    browser.set_handle_refresh(False)
    browser.addheaders = [('user-agent', '   Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3'),
('accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')]
    browser.open(link)
    for f in browser.forms():
        print (f.name, "\n")
    #browser.select_form(nr = 0)
    #browser.form['username'] = my_login
    #browser.form['password'] = my_pass
    #browser.submit()
    
    print (browser.response().read())
  
#logout 
url="https://qa-login.uscourts.gov/services/cso-logout"
authHeaders={'Content-type': 'application/json',
'Accept': 'application/json'}
authBody={
  "nextGenCSO": myToken,
}


logoutResponse = requests.post(url,json=authBody,headers=authHeaders)

print ("Logout response",logoutResponse.json())

